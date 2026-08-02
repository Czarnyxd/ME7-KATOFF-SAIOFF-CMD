# 🚗 ME7 CDKAT / CDSLS DISABLER

**Disable Catalyst (CDKAT) and Secondary Air Injection (CDSLS) DTC switches in Bosch ME7 / ME7.5 ECU firmware.**

This utility automatically locates and disables the **CDKAT** (Catalyst Diagnostic) and **CDSLS** (Secondary Air Injection Diagnostic) switches using original Bosch ME7 code patterns. The original firmware is never overwritten, making the modification process both safe and simple.

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

The program creates a new file:

```text
dump_CDKAT_CDSLS_OFF.bin
```

If **ME7Sum** is located in the same directory, the checksum will be corrected automatically and an additional checksum-corrected BIN file will be generated.

---

# ⚙️ Requirements

* Windows
* Bosch **ME7 / ME7.5** firmware
* `me7sum.exe` *(optional but highly recommended)*

To enable automatic checksum correction, simply place **me7sum.exe** in the same directory as **Kat_Sai_OFF.exe**.

---

# ⚠️ Important

**Never flash a modified BIN file with an invalid checksum.**

If checksum correction fails or **ME7Sum** is not found, **do not flash the generated BIN file**.

Always verify the modified firmware before programming the ECU.

---

# 🔬 Verification Notice

One of the biggest challenges during development was reliably identifying the **CDKAT** and **CDSLS** switch addresses across the many different Bosch **ME7 / ME7.5** firmware variants.

Although the tool has been successfully tested on multiple firmware files and works as intended, I kindly ask experienced Bosch ME7 users to **verify every modified BIN file** using trusted tools such as **WinOLS**, **ME7Check**, or other ECU analysis software.

If you find a firmware where the tool identifies an incorrect switch address or behaves unexpectedly, please create a **GitHub Issue** and include as much information as possible, such as:

* ECU part number
* Hardware number
* Software number
* Original BIN file
* Program log
* Any additional observations

Every bug report and compatibility test helps improve support for additional Bosch ME7 / ME7.5 firmware versions.

---

# 🌍 Open Source

This project is fully **Open Source**.

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

Thank you for your support, and happy tuning!
