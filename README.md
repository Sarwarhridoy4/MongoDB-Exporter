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

# Get Installer(Windows)

Welcome to MongoDB Exporter! Click the button below to download the latest version.

<a href="https://drive.google.com/file/d/1Qyvni4RL_aOEpJWmFfE8k5acJO-O8rNP/view?usp=sharing" download>
    <img src="https://img.shields.io/badge/Download-Now-brightgreen" alt="Download Now">
</a>
