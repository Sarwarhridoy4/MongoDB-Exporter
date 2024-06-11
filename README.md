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

## Installation

1. Clone the repository or download the script.
2. Install the required libraries if not already installed:

```sh
pip install pymongo pyqt5
```

# Key Changes:

## Version 2.0.1

1. **Confirmation Dialog**:

   - A confirmation dialog (`QMessageBox.question`) is shown when the export button is clicked, asking the user to confirm if they want to start the export process.

2. **Abort Button**:

   - An "Abort" button has been added to the interface. This button is styled with a red background and white text.
   - When clicked, it sets a flag to abort the export process.

3. **Disable/Enable Buttons**:

   - The export and abort buttons are enabled and disabled appropriately during the export process.
   - The export button is disabled while the export is in progress.
   - The abort button is disabled when the export is not in progress or after the abort is triggered.

4. **Fix Real-time Percentage**:
   - The real-time percentage progress display has been fixed to show accurate progress during the export process.
   - Fix the Crashing app while exporting large collections

## Version 2.0.2

1. **Change Font**:

   - Change font from Arial to Roboto

2. **WaterMark Logo**:

   - Add Background Image Watermark Logo

## Version 2.1.0

1. **Add Dated Folder**:

   - Add a Dated Folder inside the Output Folder

2. **Add Zipping Feature**:

   - Add Zipping after successful export. It will help reduce the size if you need to upload or send it to anyone.

## Version 2.2.0

1. **Export / Import Script added**:

   - Add an option to create and load JSON script.
   - Fill info once ==> click file menu ==> click create script ==> Give name ==> Save
   - Create a script once and load it to start exporting automatically.
   - It will save a backup file to your selected location every time.
   - Once You load a file it will ask you to start export automatically.
   - If you select yes it will start and save the backup and zipped folder on your desired location.
   - If no it does not start immediately but leave input populated with your script information.

## Version 2.2.1

1. Add new file extension .mdbexport
2. Make code modular

## Version 2.2.2

1. Add new file extension .mdbexport
2. Make code modular
3. Add Check For Update Option

# Get Installer(Windows)

Welcome to MongoDB Exporter! Click the button below to download the latest version.

<a href="https://github.com/Sarwarhridoy4/MongoDB-Exporter/releases/download/2.2.2/MogoDBExporter.exe" download>
    <img src="https://img.shields.io/badge/Download-Now-brightgreen" alt="Download Now">
</a>
