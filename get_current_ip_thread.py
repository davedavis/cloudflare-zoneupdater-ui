from PyQt5.QtCore import QThread, pyqtSignal
import requests


class GetCurrentIpThread(QThread):
    """A QThread that retrieves the current IP address using an HTTP GET request."""

    ip_signal = pyqtSignal(str)  # Signal for sending the IP address or error message

    def run(self):
        """Retrieves the current IP and emits it, or emits an error message if an exception occurs."""
        try:
            # Send a GET request to the httpbin service to retrieve the IP
            response = requests.get('https://httpbin.org/ip')
            response.raise_for_status()  # Raises stored HTTPError, if one occurred.

            # Emit the IP address. The IP is located in the 'origin' field of the JSON response
            self.ip_signal.emit(response.json()['origin'])
        except requests.HTTPError as http_err:
            # If an HTTP error occurred, emit an error message
            self.ip_signal.emit(f"HTTP error occurred: {http_err}")
        except Exception as err:
            # If any other error occurred, emit an error message
            self.ip_signal.emit(f"An error occurred: {err}")
