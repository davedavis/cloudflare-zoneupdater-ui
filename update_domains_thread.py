from PyQt5 import QtCore
from CloudFlare import CloudFlare
from typing import Dict, List

class UpdateDomainsThread(QtCore.QThread):
    """A QThread that updates the IP addresses for selected domains/zones on Cloudflare."""

    progress_signal = QtCore.pyqtSignal(int)  # Signal for progress updates
    update_signal = QtCore.pyqtSignal(str, str)  # Signal for reporting successful updates
    error_signal = QtCore.pyqtSignal(str)  # Signal for error notifications

    def __init__(self, api_key: str, current_ip: str, domains: List[str]):
        """
        Initializes the thread with the given Cloudflare API key, current IP, and domains list.

        :param api_key: The Cloudflare API key.
        :param current_ip: The current IP address.
        :param domains: The list of domains to update.
        """
        QtCore.QThread.__init__(self)
        self.api_key = api_key
        self.current_ip = current_ip
        self.domains = domains

    def run(self):
        """Updates the domains with the current IP and emits progress, update, and error signals."""
        try:
            cf = CloudFlare(token=self.api_key)  # Connect to Cloudflare with the API key
            zones = cf.zones.get()  # Get the list of zones
            total_zones = len(zones)  # Total number of zones
            for i, zone in enumerate(zones):
                zone_id = zone['id']  # Get the zone ID
                dns_records = cf.zones.dns_records.get(zone_id)  # Get DNS records for the zone
                for dns_record in dns_records:
                    # If the record is an 'A' record and the name is in the domains list
                    if dns_record['type'] == 'A' and dns_record['name'] in self.domains:
                        dns_record['content'] = self.current_ip  # Update the IP address
                        cf.zones.dns_records.put(zone_id, dns_record['id'], data=dns_record)  # Update the DNS record on Cloudflare
                        self.update_signal.emit(dns_record['name'], self.current_ip)  # Emit signal with the updated domain and IP

                # Calculate and emit progress
                progress = int((i + 1) / total_zones * 100)
                self.progress_signal.emit(progress)
        except Exception as e:
            # Emit error signal with the error message
            self.error_signal.emit(f"An error occurred in UpdateDomainsThread: {str(e)}")
