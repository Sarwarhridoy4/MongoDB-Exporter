# MongoDB Exporter GUI

## Overview

MongoDB Exporter GUI is a Python-based application that provides a simple graphical user interface (GUI) for exporting collections from a MongoDB database to JSON files. This tool allows users to connect to their MongoDB database, select the database they want to export, and specify the output directory where the JSON files will be saved. The application also provides real-time progress updates, including the name of the current collection being exported and the percentage of the export process completed.

## Features

- **Graphical User Interface**: Easy-to-use interface built with `tkinter`.
- **MongoDB Connection**: Connect to any MongoDB database using a URI.
- **Database Selection**: Specify the database you want to export collections from.
- **Output Directory**: Choose the directory where JSON files will be saved.
- **Export Non-Empty Collections**: Only exports collections that contain documents.
- **Real-Time Progress Updates**: Displays the current collection being exported and the percentage of completion.
- **Error Handling**: Provides error messages if the export process fails.

## Prerequisites

- Python 3.x
- `pymongo` library
- `tkinter` library (included with standard Python distribution)

## Installation

1. Clone the repository or download the script.
2. Install the required `pymongo` library if not already installed:

```sh
pip install pymongo