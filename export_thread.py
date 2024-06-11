import os
import datetime
import threading
import zipfile
from PyQt5.QtCore import QThread, pyqtSignal
from pymongo import MongoClient
from bson.json_util import dumps


class ExportThread(QThread):
    update_progress = pyqtSignal(int, str, int, int, float)
    update_zip_progress = pyqtSignal(int, str)
    finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, uri, db_name, output_dir):
        super().__init__()
        self.uri = uri
        self.db_name = db_name
        self.output_dir = output_dir
        self.abort_flag = False
        self.lock = threading.Lock()
        self.total_collections = 0
        self.processed_collections = 0
        self.total_documents = {}
        self.processed_documents = {}

    def run(self):
        try:
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)

            date_str = datetime.datetime.now().strftime("%d-%m-%Y")
            self.output_dir = os.path.join(self.output_dir, date_str)

            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)

            client = MongoClient(self.uri)
            db = client[self.db_name]
            collections = db.list_collection_names()
            self.total_collections = len(collections)

            if self.total_collections == 0:
                self.finished.emit("No collections found in the database.")
                return

            # Use a thread pool to process collections in parallel
            threads = []
            for collection_name in collections:
                if self.abort_flag:
                    self.finished.emit("Export aborted by user.")
                    return

                thread = threading.Thread(target=self.process_collection, args=(db, collection_name))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            client.close()

            # Zip the folder
            zip_file_path = self.zip_output_folder()
            self.finished.emit(f"Export completed successfully! \n Zipped at: {zip_file_path}")
        except Exception as e:
            self.error_occurred.emit(str(e))

    def process_collection(self, db, collection_name):
        try:
            collection = db[collection_name]
            total_documents = collection.count_documents({})
            self.lock.acquire()
            self.total_documents[collection_name] = total_documents
            self.processed_documents[collection_name] = 0
            self.lock.release()

            if total_documents > 0:
                processed_documents = 0

                # Increased batch size
                batch_size = 10000
                cursor = collection.find().batch_size(batch_size)

                with open(os.path.join(self.output_dir, f"{self.db_name}_{collection_name}.json"), "w") as file:
                    for document in cursor:
                        if self.abort_flag:
                            self.finished.emit("Export aborted by user.")
                            return

                        file.write(dumps(document, indent=4) + "\n")
                        processed_documents += 1

                        self.lock.acquire()
                        self.processed_documents[collection_name] = processed_documents
                        document_percentage = (processed_documents / total_documents) * 100
                        overall_percentage = self.calculate_overall_percentage()
                        self.lock.release()

                        # Update document progress
                        if processed_documents % batch_size == 0 or processed_documents == total_documents:
                            self.update_progress.emit(int(overall_percentage), collection_name, processed_documents,
                                                      total_documents, document_percentage)

            self.lock.acquire()
            self.processed_collections += 1
            self.lock.release()
        except Exception as e:
            self.error_occurred.emit(str(e))

    def calculate_overall_percentage(self):
        total_documents = sum(self.total_documents.values())
        processed_documents = sum(self.processed_documents.values())
        if total_documents == 0:
            return 0
        return (processed_documents / total_documents) * 100

    def zip_output_folder(self):
        zip_file_path = f"{self.output_dir}.zip"
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(self.output_dir):
                for file in files:
                    if self.abort_flag:
                        self.finished.emit("Export aborted by user.")
                        return

                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, self.output_dir))
                    files_processed = zipf.infolist()
                    zip_progress = (len(files_processed) / len(files)) * 100
                    self.update_zip_progress.emit(int(zip_progress), file)

        return zip_file_path

    def abort(self):
        self.abort_flag = True
