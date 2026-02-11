import json
import os

from PySide6.QtWidgets import (
    QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QWidget, QFileDialog, QMessageBox, QProgressBar, QGraphicsOpacityEffect, QDialog, QApplication,
    QCheckBox, QInputDialog
)
from PySide6.QtGui import QAction, QActionGroup, QFont, QPixmap, QIcon
from PySide6.QtCore import Qt
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from export_thread import ExportThread
from updater import UpdateThread
from utils import resource_path


class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About MongoDB Exporter")
        self.setFixedSize(400, 500)

        layout = QVBoxLayout()

        # Set window icon (favicon)
        self.setWindowIcon(QIcon(resource_path("./asset/favicon.png")))  # Provide the path to your favicon file

        # Logo
        logo_label = QLabel(self)
        pixmap = QPixmap(resource_path("./asset/mongo_icon.png"))
        logo_label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setFixedSize(72, 72)
        logo_label.setAlignment(Qt.AlignCenter)

        # Application name and version
        app_name_label = QLabel("MongoDB Exporter", self)
        app_name_label.setFont(QFont('Roboto', 18, QFont.Bold))
        app_name_label.setAlignment(Qt.AlignCenter)

        version_label = QLabel("Version 2.3.0", self)
        version_label.setFont(QFont('Roboto', 12))
        version_label.setAlignment(Qt.AlignCenter)

        # Developer image
        dev_image_label = QLabel(self)
        dev_image_pixmap = QPixmap(resource_path("./asset/developer_image.png"))  # Provide the path to your developer image
        dev_image_label.setPixmap(dev_image_pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        dev_image_label.setAlignment(Qt.AlignCenter)
        dev_image_label.mousePressEvent = self.open_developer_website  # Connect the click event

        # Author information
        author_label = QLabel("Sarwar Hossain Hridoy", self)
        author_label.setFont(QFont('Roboto', 12))
        author_label.setAlignment(Qt.AlignCenter)

        # Email
        email_label = QLabel("Email: sarwarhridoy4@gmail.com", self)
        email_label.setFont(QFont('Roboto', 10))
        email_label.setAlignment(Qt.AlignCenter)

        # GitHub link with logo
        github_label = QLabel(self)
        github_pixmap = QPixmap(resource_path("./asset/github_icon.png"))  # Provide the path to your GitHub logo image
        github_label.setPixmap(github_pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        github_label.setAlignment(Qt.AlignCenter)
        github_label.mousePressEvent = self.open_github_link  # Connect the click event

        layout.addWidget(logo_label)
        layout.addWidget(app_name_label)
        layout.addWidget(version_label)
        layout.addWidget(dev_image_label)
        layout.addWidget(author_label)
        layout.addWidget(email_label)
        layout.addWidget(github_label)

        self.setLayout(layout)

    def open_developer_website(self, event):
        import webbrowser
        webbrowser.open("https://sarwar-hossain-hridoy.web.app/")

    def open_github_link(self, event):
        import webbrowser
        webbrowser.open("https://github.com/Sarwarhridoy4")


class MongoDBExporter(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MongoDB Exporter 2.3.0")
        self.setGeometry(100, 100, 600, 400)
        self.theme_mode = "system"

        # Set window icon (favicon)
        self.setWindowIcon(QIcon(resource_path("./asset/favicon.png")))  # Provide the path to your favicon file

        # Main layout
        main_layout = QVBoxLayout()

        # An image as a watermark
        watermark_image = QLabel(self)
        watermark_pixmap = QPixmap(resource_path('./asset/mongo_icon.png'))
        watermark_image.setPixmap(watermark_pixmap)
        watermark_image.setAttribute(Qt.WA_TranslucentBackground)
        watermark_image.adjustSize()

        # Apply opacity effect to the watermark image
        opacity_effect_image = QGraphicsOpacityEffect()
        opacity_effect_image.setOpacity(0.7)  # Set opacity level (0.0 to 1.0)
        watermark_image.setGraphicsEffect(opacity_effect_image)

        # Position the watermark image (bottom-right corner)
        watermark_image.move(self.width() - watermark_image.width() - 20, self.height() - watermark_image.height() - 20)

        # Title and logo layout
        title_layout = QHBoxLayout()
        self.logo_label = QLabel(self)
        pixmap = QPixmap(resource_path("./asset/mongo_icon.png"))  # Provide the path to your logo image
        self.logo_label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_label.setFixedSize(72, 72)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.title_label = QLabel("MongoDB Exporter", self)
        self.title_label.setFont(QFont('Roboto', 18, QFont.Bold))

        title_layout.addWidget(self.logo_label)
        title_layout.addWidget(self.title_label, alignment=Qt.AlignVCenter)
        main_layout.addLayout(title_layout)

        # URI
        uri_layout = QHBoxLayout()
        self.uri_label = QLabel("MongoDB URI:", self)
        self.uri_label.setFont(QFont('Roboto', 12))
        self.uri_input = QLineEdit(self)
        self.uri_input.setFont(QFont('Roboto', 12))
        uri_layout.addWidget(self.uri_label)
        uri_layout.addWidget(self.uri_input)
        main_layout.addLayout(uri_layout)

        # Database Name
        db_name_layout = QHBoxLayout()
        self.db_name_label = QLabel("Database Name:", self)
        self.db_name_label.setFont(QFont('Roboto', 12))
        self.db_name_input = QLineEdit(self)
        self.db_name_input.setFont(QFont('Roboto', 12))
        db_name_layout.addWidget(self.db_name_label)
        db_name_layout.addWidget(self.db_name_input)
        main_layout.addLayout(db_name_layout)

        # Output Directory
        output_dir_layout = QHBoxLayout()
        self.output_dir_label = QLabel("Output Directory:", self)
        self.output_dir_label.setFont(QFont('Roboto', 12))
        self.output_dir_input = QLineEdit(self)
        self.output_dir_input.setFont(QFont('Roboto', 12))
        self.browse_button = QPushButton("Browse", self)
        self.browse_button.setFont(QFont('Roboto', 12))
        self.browse_button.clicked.connect(self.browse_output_dir)
        output_dir_layout.addWidget(self.output_dir_label)
        output_dir_layout.addWidget(self.output_dir_input)
        output_dir_layout.addWidget(self.browse_button)
        main_layout.addLayout(output_dir_layout)

        # Backup options
        backup_options_layout = QHBoxLayout()
        self.compress_checkbox = QCheckBox("Compress Backup (.zip)", self)
        self.compress_checkbox.setChecked(True)
        self.encrypt_checkbox = QCheckBox("Encrypt Backup", self)
        self.encrypt_checkbox.toggled.connect(self.toggle_encryption_password)
        self.encrypt_password_input = QLineEdit(self)
        self.encrypt_password_input.setPlaceholderText("Encryption password")
        self.encrypt_password_input.setEchoMode(QLineEdit.Password)
        self.encrypt_password_input.setEnabled(False)
        backup_options_layout.addWidget(self.compress_checkbox)
        backup_options_layout.addWidget(self.encrypt_checkbox)
        backup_options_layout.addWidget(self.encrypt_password_input)
        main_layout.addLayout(backup_options_layout)

        # Cloud options
        cloud_options_layout = QHBoxLayout()
        self.upload_drive_checkbox = QCheckBox("Upload to Google Drive", self)
        self.upload_drive_checkbox.toggled.connect(self.toggle_drive_upload_options)
        self.drive_credentials_input = QLineEdit(self)
        self.drive_credentials_input.setPlaceholderText("Service account JSON credentials")
        self.drive_credentials_input.setMinimumWidth(340)
        self.drive_credentials_input.setEnabled(False)
        self.drive_credentials_browse_button = QPushButton("Credentials", self)
        self.drive_credentials_browse_button.setMinimumWidth(120)
        self.drive_credentials_browse_button.setEnabled(False)
        self.drive_credentials_browse_button.clicked.connect(self.browse_drive_credentials)
        self.drive_folder_id_input = QLineEdit(self)
        self.drive_folder_id_input.setPlaceholderText("Drive Folder ID (optional)")
        self.drive_folder_id_input.setMinimumWidth(260)
        self.drive_folder_id_input.setEnabled(False)
        cloud_options_layout.addWidget(self.upload_drive_checkbox, 2)
        cloud_options_layout.addWidget(self.drive_credentials_input, 4)
        cloud_options_layout.addWidget(self.drive_credentials_browse_button, 1)
        cloud_options_layout.addWidget(self.drive_folder_id_input, 3)
        main_layout.addLayout(cloud_options_layout)

        # Export Button
        self.export_button = QPushButton("Export", self)
        self.export_button.setObjectName("primaryButton")
        self.export_button.setFont(QFont('Roboto', 12))
        self.export_button.clicked.connect(self.confirm_start_export)
        main_layout.addWidget(self.export_button, alignment=Qt.AlignCenter)

        # Abort Button
        self.abort_button = QPushButton("Abort", self)
        self.abort_button.setObjectName("dangerButton")
        self.abort_button.setFont(QFont('Roboto', 12))
        self.abort_button.clicked.connect(self.abort_export)
        self.abort_button.setDisabled(True)
        main_layout.addWidget(self.abort_button, alignment=Qt.AlignCenter)

        # Progress Label and Bar
        self.progress_label = QLabel("Progress: ", self)
        self.progress_label.setFont(QFont('Roboto', 12))
        self.progress_bar = QProgressBar(self)
        main_layout.addWidget(self.progress_label)
        main_layout.addWidget(self.progress_bar)

        # Set central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Add margins and spacing
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)

        self.export_thread = None

        # Create the menu bar
        self.create_menu_bar()
        self.apply_theme()
        self.observe_system_theme_changes()

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # Create the 'File' menu
        file_menu = menu_bar.addMenu('File')

        # Create 'Create Backup Script' action
        create_backup_action = QAction('Create Backup Script', self)
        create_backup_action.triggered.connect(self.create_backup_script)
        file_menu.addAction(create_backup_action)

        # Create 'Load Backup Script' action
        load_backup_action = QAction('Load Backup Script', self)
        load_backup_action.triggered.connect(self.load_backup_script)
        file_menu.addAction(load_backup_action)

        # Add Check for Updates action
        check_updates_action = QAction('Check for Updates', self)
        check_updates_action.triggered.connect(self.check_for_updates)
        file_menu.addAction(check_updates_action)

        # Add Decrypt Backup action
        decrypt_backup_action = QAction('Decrypt Backup', self)
        decrypt_backup_action.triggered.connect(self.decrypt_backup_file)
        file_menu.addAction(decrypt_backup_action)

        # Create the 'About' menu
        about_menu = menu_bar.addMenu('About')

        # Create 'About MongoDB Exporter' action
        about_action = QAction('About MongoDB Exporter', self)
        about_action.triggered.connect(self.show_about_dialog)
        about_menu.addAction(about_action)

        # Create theme menu
        theme_menu = menu_bar.addMenu('Theme')
        theme_group = QActionGroup(self)
        theme_group.setExclusive(True)

        self.theme_actions = {
            "system": QAction("System", self, checkable=True),
            "light": QAction("Light", self, checkable=True),
            "dark": QAction("Dark", self, checkable=True)
        }

        for mode, action in self.theme_actions.items():
            action.triggered.connect(lambda checked, selected=mode: self.set_theme(selected))
            theme_group.addAction(action)
            theme_menu.addAction(action)

        self.theme_actions["system"].setChecked(True)

    def toggle_encryption_password(self, checked):
        self.encrypt_password_input.setEnabled(checked)
        if not checked:
            self.encrypt_password_input.clear()

    def toggle_drive_upload_options(self, checked):
        self.drive_credentials_input.setEnabled(checked)
        self.drive_credentials_browse_button.setEnabled(checked)
        self.drive_folder_id_input.setEnabled(checked)
        if not checked:
            self.drive_credentials_input.clear()
            self.drive_folder_id_input.clear()

    def set_theme(self, mode):
        self.theme_mode = mode
        self.apply_theme()

    def observe_system_theme_changes(self):
        style_hints = QApplication.instance().styleHints()
        if hasattr(style_hints, "colorSchemeChanged"):
            style_hints.colorSchemeChanged.connect(self.handle_system_theme_change)

    def handle_system_theme_change(self, _scheme):
        if self.theme_mode == "system":
            self.apply_theme()

    def detect_system_theme(self):
        app = QApplication.instance()
        style_hints = app.styleHints()

        if hasattr(style_hints, "colorScheme"):
            scheme = style_hints.colorScheme()
            if scheme == Qt.ColorScheme.Dark:
                return "dark"
            return "light"

        window_color = app.palette().window().color()
        return "dark" if window_color.lightness() < 128 else "light"

    def apply_theme(self):
        selected_theme = self.theme_mode
        if selected_theme == "system":
            selected_theme = self.detect_system_theme()

        qss = self.build_neumorphism_qss(selected_theme)
        QApplication.instance().setStyleSheet(qss)

    def build_neumorphism_qss(self, theme):
        if theme == "dark":
            return """
                QMainWindow, QWidget, QDialog {
                    background-color: #242931;
                    color: #e8edf2;
                    font-family: 'Roboto';
                }
                QLabel {
                    color: #e8edf2;
                }
                QCheckBox {
                    color: #e8edf2;
                    spacing: 8px;
                    padding: 4px 0;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border: 1px solid #1f232a;
                    border-radius: 4px;
                    background-color: #2b313a;
                }
                QCheckBox::indicator:checked {
                    background-color: #4f9cd8;
                }
                QLineEdit, QProgressBar, QMenuBar, QMenu {
                    background-color: #2b313a;
                    color: #e8edf2;
                    border: 1px solid #1f232a;
                    border-radius: 12px;
                    padding: 8px;
                }
                QLineEdit:focus {
                    border: 1px solid #5ca7e5;
                    background-color: #313844;
                }
                QPushButton {
                    background-color: #2b313a;
                    color: #e8edf2;
                    border: 1px solid #1f232a;
                    border-radius: 14px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #323a45;
                }
                QPushButton:pressed {
                    background-color: #21262e;
                }
                QPushButton:disabled {
                    color: #8b939f;
                    background-color: #252a32;
                }
                QPushButton#primaryButton {
                    background-color: #3e7fb8;
                    color: #ffffff;
                    border: 1px solid #356f9f;
                }
                QPushButton#primaryButton:hover {
                    background-color: #4a8dc7;
                }
                QPushButton#dangerButton {
                    background-color: #bd4f5d;
                    color: #ffffff;
                    border: 1px solid #9f4250;
                }
                QPushButton#dangerButton:hover {
                    background-color: #cc5b6a;
                }
                QProgressBar {
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #4f9cd8;
                    border-radius: 8px;
                }
                QMenuBar::item:selected, QMenu::item:selected {
                    background-color: #313844;
                    border-radius: 8px;
                }
            """

        return """
            QMainWindow, QWidget, QDialog {
                background-color: #e8edf2;
                color: #1f2a36;
                font-family: 'Roboto';
            }
            QLabel {
                color: #1f2a36;
            }
            QCheckBox {
                color: #1f2a36;
                spacing: 8px;
                padding: 4px 0;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #d4dae1;
                border-radius: 4px;
                background-color: #e8edf2;
            }
            QCheckBox::indicator:checked {
                background-color: #4b9fda;
            }
            QLineEdit, QProgressBar, QMenuBar, QMenu {
                background-color: #e8edf2;
                color: #1f2a36;
                border: 1px solid #d4dae1;
                border-radius: 12px;
                padding: 8px;
            }
            QLineEdit:focus {
                border: 1px solid #4b9fda;
                background-color: #f1f5f9;
            }
            QPushButton {
                background-color: #e8edf2;
                color: #1f2a36;
                border: 1px solid #d4dae1;
                border-radius: 14px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #f0f4f8;
            }
            QPushButton:pressed {
                background-color: #dfe6ed;
            }
            QPushButton:disabled {
                color: #8e97a2;
                background-color: #dfe5ec;
            }
            QPushButton#primaryButton {
                background-color: #3f89c5;
                color: #ffffff;
                border: 1px solid #3674a7;
            }
            QPushButton#primaryButton:hover {
                background-color: #4a95d5;
            }
            QPushButton#dangerButton {
                background-color: #d65a67;
                color: #ffffff;
                border: 1px solid #b64d58;
            }
            QPushButton#dangerButton:hover {
                background-color: #df6874;
            }
            QProgressBar {
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4b9fda;
                border-radius: 8px;
            }
            QMenuBar::item:selected, QMenu::item:selected {
                background-color: #dfe7ee;
                border-radius: 8px;
            }
        """

    def show_about_dialog(self):
        about_dialog = AboutDialog()
        about_dialog.exec()

    def create_backup_script(self):
        backup_data = {
            'uri': self.uri_input.text(),
            'db_name': self.db_name_input.text(),
            'output_dir': self.output_dir_input.text(),
            'compress_backup': self.compress_checkbox.isChecked(),
            'encrypt_backup': self.encrypt_checkbox.isChecked(),
            'upload_to_drive': self.upload_drive_checkbox.isChecked(),
            'drive_credentials_path': self.drive_credentials_input.text(),
            'drive_folder_id': self.drive_folder_id_input.text()
        }

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Backup Script", "",
                                                   "JSON Files (*.mdbexport);;All Files (*)",
                                                   options=options)
        if file_name:
            with open(file_name, 'w') as file:
                json.dump(backup_data, file)
            QMessageBox.information(self, "Success", "Backup script created successfully!")

    def load_backup_script(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Backup Script", "",
                                                   "JSON Files (*.mdbexport);;All Files (*)",
                                                   options=options)
        if file_name:
            with open(file_name, 'r') as file:
                backup_data = json.load(file)
                self.uri_input.setText(backup_data['uri'])
                self.db_name_input.setText(backup_data['db_name'])
                self.output_dir_input.setText(backup_data['output_dir'])
                self.compress_checkbox.setChecked(backup_data.get('compress_backup', True))
                self.encrypt_checkbox.setChecked(backup_data.get('encrypt_backup', False))
                self.encrypt_password_input.clear()
                self.upload_drive_checkbox.setChecked(backup_data.get('upload_to_drive', False))
                self.drive_credentials_input.setText(backup_data.get('drive_credentials_path', ''))
                self.drive_folder_id_input.setText(backup_data.get('drive_folder_id', ''))

            reply = QMessageBox.question(
                self, 'Start Export', 'Do you want to start the export now?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.start_export()

    def browse_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.output_dir_input.setText(directory)

    def browse_drive_credentials(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Google Service Account Credentials",
            "",
            "JSON Files (*.json);;All Files (*)",
            options=options
        )
        if file_name:
            self.drive_credentials_input.setText(file_name)

    def confirm_start_export(self):
        reply = QMessageBox.question(
            self, 'Confirm Export', 'Are you sure you want to start the export?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.start_export()

    def start_export(self):
        uri = self.uri_input.text()
        db_name = self.db_name_input.text()
        output_dir = self.output_dir_input.text()
        compress_backup = self.compress_checkbox.isChecked()
        encrypt_backup = self.encrypt_checkbox.isChecked()
        encrypt_password = self.encrypt_password_input.text()
        upload_to_drive = self.upload_drive_checkbox.isChecked()
        drive_credentials_path = self.drive_credentials_input.text()
        drive_folder_id = self.drive_folder_id_input.text()

        if not uri or not db_name or not output_dir:
            QMessageBox.critical(self, "Error", "All fields are required!")
        elif encrypt_backup and len(encrypt_password) < 8:
            QMessageBox.critical(self, "Error", "Encryption password must be at least 8 characters.")
        elif upload_to_drive and not drive_credentials_path:
            QMessageBox.critical(self, "Error", "Google Drive credentials JSON is required for upload.")
        elif upload_to_drive and not os.path.isfile(drive_credentials_path):
            QMessageBox.critical(self, "Error", "Google Drive credentials file not found.")
        else:
            self.export_button.setDisabled(True)
            self.abort_button.setDisabled(False)
            self.export_thread = ExportThread(
                uri, db_name, output_dir,
                compress_backup=compress_backup,
                encrypt_backup=encrypt_backup,
                encryption_password=encrypt_password,
                upload_to_drive=upload_to_drive,
                drive_credentials_path=drive_credentials_path,
                drive_folder_id=drive_folder_id
            )
            self.export_thread.update_progress.connect(self.update_progress)
            self.export_thread.update_zip_progress.connect(self.update_zip_progress)
            self.export_thread.finished.connect(self.export_finished)
            self.export_thread.error_occurred.connect(self.export_error)
            self.export_thread.start()

    def update_progress(self, overall_percentage, collection_name, processed_documents, total_documents,
                        document_percentage):
        self.progress_label.setText(
            f"Exporting: {collection_name}.json ({processed_documents}/{total_documents} documents) - Overall {overall_percentage:.2f}%")
        self.progress_bar.setValue(int(overall_percentage))
        QApplication.processEvents()

    def update_zip_progress(self, zip_progress, file_name):
        self.progress_label.setText(f"Processing: {file_name} - Overall {zip_progress:.2f}%")
        self.progress_bar.setValue(zip_progress)
        QApplication.processEvents()

    def export_finished(self, message):
        self.progress_label.setText(message)
        self.export_button.setDisabled(False)
        self.abort_button.setDisabled(True)
        QMessageBox.information(self, "Success", message)

    def export_error(self, message):
        self.progress_label.setText("Error occurred!")
        self.export_button.setDisabled(False)
        self.abort_button.setDisabled(True)
        QMessageBox.critical(self, "Error", f"An error occurred: {message}")

    def abort_export(self):
        if self.export_thread:
            self.export_thread.abort()
            self.abort_button.setDisabled(True)
            self.progress_label.setText("Aborting export...")

    def check_for_updates(self):
        current_version = "2.3.0"  # Replace with your current version
        repo = "Sarwarhridoy4/MongoDB-Exporter"  # Replace with your GitHub repo

        self.update_thread = UpdateThread(repo, current_version)
        self.update_thread.update_progress.connect(self.show_update_progress)
        self.update_thread.update_finished.connect(self.update_finished)
        self.update_thread.update_error.connect(self.update_error)
        self.update_thread.start()

        self.update_dialog = QDialog(self)
        self.update_dialog.setWindowTitle("Checking for Updates")
        self.update_dialog.setGeometry(300, 300, 300, 150)
        layout = QVBoxLayout()

        self.update_label = QLabel("Checking for updates...", self.update_dialog)
        self.update_progress_bar = QProgressBar(self.update_dialog)

        layout.addWidget(self.update_label)
        layout.addWidget(self.update_progress_bar)

        self.update_dialog.setLayout(layout)
        self.update_dialog.show()

    def show_update_progress(self, value, speed):
        self.update_progress_bar.setValue(value)
        self.update_label.setText(f"Downloading update... {value}% - {speed}")

    def update_finished(self, message):
        self.update_dialog.close()
        QMessageBox.information(self, "Update", message)

    def update_error(self, message):
        self.update_dialog.close()
        QMessageBox.critical(self, "Update Error", message)

    def decrypt_backup_file(self):
        options = QFileDialog.Options()
        encrypted_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Encrypted Backup",
            "",
            "Encrypted Backup (*.enc);;All Files (*)",
            options=options
        )
        if not encrypted_path:
            return

        password, ok = QInputDialog.getText(
            self,
            "Decrypt Backup",
            "Enter decryption password:",
            QLineEdit.Password
        )
        if not ok:
            return

        if not password:
            QMessageBox.critical(self, "Error", "Password is required to decrypt backup.")
            return

        default_output = encrypted_path[:-4] if encrypted_path.endswith(".enc") else f"{encrypted_path}.dec"
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Decrypted Backup",
            default_output,
            "ZIP Files (*.zip);;All Files (*)",
            options=options
        )
        if not output_path:
            return

        try:
            self.progress_label.setText("Decrypting backup...")
            self.progress_bar.setValue(0)
            self.decrypt_file(encrypted_path, output_path, password)
            self.progress_label.setText(f"Decryption complete: {output_path}")
            self.progress_bar.setValue(100)
            QMessageBox.information(self, "Success", f"Backup decrypted successfully:\n{output_path}")
        except Exception as e:
            self.progress_label.setText("Decryption failed.")
            self.progress_bar.setValue(0)
            QMessageBox.critical(self, "Decryption Error", str(e))

    def decrypt_file(self, encrypted_path, output_path, password):
        header_size = 6
        salt_size = 16
        nonce_size = 12
        tag_size = 16
        metadata_size = header_size + salt_size + nonce_size

        with open(encrypted_path, "rb") as source_file:
            magic = source_file.read(header_size)
            if magic != b"MDBEX1":
                raise ValueError("Invalid backup format. This file was not encrypted by MongoDB Exporter.")

            salt = source_file.read(salt_size)
            nonce = source_file.read(nonce_size)

            source_file.seek(0, os.SEEK_END)
            total_size = source_file.tell()
            if total_size <= metadata_size + tag_size:
                raise ValueError("Encrypted backup file is incomplete or corrupted.")

            source_file.seek(total_size - tag_size)
            tag = source_file.read(tag_size)

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=390000,
                backend=default_backend()
            )
            key = kdf.derive(password.encode("utf-8"))
            decryptor = Cipher(
                algorithms.AES(key),
                modes.GCM(nonce, tag),
                backend=default_backend()
            ).decryptor()

            ciphertext_size = total_size - metadata_size - tag_size
            processed = 0
            chunk_size = 1024 * 1024

            source_file.seek(metadata_size)
            with open(output_path, "wb") as output_file:
                try:
                    while processed < ciphertext_size:
                        to_read = min(chunk_size, ciphertext_size - processed)
                        chunk = source_file.read(to_read)
                        if not chunk:
                            break
                        output_file.write(decryptor.update(chunk))
                        processed += len(chunk)
                        progress = int((processed / ciphertext_size) * 100)
                        self.progress_bar.setValue(progress)
                        QApplication.processEvents()

                    output_file.write(decryptor.finalize())
                except InvalidTag as error:
                    output_file.close()
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    raise ValueError("Invalid password or corrupted encrypted backup.") from error
                except Exception:
                    output_file.close()
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    raise
