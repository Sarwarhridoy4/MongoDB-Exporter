# Key Changes

## Version 2.4.0

1. UI and Theme
   - Added elegant neumorphism QSS styling.
   - Added `Theme` menu with `System` (default), `Light`, and `Dark`.

2. Backup Options
   - Added `Compress Backup (.zip)` option.
   - Added `Encrypt Backup` option with password input.
   - Added `Upload to Google Drive` option with credential path and optional folder ID.
   - Enforced minimum password length (8 characters) for encryption.

3. Security and Encryption
   - Implemented AES-GCM backup encryption.
   - Added PBKDF2 key derivation for password-based encryption.
   - Export scripts no longer store encryption passwords.

4. Decryption Support
   - Added `File -> Decrypt Backup` action.
   - Added in-app decryption flow for `.enc` backups.
   - Added validation for invalid password/corrupted backup.
   - Added cleanup for partial output on decryption failure.

5. Progress and UX
   - Improved processing progress text to cover compression/encryption stages.
   - Kept export/import script flow aligned with new backup options.

6. Dependencies
   - Added `cryptography` to `requirements.txt`.
   - Added Google Drive API dependencies (`google-api-python-client`, `google-auth`, `google-auth-httplib2`).

## Version 2.3.0

1. Add About Page
2. Add Developer Info

## Version 2.2.2

1. Add new file extension `.mdbexport`
2. Make code modular
3. Add Check For Update option

## Version 2.2.1

1. Add new file extension `.mdbexport`
2. Make code modular

## Version 2.2.0

1. Export / Import Script added
   - Add option to create and load JSON script.
   - Fill input once, create script, and reuse later.
   - Loaded scripts can start export immediately if confirmed.

## Version 2.1.0

1. Add Dated Folder
   - Create a dated folder inside selected output directory.

2. Add Zipping Feature
   - Create zip after successful export for portability.

## Version 2.0.2

1. Change Font
   - Changed font from Arial to Roboto.

2. Watermark Logo
   - Added background watermark logo.

## Version 2.0.1

1. Confirmation Dialog
   - Added export confirmation dialog.

2. Abort Button
   - Added abort button to stop export process.

3. Disable/Enable Buttons
   - Export and abort buttons are enabled/disabled based on export state.

4. Progress and Stability
   - Fixed real-time progress percentage.
   - Fixed crashes during large collection exports.
