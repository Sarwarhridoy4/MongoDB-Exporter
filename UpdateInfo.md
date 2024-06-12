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

   - Change font Arial to Roboto

2. **WaterMark Logo**:

   - Add Background Image Watermark Logo

## Version 2.1.0

1. **Add Dated Folder**:

   - Add a Dated Folder inside output Folder

2. **Add Zipping Feature**:

   - Add Zipping after successful export. It will help to reduce size if you needs to upload or sen to anyone.

## Version 2.2.0

1. **Export / Import Script added**:

   - Add option to create and load json script.
   - Fill info once ==> click file menu ==> click create script ==> Give name ==> Save
   - Create script once and load it to start export automatically.
   - It will save backup file to your selected location every time.
   - Once You loaded a file it will ask you to start export automatically.
   - If you select yes it will start and save backup and zipped folder on your desire location.
   - If no it does not start immediately but leave input populated with your script information.

## Version 2.2.1

1. Add new file extension .mdbexport
2. Make code modular

## Version 2.2.2

1. Add new file extension .mdbexport
2. Make code modular
3. Add Check For Update Option

## Version 2.3.0

1. Add About Page
2. Add Developer Info
