#!/usr/bin/env python3
"""
ME7.5 CDKAT / CDSLS DISABLER

Default:
    python3 katoff.py test.bin

Scan only:
    python3 katoff.py test.bin --SCANONLY
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

VERSION = "1.3.0"
LINE = "=" * 72
SUBLINE = "-" * 72
VALID_BIN_SIZES = {512 * 1024, 1024 * 1024, 2 * 1024 * 1024}


@dataclass(frozen=True)
class Signature:
    name: str
    pattern: tuple[int | None, ...]
    marker_index: int = 6
    dpp_offset_from_marker: int = -4

    @property
    def length(self) -> int:
        return len(self.pattern)


@dataclass(frozen=True)
class Match:
    name: str
    pattern_start: int
    marker_address: int
    dpp_value: int
    map_operand: int
    switch_address: int
    current_value: int
    valid: bool
    reason: str


@dataclass(frozen=True)
class EcuInfo:
    vag_number: str
    bosch_hw: str
    bosch_sw: str
    engine: str
    bootrom: str
    epk: str


SIGNATURES = (
    Signature(
        "CDKAT",
        (
            0xD7, 0x40, None, None,
            0xC2, 0xF4, None, None,
            0x68, 0x41, 0x2D, 0x05,
            0xE6, 0xF4, 0x00, 0x01,
            0x74, 0xF4,
        ),
    ),
    Signature(
        "CDSLS",
        (
            0xD7, 0x40, None, None,
            0xC2, 0xF4, None, None,
            0x68, 0x41, 0x2D, 0x05,
            0xE6, 0xF4, 0x00, 0x04,
            0x74, 0xF4,
        ),
    ),
)


def u16le(data: bytes | bytearray, offset: int) -> int:
    return data[offset] | (data[offset + 1] << 8)


def pattern_matches(data: bytes, start: int, pattern: tuple[int | None, ...]) -> bool:
    for index, expected in enumerate(pattern):
        if expected is not None and data[start + index] != expected:
            return False
    return True


def calculate_me7_address(dpp_value: int, map_operand: int) -> int:
    return (dpp_value * 0x4000) - 0x800000 + (map_operand & 0x3FFF)


def find_first_match(data: bytes, signature: Signature) -> Match | None:
    last_start = len(data) - signature.length
    if last_start < 0:
        return None

    for start in range(last_start + 1):
        if not pattern_matches(data, start, signature.pattern):
            continue

        marker = start + signature.marker_index
        dpp_position = marker + signature.dpp_offset_from_marker
        dpp_value = u16le(data, dpp_position)
        map_operand = u16le(data, marker)
        switch_address = calculate_me7_address(dpp_value, map_operand)

        if switch_address < 0 or switch_address >= len(data):
            return Match(
                signature.name, start, marker, dpp_value, map_operand,
                switch_address, -1, False,
                "calculated address is outside the BIN",
            )

        current_value = data[switch_address]
        if current_value not in (0x00, 0x01):
            return Match(
                signature.name, start, marker, dpp_value, map_operand,
                switch_address, current_value, False,
                f"unexpected switch value 0x{current_value:02X}",
            )

        return Match(
            signature.name, start, marker, dpp_value, map_operand,
            switch_address, current_value, True, "validated",
        )

    return None


def clean_ascii(value: bytes) -> str:
    return value.decode("latin-1", errors="ignore").replace("\x00", "").strip()


def first_regex(data: bytes, patterns: tuple[bytes, ...]) -> str:
    for pattern in patterns:
        match = re.search(pattern, data)
        if match:
            return clean_ascii(match.group(0))
    return "Not found"


def extract_ecu_info(data: bytes) -> EcuInfo:
    vag_number = first_regex(
        data,
        (
            rb"06A9060[0-9A-Z]{3,5}",
            rb"8N09060[0-9A-Z]{3,5}",
            rb"8E09095[0-9A-Z]{3,5}",
            rb"4B09060[0-9A-Z]{3,5}",
            rb"8L09060[0-9A-Z]{3,5}",
        ),
    )

    bosch_hw = first_regex(data, (rb"0261[0-9]{6}",))
    bosch_sw = first_regex(data, (rb"1037[0-9]{6}",))
    engine = first_regex(
        data,
        (
            rb"[12]\.[0-9]L R[3456]/[0-9A-Z]{2,8}",
            rb"[12]\.[0-9]T[^\x00\r\n]{0,12}",
        ),
    )
    bootrom = first_regex(data, (rb"0[0-9]\.[0-9]{2}",))
    epk = first_regex(data, (rb"[0-9]{2}/[0-9]/ME7\.[0-9]/[^\x00\r\n]{5,80}",))

    return EcuInfo(vag_number, bosch_hw, bosch_sw, engine, bootrom, epk)


def collect_bin_files(path: Path, recursive: bool) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix.lower() == ".bin" else []

    if not path.is_dir():
        return []

    iterator: Iterable[Path] = path.rglob("*") if recursive else path.iterdir()
    return sorted(
        item for item in iterator
        if item.is_file()
        and item.suffix.lower() == ".bin"
        and not item.name.upper().endswith("_CDKAT_CDSLS_OFF.BIN")
        and not item.name.upper().endswith("_CDKAT_CDSLS_OFF_CSOK.BIN")
    )


def find_me7sum(script_dir: Path) -> Path | None:
    candidates = (
        script_dir / "me7sum.exe",
        Path.cwd() / "me7sum.exe",
        script_dir / "tools" / "me7sum.exe",
    )
    return next((path for path in candidates if path.is_file()), None)


def run_me7sum(me7sum: Path, input_bin: Path, output_bin: Path) -> tuple[bool, str]:
    command = [str(me7sum), str(input_bin), str(output_bin)]

    if sys.platform != "win32":
        wine = shutil.which("wine")
        if wine is None:
            return False, "Wine was not found"
        command.insert(0, wine)

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=120,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, str(exc)

    combined = "\n".join(
        part for part in (result.stdout, result.stderr) if part
    ).strip()

    if result.returncode == 0 and output_bin.is_file():
        counts = re.findall(r"\b([0-9]+)/([0-9]+)\b", combined)
        if counts:
            current, total = counts[-1]
            return True, f"OK ({current}/{total})"
        return True, "OK"

    detail = combined.splitlines()[-1] if combined else f"exit code {result.returncode}"
    return False, detail


def print_header() -> None:
    print(LINE)
    print("              ME7.5 CDKAT / CDSLS DISABLER")
    print("        Catalyst & Secondary Air Injection DTC Switches")
    print(LINE)
    print(f"Version         : {VERSION}")
    print()


def print_match(step: int, match: Match | None, name: str) -> None:
    print(f"[{step}/6] Searching {name}...")
    print(SUBLINE)

    if match is None:
        print("Pattern         : NOT FOUND")
        print("Status          : ERROR")
        print()
        return

    print(f"Pattern start   : 0x{match.pattern_start:06X}")
    print(f"MM marker       : 0x{match.marker_address:06X}")
    print(f"DPP value       : 0x{match.dpp_value:04X}")
    print(f"Map operand     : 0x{match.map_operand:04X}")
    print(
        f"Address         : 0x{match.switch_address:06X}"
        if match.switch_address >= 0 else
        "Address         : INVALID"
    )
    print(
        f"Current value   : 0x{match.current_value:02X}"
        if match.current_value >= 0 else
        "Current value   : --"
    )

    if match.valid:
        state = "Already disabled" if match.current_value == 0 else "Ready to disable"
        print(f"Status          : FOUND - {state}")
    else:
        print(f"Status          : REJECTED - {match.reason}")
    print()


def process_file(source: Path, scan_only: bool, force_size: bool) -> bool:
    started = time.perf_counter()
    print_header()
    print(f"Input file      : {source}")
    print(f"Mode            : {'SCAN ONLY' if scan_only else 'DISABLE AND SAVE'}")
    print()

    try:
        data = source.read_bytes()
    except OSError as exc:
        print(f"[ERROR] Cannot read BIN: {exc}")
        return False

    info = extract_ecu_info(data)

    print("[1/6] Reading ECU information...")
    print(SUBLINE)
    print(f"ECU             : {info.vag_number}")
    print(f"Bosch HW        : {info.bosch_hw}")
    print(f"Bosch SW        : {info.bosch_sw}")
    print(f"Engine          : {info.engine}")
    print(f"Bootrom         : {info.bootrom}")
    print(f"File size       : {len(data)} bytes")
    print(f"Status          : {'Supported size' if len(data) in VALID_BIN_SIZES else 'Non-standard size'}")
    print()

    if len(data) not in VALID_BIN_SIZES and not force_size:
        print("[ERROR] Unsupported or non-standard BIN size.")
        return False

    cdkat = find_first_match(data, SIGNATURES[0])
    cdsls = find_first_match(data, SIGNATURES[1])

    print_match(2, cdkat, "CDKAT")
    print_match(3, cdsls, "CDSLS")

    if (
        cdkat is None or cdsls is None
        or not cdkat.valid or not cdsls.valid
        or cdkat.switch_address == cdsls.switch_address
    ):
        print("[4/6] Applying changes...")
        print(SUBLINE)
        print("Status          : ABORTED")
        print("Reason          : Both switches were not resolved safely.")
        return False

    if scan_only:
        print("[4/6] Applying changes...")
        print(SUBLINE)
        print("Status          : SKIPPED - SCAN ONLY")
        print()
        print("[5/6] Correcting checksum...")
        print(SUBLINE)
        print("Status          : SKIPPED - SCAN ONLY")
        print()
        print("[6/6] Finished")
        print(SUBLINE)
        print(f"CDKAT           : 0x{cdkat.switch_address:06X} = 0x{cdkat.current_value:02X}")
        print(f"CDSLS           : 0x{cdsls.switch_address:06X} = 0x{cdsls.current_value:02X}")
        print("Output file     : Not created")
        print(f"Elapsed time    : {time.perf_counter() - started:.2f} sec")
        return True

    if cdkat.current_value == 0 and cdsls.current_value == 0:
        print("[4/6] Applying changes...")
        print(SUBLINE)
        print("CDKAT           : Already disabled")
        print("CDSLS           : Already disabled")
        print("Status          : Nothing to modify")
        print()
        print("[5/6] Correcting checksum...")
        print(SUBLINE)
        print("Status          : SKIPPED")
        print()
        print("[6/6] Finished")
        print(SUBLINE)
        print("Output file     : Not created")
        print(f"Elapsed time    : {time.perf_counter() - started:.2f} sec")
        return True

    modified = bytearray(data)
    changes = 0

    print("[4/6] Applying changes...")
    print(SUBLINE)
    for match in (cdkat, cdsls):
        if modified[match.switch_address] == 0x01:
            modified[match.switch_address] = 0x00
            changes += 1
            print(f"{match.name:<16}: 0x01 -> 0x00")
        else:
            print(f"{match.name:<16}: Already disabled")
    print(f"Modified bytes  : {changes}")
    print("Status          : OK")
    print()

    modified_path = source.with_name(f"{source.stem}_CDKAT_CDSLS_OFF.bin")
    try:
        modified_path.write_bytes(modified)
    except OSError as exc:
        print(f"[ERROR] Cannot save modified BIN: {exc}")
        return False

    print(LINE)
    print(" WARNING")
    print(LINE)
    print(" The checksum is currently INVALID.")
    print()
    print(" Do NOT flash this file until the checksum has been corrected.")
    print()

    print("[5/6] Correcting checksum...")
    print(SUBLINE)

    me7sum = find_me7sum(Path(__file__).resolve().parent)
    checksum_ok = False
    final_output = modified_path

    if me7sum is None:
        print("ME7Sum          : NOT FOUND")
        print("Status          : Checksum was NOT corrected")
        print("WARNING         : Do NOT flash the modified BIN")
    else:
        csok_path = modified_path.with_name(f"{modified_path.stem}_CSOK.bin")
        checksum_ok, message = run_me7sum(me7sum, modified_path, csok_path)
        print(f"ME7Sum          : {message}")

        if checksum_ok:
            final_output = csok_path
            print("Status          : Checksum corrected")
        else:
            print("Status          : Checksum correction FAILED")
            print("WARNING         : Do NOT flash the modified BIN")
    print()

    print("[6/6] Finished")
    print(SUBLINE)
    print(f"ECU             : {info.vag_number}")
    print(f"CDKAT           : Disabled at 0x{cdkat.switch_address:06X}")
    print(f"CDSLS           : Disabled at 0x{cdsls.switch_address:06X}")
    print(f"Modified bytes  : {changes}")
    print(f"Checksum        : {'OK' if checksum_ok else 'NOT CORRECTED'}")
    print(f"Output file     : {final_output}")
    print(f"Elapsed time    : {time.perf_counter() - started:.2f} sec")
    print()

    if checksum_ok:
        print("Completed successfully.")
    else:
        print("Modification completed, but checksum correction is required.")

    return True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Disable CDKAT and CDSLS in Bosch ME7/ME7.5 BIN files."
    )
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=Path("."),
        help="BIN file or directory; default: current directory",
    )
    parser.add_argument(
        "--SCANONLY",
        "--scanonly",
        "--scan",
        "-s",
        dest="scan_only",
        action="store_true",
        help="display addresses without modifying the BIN",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="process subdirectories",
    )
    parser.add_argument(
        "--force-size",
        action="store_true",
        help="allow a non-standard BIN size",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    files = collect_bin_files(args.path, args.recursive)

    if not files:
        print("[ERROR] No .bin files found.")
        return 2

    successful = 0
    for index, source in enumerate(files, start=1):
        if len(files) > 1:
            print()
            print(LINE)
            print(f" FILE {index}/{len(files)}")
            print(LINE)

        if process_file(source, args.scan_only, args.force_size):
            successful += 1

    if len(files) > 1:
        print()
        print(LINE)
        print(" BATCH SUMMARY")
        print(LINE)
        print(f"Successful      : {successful}/{len(files)}")
        print(f"Failed          : {len(files) - successful}/{len(files)}")

    return 0 if successful == len(files) else 1


if __name__ == "__main__":
    raise SystemExit(main())
