# from PyQt5 import QtCore
# from PyQt5.QtWidgets import QListWidgetItem, QCheckBox
# from CloudFlare import CloudFlare
#
#
# class UpdateDomainListThread(QtCore.QThread):
#     progress_signal = QtCore.pyqtSignal(int)
#
#     def __init__(self, api_key, domain_list, update_domains_button, select_all_button):
#         QtCore.QThread.__init__(self)
#         self.api_key = api_key
#         self.domain_list = domain_list
#         self.update_domains_button = update_domains_button
#         self.select_all_button = select_all_button
#
#     def run(self):
#         self.domain_list.clear()
#
#         cf = CloudFlare(token=self.api_key)
#         zones = cf.zones.get()
#         total_zones = len(zones)
#         for i, zone in enumerate(zones):
#             zone_id = zone['id']
#             dns_records = cf.zones.dns_records.get(zone_id)
#             for dns_record in dns_records:
#                 if dns_record['type'] == 'A':
#                     checkbox = QCheckBox(dns_record['name'] + ' (' + dns_record['content'] + ')', self)
#                     list_item = QListWidgetItem(self.domain_list)
#                     list_item.setSizeHint(checkbox.sizeHint())
#                     self.domain_list.addItem(list_item)
#                     self.domain_list.setItemWidget(list_item, checkbox)
#             self.update_domains_button.setEnabled(True)
#             self.select_all_button.setEnabled(True)
#
#             progress = int((i + 1) / total_zones * 100)
#             self.progress_signal.emit(progress)
