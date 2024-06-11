import requests
import os
import zipfile
import time
from PyQt5.QtCore import QThread, pyqtSignal


class UpdateThread(QThread):
    update_progress = pyqtSignal(int, str)
    update_finished = pyqtSignal(str)
    update_error = pyqtSignal(str)

    def __init__(self, repo, current_version):
        super().__init__()
        self.repo = repo
        self.current_version = current_version

    def run(self):
        try:
            latest_release = self.get_latest_release()
            latest_version = latest_release['tag_name']
            if self.is_newer_version(latest_version, self.current_version):
                asset = self.get_asset(latest_release)
                if asset:
                    download_url = asset['browser_download_url']
                    self.download_update(download_url)
                    self.install_update()
                    self.update_finished.emit("Update downloaded and installed successfully.")
                else:
                    self.update_error.emit("No suitable asset found for the latest release.")
            else:
                self.update_finished.emit("No updates available.")
        except Exception as e:
            self.update_error.emit(str(e))

    def get_latest_release(self):
        url = f"https://api.github.com/repos/{self.repo}/releases/latest"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def is_newer_version(self, latest_version, current_version):
        latest_parts = latest_version.lstrip('v').split('.')
        current_parts = current_version.lstrip('v').split('.')
        for latest, current in zip(latest_parts, current_parts):
            if int(latest) > int(current):
                return True
            elif int(latest) < int(current):
                return False
        return len(latest_parts) > len(current_parts)

    def get_asset(self, release):
        for asset in release['assets']:
            if asset['name'].endswith('.zip') or asset['name'].endswith('.exe'):
                return asset
        return None

    def download_update(self, url):
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        chunk_size = 1024
        output_path = os.path.join(os.path.abspath("."), "update.zip" if url.endswith('.zip') else "update.exe")

        start_time = time.time()
        downloaded_size = 0

        with open(output_path, 'wb') as file:
            for data in response.iter_content(chunk_size):
                file.write(data)
                downloaded_size += len(data)
                elapsed_time = time.time() - start_time
                download_speed = downloaded_size / elapsed_time / 1024  # KB/s
                percentage = downloaded_size * 100 / total_size
                self.update_progress.emit(int(percentage), f"Speed: {download_speed:.2f} KB/s")

    def install_update(self):
        update_path = os.path.join(os.path.abspath("."), "update.zip")
        if os.path.exists(update_path):
            with zipfile.ZipFile(update_path, 'r') as zip_ref:
                zip_ref.extractall(os.path.abspath("."))
            os.remove(update_path)
        else:
            update_path = os.path.join(os.path.abspath("."), "update.exe")
            if os.path.exists(update_path):
                os.startfile(update_path)
                os._exit(0)
