from PyQt5 import QtCore
from CloudFlare import CloudFlare

class UpdateDomainsThread(QtCore.QThread):
    progress_signal = QtCore.pyqtSignal(int)

    def __init__(self, api_key, current_ip, domains):
        QtCore.QThread.__init__(self)
        self.api_key = api_key
        self.current_ip = current_ip
        self.domains = domains

    def run(self):
        cf = CloudFlare(token=self.api_key)
        zones = cf.zones.get()
        total_zones = len(zones)
        for i, zone in enumerate(zones):
            zone_id = zone['id']
            dns_records = cf.zones.dns_records.get(zone_id)
            for dns_record in dns_records:
                if dns_record['type'] == 'A':
                    if dns_record['name'] in self.domains:
                        dns_record['content'] = self.current_ip
                        cf.zones.dns_records.put(zone_id, dns_record['id'], data=dns_record)
            progress = int((i + 1) / total_zones * 100)
            self.progress_signal.emit(progress)