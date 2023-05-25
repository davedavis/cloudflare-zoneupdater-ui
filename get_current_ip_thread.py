from PyQt5.QtCore import QThread, pyqtSignal
import requests


class GetCurrentIpThread(QThread):
    ip_signal = pyqtSignal(str)

    def run(self):
        try:
            response = requests.get('https://httpbin.org/ip')
            response.raise_for_status()  # Raises stored HTTPError, if one occurred.
            self.ip_signal.emit(response.json()['origin'])
        except requests.HTTPError as http_err:
            self.ip_signal.emit(f"HTTP error occurred: {http_err}")
        except Exception as err:
            self.ip_signal.emit(f"An error occurred: {err}")
