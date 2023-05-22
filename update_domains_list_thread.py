from PyQt5 import QtCore
from CloudFlare import CloudFlare

class UpdateDomainListThread(QtCore.QThread):
    progress_signal = QtCore.pyqtSignal(int)
    data_signal = QtCore.pyqtSignal(dict)

    def __init__(self, api_key):
        QtCore.QThread.__init__(self)
        self.api_key = api_key

    def run(self):
        cf = CloudFlare(token=self.api_key)
        zones = cf.zones.get()
        total_zones = len(zones)
        for i, zone in enumerate(zones):
            zone_id = zone['id']
            dns_records = cf.zones.dns_records.get(zone_id)
            for dns_record in dns_records:
                if dns_record['type'] == 'A':
                    self.data_signal.emit(dns_record)

            progress = int((i + 1) / total_zones * 100)
            self.progress_signal.emit(progress)