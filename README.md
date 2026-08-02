# 🚗 ME7 CDKAT / CDSLS DISABLER

**Disable Catalyst (CDKAT) and Secondary Air Injection (CDSLS) DTC switches in Bosch ME7 / ME7.5 ECU firmware.**

A lightweight command-line utility that automatically locates and safely disables **CDKAT** and **CDSLS** diagnostic switches using original Bosch ME7 code patterns.

The original BIN file is **never overwritten**, making the modification process safe and straightforward.

---

# ✨ Features

* ✅ Automatic **CDKAT** detection
* ✅ Automatic **CDSLS** detection
* ✅ Supports Bosch **ME7 / ME7.5** ECUs
* ✅ Automatic ECU information detection
* ✅ Safe pattern-based switch identification
* ✅ Scan-only mode
* ✅ Automatic checksum correction using **ME7Sum**
* ✅ Original BIN file is never overwritten
* ✅ Detailed operation log
* ✅ Windows executable included

---

# 📦 Usage

## Disable CDKAT & CDSLS

```text
Kat_Sai_OFF.exe dump.bin
```

## Scan only

```text
Kat_Sai_OFF.exe dump.bin --SCANONLY
```

or

```text
Kat_Sai_OFF.exe dump.bin -s
```

---

# 📁 Output

The original BIN file is **never modified**.

The program creates:

```text
dump_CDKAT_CDSLS_OFF.bin
```

If **ME7Sum** is available in the same directory, an additional checksum-corrected BIN file is automatically generated.

---

# ⚙️ Requirements

* Windows
* Bosch **ME7 / ME7.5** firmware
* `me7sum.exe` *(optional but highly recommended)*

To enable automatic checksum correction, simply place **me7sum.exe** in the same directory as **Kat_Sai_OFF.exe**.

---

# ⚠️ Important

**Never flash a modified BIN file with an invalid checksum.**

If checksum correction fails or **ME7Sum** is missing, the generated BIN **must not be flashed**.

Always verify the modified firmware before programming the ECU.

---

# 🖥️ Example

```text
========================================================================
              ME7.5 CDKAT / CDSLS DISABLER
        Catalyst & Secondary Air Injection DTC Switches
========================================================================

[1/6] Reading ECU information...

[2/6] Searching CDKAT...

[3/6] Searching CDSLS...

[4/6] Applying changes...

[5/6] Correcting checksum...

[6/6] Finished
```

---

# 🔬 Verification Notice

One of the biggest challenges during the development of this tool was correctly identifying the **CDKAT** and **CDSLS** switch addresses across the many different Bosch **ME7 / ME7.5** firmware variants.

Although the tool has been successfully tested on multiple firmware files, I kindly ask experienced Bosch ME7 users to **verify every modified BIN file** after modification using trusted software such as **WinOLS**, **ME7Check**, or other ECU analysis tools.

If you find a firmware where the tool identifies an incorrect address or behaves unexpectedly, please open a **GitHub Issue** and include as much information as possible, for example:

* ECU part number
* Bosch hardware number
* Bosch software number
* Original BIN file *(if possible)*
* Program output / log
* Any additional observations

Every report helps improve compatibility with more Bosch **ME7 / ME7.5** firmware versions.

---

# 🤝 Contributing

Bug reports, feature requests and Pull Requests are always welcome.

If you have tested the software on firmware that is not yet known to be compatible, your feedback is highly appreciated and helps improve the project for everyone.

Whether you find a bug, discover a new supported ECU, or have an idea for improving the software, feel free to contribute.

---

# 🌍 Open Source

This project is completely **Open Source**.

Everyone is welcome to:

* ⭐ Star the repository
* 🐞 Report bugs
* 💡 Suggest new features
* 🔧 Submit Pull Requests
* ❤️ Help improve the project

Every contribution is greatly appreciated.

---

# ⚖️ Disclaimer

This software is provided **"AS IS"**, without warranty of any kind.

The author assumes **no responsibility** for any damage to the ECU, vehicle, or any other consequences resulting from the use or misuse of this software.

**Use this software entirely at your own risk.**

---

# ☕ Support

If you find this project useful, please consider giving it a ⭐ on GitHub.

It helps the project reach more Bosch ME7 enthusiasts and supports future development.

Thank you for your support and happy tuning! 🚗💨
