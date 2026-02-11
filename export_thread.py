import os
import datetime
import threading
import zipfile

from PySide6.QtCore import QThread, Signal
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pymongo import MongoClient
from bson.json_util import dumps


class ExportThread(QThread):
    update_progress = Signal(int, str, int, int, float)
    update_zip_progress = Signal(int, str)
    finished = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, uri, db_name, output_dir, compress_backup=True, encrypt_backup=False, encryption_password=""):
        super().__init__()
        self.uri = uri
        self.db_name = db_name
        self.output_dir = output_dir
        self.compress_backup = compress_backup
        self.encrypt_backup = encrypt_backup
        self.encryption_password = encryption_password
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

            if self.abort_flag:
                self.finished.emit("Export aborted by user.")
                return

            outputs = [self.output_dir]
            target_file = None

            if self.compress_backup or self.encrypt_backup:
                target_file = self.zip_output_folder()
                if target_file is None:
                    return
                outputs.append(target_file)

            if self.encrypt_backup:
                encrypted_file = self.encrypt_file(target_file, self.encryption_password)
                if encrypted_file is None:
                    return
                outputs.append(encrypted_file)

            self.finished.emit("Export completed successfully!\nOutput:\n" + "\n".join(outputs))
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

                        if processed_documents % batch_size == 0 or processed_documents == total_documents:
                            self.update_progress.emit(
                                int(overall_percentage),
                                collection_name,
                                processed_documents,
                                total_documents,
                                document_percentage
                            )

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
        all_files = []
        for root, _, files in os.walk(self.output_dir):
            for file in files:
                all_files.append((root, file))

        total_files = len(all_files)
        if total_files == 0:
            return zip_file_path

        with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for index, (root, file) in enumerate(all_files, start=1):
                if self.abort_flag:
                    self.finished.emit("Export aborted by user.")
                    return None

                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, self.output_dir))
                zip_progress = (index / total_files) * 100
                self.update_zip_progress.emit(int(zip_progress), f"Compressing {file}")

        return zip_file_path

    def encrypt_file(self, input_file_path, password):
        if not input_file_path:
            self.error_occurred.emit("Unable to encrypt backup: no archive found.")
            return None

        if not password:
            self.error_occurred.emit("Encryption password is required.")
            return None

        output_file_path = f"{input_file_path}.enc"
        salt = os.urandom(16)
        nonce = os.urandom(12)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=390000,
            backend=default_backend(),
        )
        key = kdf.derive(password.encode("utf-8"))
        encryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce),
            backend=default_backend(),
        ).encryptor()

        total_size = os.path.getsize(input_file_path)
        processed = 0
        chunk_size = 1024 * 1024

        with open(input_file_path, "rb") as source_file, open(output_file_path, "wb") as encrypted_file:
            encrypted_file.write(b"MDBEX1")
            encrypted_file.write(salt)
            encrypted_file.write(nonce)

            while True:
                if self.abort_flag:
                    self.finished.emit("Export aborted by user.")
                    return None

                chunk = source_file.read(chunk_size)
                if not chunk:
                    break

                encrypted_file.write(encryptor.update(chunk))
                processed += len(chunk)
                if total_size > 0:
                    progress = (processed / total_size) * 100
                    self.update_zip_progress.emit(int(progress), "Encrypting backup")

            encrypted_file.write(encryptor.finalize())
            encrypted_file.write(encryptor.tag)

        self.update_zip_progress.emit(100, "Encryption complete")
        return output_file_path

    def abort(self):
        self.abort_flag = True
