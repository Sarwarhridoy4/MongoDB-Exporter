# MongoDB Exporter GUI

## Overview

MongoDB Exporter GUI is a Python-based application with a simple graphical user interface (GUI) for exporting collections from a MongoDB database to JSON files. This tool allows users to connect to their MongoDB database, select the database they want to export, and specify the output directory where the JSON files will be saved. The application also provides real-time progress updates, including the name of the current collection being exported and the percentage of the export process completed.

## Features

- **Graphical User Interface**: Easy-to-use interface built with `PyQt5`.
- **MongoDB Connection**: Connect to any MongoDB database using a URI.
- **Database Selection**: Specify the database from which you want to export collections.
- **Output Directory**: Choose the directory where JSON files will be saved.
- **Export Non-Empty Collections**: Only exports collections that contain documents.
- **Real-Time Progress Updates**: Displays the current collection being exported and the completion percentage.
- **Error Handling**: Provides error messages if the export process fails.
- **Logo and Favicon**: Displays a logo in the application and a favicon in the title bar and taskbar.

## Prerequisites

- Python 3.x
- `pymongo` library
- `PyQt5` library
- `requests` library

## Installation (From Source)

1. Clone the repository or download the script.
2. Install the required libraries if not already installed:

```bash
pip install -r requirements.txt
```

---

# 🆕 Changelog

### ✅ Version 2.3.0

- Add **About Page**
- Add **Developer Info**

<details>
<summary>Previous Versions</summary>

### Version 2.2.2

- Add new file extension `.mdbexport`
- Make code modular
- Add **Check For Update** option

### Version 2.2.1

- Introduced `.mdbexport` file format
- Refactored into a modular codebase

### Version 2.2.0

- Add **Export/Import Script**

  - Create, save, and reuse JSON export scripts
  - Auto-load and populate fields on script load
  - Backup and zip upon export

### Version 2.1.0

- **Auto-dated Output Folder**
- **Zipping** after export for portability

### Version 2.0.2

- Switched default font to **Roboto**
- Added **background watermark logo**

### Version 2.0.1

- Confirmation dialog before export
- Abort button with progress tracking
- Fixed UI freeze during large exports

</details>

---

# 📥 Download

Welcome to MongoDB Exporter! Click the buttons below to download the latest version for your platform:

### 🔹 Windows

👉 [Download for Windows (.exe)](https://github.com/Sarwarhridoy4/MongoDB-Exporter/releases/latest/download/MongoDBExporter-Setup.exe)

### 🔹 Linux (Debian/Ubuntu)

👉 [Download .deb Installer](https://github.com/Sarwarhridoy4/MongoDB-Exporter/releases/download/2.3.0/mongodbexporter_2.3.0_amd64.deb)

### 🔹 Linux (Universal AppImage)

👉 [Download AppImage](https://github.com/Sarwarhridoy4/MongoDB-Exporter/releases/download/2.3.0/MongoDB_Exporter-x86_64.AppImage)

---

## 💬 Feedback & Issues

If you encounter bugs or have suggestions, feel free to [create an issue](https://github.com/Sarwarhridoy4/MongoDB-Exporter/issues).

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

```

```
