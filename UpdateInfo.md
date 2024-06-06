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
