from PyQt5 import QtCore
from CloudFlare import CloudFlare


class UpdateDomainListThread(QtCore.QThread):
    """A QThread that fetches the list of domains/zones from Cloudflare."""

    progress_signal = QtCore.pyqtSignal(int)  # Signal for progress updates
    data_signal = QtCore.pyqtSignal(object)  # Signal for passing fetched data
    error_signal = QtCore.pyqtSignal(str)  # Signal for error notifications

    def __init__(self, api_key: str):
        """
        Initializes the thread with the given Cloudflare API key.

        :param api_key: The Cloudflare API key.
        """
        QtCore.QThread.__init__(self)
        self.api_key = api_key

    def run(self):
        """Fetches the list of domains/zones and emits progress and data signals."""
        try:
            cf = CloudFlare(token=self.api_key)  # Connect to Cloudflare with the API key
            zones = cf.zones.get()  # Get the list of zones
            total_zones = len(zones)  # Total number of zones
            for i, zone in enumerate(zones):
                zone_id = zone['id']  # Get the zone ID
                dns_records = cf.zones.dns_records.get(zone_id)  # Get DNS records for the zone
                for dns_record in dns_records:
                    if dns_record['type'] == 'A':  # Only interested in 'A' records
                        self.data_signal.emit(dns_record)  # Emit signal with the DNS record

                # Calculate and emit progress
                progress = int((i + 1) / total_zones * 100)
                self.progress_signal.emit(progress)
        except Exception as e:
            # Emit error signal with the error message
            self.error_signal.emit(f"An error occurred in UpdateDomainListThread: {str(e)}")
