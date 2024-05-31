import os
import json
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QWidget, QFileDialog, QMessageBox, QProgressBar
)
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt
from pymongo import MongoClient
from bson.json_util import dumps

class MongoDBExporter(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MongoDB Exporter")
        self.setGeometry(100, 100, 600, 400)

        # Set window icon (favicon)
        self.setWindowIcon(QIcon("./asset/favicon.png"))  # Provide the path to your favicon file

        # Main layout
        main_layout = QVBoxLayout()

        # Title and logo layout
        title_layout = QHBoxLayout()
        self.logo_label = QLabel(self)
        pixmap = QPixmap("./asset/mongo_icon.png")  # Provide the path to your logo image
        self.logo_label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.title_label = QLabel("MongoDB Exporter", self)
        self.title_label.setFont(QFont('Arial', 18, QFont.Bold))

        title_layout.addWidget(self.logo_label)
        title_layout.addWidget(self.title_label, alignment=Qt.AlignVCenter)
        main_layout.addLayout(title_layout)

        # URI
        uri_layout = QHBoxLayout()
        self.uri_label = QLabel("MongoDB URI:", self)
        self.uri_label.setFont(QFont('Arial', 12))
        self.uri_input = QLineEdit(self)
        self.uri_input.setFont(QFont('Arial', 12))
        uri_layout.addWidget(self.uri_label)
        uri_layout.addWidget(self.uri_input)
        main_layout.addLayout(uri_layout)

        # Database Name
        db_name_layout = QHBoxLayout()
        self.db_name_label = QLabel("Database Name:", self)
        self.db_name_label.setFont(QFont('Arial', 12))
        self.db_name_input = QLineEdit(self)
        self.db_name_input.setFont(QFont('Arial', 12))
        db_name_layout.addWidget(self.db_name_label)
        db_name_layout.addWidget(self.db_name_input)
        main_layout.addLayout(db_name_layout)

        # Output Directory
        output_dir_layout = QHBoxLayout()
        self.output_dir_label = QLabel("Output Directory:", self)
        self.output_dir_label.setFont(QFont('Arial', 12))
        self.output_dir_input = QLineEdit(self)
        self.output_dir_input.setFont(QFont('Arial', 12))
        self.browse_button = QPushButton("Browse", self)
        self.browse_button.setFont(QFont('Arial', 12))
        self.browse_button.clicked.connect(self.browse_output_dir)
        output_dir_layout.addWidget(self.output_dir_label)
        output_dir_layout.addWidget(self.output_dir_input)
        output_dir_layout.addWidget(self.browse_button)
        main_layout.addLayout(output_dir_layout)

        # Export Button
        self.export_button = QPushButton("Export", self)
        self.export_button.setFont(QFont('Arial', 12))
        self.export_button.clicked.connect(self.start_export)
        main_layout.addWidget(self.export_button, alignment=Qt.AlignCenter)

        # Progress Label and Bar
        self.progress_label = QLabel("Progress: ", self)
        self.progress_label.setFont(QFont('Arial', 12))
        self.progress_bar = QProgressBar(self)
        main_layout.addWidget(self.progress_label)
        main_layout.addWidget(self.progress_bar)

        # Set central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Add margins and spacing
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

    def browse_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.output_dir_input.setText(directory)

    def start_export(self):
        uri = self.uri_input.text()
        db_name = self.db_name_input.text()
        output_dir = self.output_dir_input.text()

        if not uri or not db_name or not output_dir:
            QMessageBox.critical(self, "Error", "All fields are required!")
        else:
            self.export_collections_to_json(uri, db_name, output_dir)

    def export_collections_to_json(self, uri, db_name, output_dir):
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            client = MongoClient(uri)
            db = client[db_name]
            collections = db.list_collection_names()
            total_collections = len(collections)

            if total_collections == 0:
                self.progress_label.setText("No collections found in the database.")
                return

            for index, collection_name in enumerate(collections):
                collection = db[collection_name]
                if collection.count_documents({}) > 0:
                    total_documents = collection.count_documents({})
                    processed_documents = 0

                    percentage = ((index + 1) / total_collections) * 100
                    self.progress_label.setText(f"Exporting: {collection_name}.json ({percentage:.2f}%)")
                    self.progress_bar.setValue(int(percentage))

                    with open(os.path.join(output_dir, f"{collection_name}.json"), "w") as file:
                        cursor = collection.find()
                        for document in cursor:
                            file.write(dumps(document, indent=4) + "\n")
                            processed_documents += 1
                            document_percentage = (processed_documents / total_documents) * 100
                            self.progress_label.setText(f"Exporting: {collection_name}.json ({percentage:.2f}%) - {processed_documents}/{total_documents} documents ({document_percentage:.2f}%)")
                            QApplication.processEvents()

            client.close()
            self.progress_label.setText("Export completed successfully!")
            QMessageBox.information(self, "Success", "Export completed successfully!")
        except Exception as e:
            self.progress_label.setText("Error occurred!")
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

def main():
    app = QApplication(sys.argv)
    window = MongoDBExporter()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
