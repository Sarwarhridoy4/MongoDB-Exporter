import os
import json
from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QWidget, QFileDialog, QMessageBox, QProgressBar, QGraphicsOpacityEffect, QAction, QDialog
)
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from export_thread import ExportThread
from updater import UpdateThread
from utils import resource_path


class MongoDBExporter(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MongoDB Exporter")
        self.setGeometry(100, 100, 600, 400)

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

        # Export Button
        self.export_button = QPushButton("Export", self)
        self.export_button.setFont(QFont('Roboto', 12))
        self.export_button.clicked.connect(self.confirm_start_export)
        main_layout.addWidget(self.export_button, alignment=Qt.AlignCenter)

        # Abort Button
        self.abort_button = QPushButton("Abort", self)
        self.abort_button.setFont(QFont('Roboto', 12))
        self.abort_button.setStyleSheet("background-color: red; color: white;")
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

    def create_backup_script(self):
        backup_data = {
            'uri': self.uri_input.text(),
            'db_name': self.db_name_input.text(),
            'output_dir': self.output_dir_input.text()
        }

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Backup Script", "", "JSON Files (*.mdbexport);;All Files (*)",
                                                   options=options)
        if file_name:
            with open(file_name, 'w') as file:
                json.dump(backup_data, file)
            QMessageBox.information(self, "Success", "Backup script created successfully!")

    def load_backup_script(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Backup Script", "", "JSON Files (*.mdbexport);;All Files (*)",
                                                   options=options)
        if file_name:
            with open(file_name, 'r') as file:
                backup_data = json.load(file)
                self.uri_input.setText(backup_data['uri'])
                self.db_name_input.setText(backup_data['db_name'])
                self.output_dir_input.setText(backup_data['output_dir'])

            reply = QMessageBox.question(
                self, 'Start Export', 'Do you want to start the export now?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.start_export()

    def browse_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.output_dir_input.setText(directory)

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

        if not uri or not db_name or not output_dir:
            QMessageBox.critical(self, "Error", "All fields are required!")
        else:
            self.export_button.setDisabled(True)
            self.abort_button.setDisabled(False)
            self.export_thread = ExportThread(uri, db_name, output_dir)
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
        self.progress_label.setText(f"Zipping: {file_name} - Overall {zip_progress:.2f}%")
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

    def check_for_updates(self):
        current_version = "2.2.2"  # Replace with your current version
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
