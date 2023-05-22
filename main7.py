from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QLineEdit, QProgressBar, QMenuBar, QMenu, QAction, QInputDialog, QListWidget, QListWidgetItem, QCheckBox
from CloudFlare import CloudFlare
import requests
import sys

class UpdateDomainListThread(QtCore.QThread):
    progress_signal = QtCore.pyqtSignal(int)

    def __init__(self, api_key, domain_list, update_domains_button, select_all_button):
        QtCore.QThread.__init__(self)
        self.api_key = api_key
        self.domain_list = domain_list
        self.update_domains_button = update_domains_button
        self.select_all_button = select_all_button

    def run(self):
        self.domain_list.clear()

        cf = CloudFlare(token=self.api_key)
        zones = cf.zones.get()
        total_zones = len(zones)
        for i, zone in enumerate(zones):
            zone_id = zone['id']
            dns_records = cf.zones.dns_records.get(zone_id)
            for dns_record in dns_records:
                if dns_record['type'] == 'A':
                    checkbox = QCheckBox(dns_record['name'] + ' (' + dns_record['content'] + ')', self)
                    list_item = QListWidgetItem(self.domain_list)
                    list_item.setSizeHint(checkbox.sizeHint())
                    self.domain_list.addItem(list_item)
                    self.domain_list.setItemWidget(list_item, checkbox)
            self.update_domains_button.setEnabled(True)
            self.select_all_button.setEnabled(True)

            progress = int((i + 1) / total_zones * 100)
            self.progress_signal.emit(progress)

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cloudflare IP Updater")
        self.setGeometry(200, 200, 500, 600)  # Adjust the size to fit the new elements


        # Create buttons
        self.get_ip_button = QPushButton("Get Current IP", self)
        self.get_ip_button.move(20, 30)
        self.get_ip_button.resize(200, 30)  # Make the button wider

        self.update_domains_button = QPushButton("Update Selected Domains", self)
        self.update_domains_button.move(20, 80)
        self.update_domains_button.resize(200, 30)  # Make the button wider
        self.update_domains_button.setEnabled(False)

        self.update_list_button = QPushButton("Get domain/zone list", self)
        self.update_list_button.move(20, 130)
        self.update_list_button.resize(200, 30)
        self.update_list_button.setEnabled(False)

        self.select_all_button = QPushButton("Select All Domains", self)
        self.select_all_button.move(20, 180)
        self.select_all_button.resize(200, 30)  # Make the button wider
        self.select_all_button.setEnabled(False)

        # Create label
        self.ip_label = QLabel(self)
        self.ip_label.move(230, 25)

        # Create list widget
        self.domain_list = QListWidget(self)
        self.domain_list.move(20, 230)
        self.domain_list.resize(460, 350)

        # Create menu bar
        self.menu_bar = self.menuBar()
        self.options_menu = QMenu("Options", self)
        self.menu_bar.addMenu(self.options_menu)

        # Create progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.move(20, 590)
        self.progress_bar.resize(460, 20)
        self.progress_bar.setValue(0)  # Initialize progress bar to 0

        # Create action
        self.set_api_key_action = QAction("Set API Key", self)
        self.options_menu.addAction(self.set_api_key_action)

        # Connect signals and slots
        self.get_ip_button.clicked.connect(self.get_current_ip)
        self.update_domains_button.clicked.connect(self.update_all_domains)
        self.update_list_button.clicked.connect(self.update_domain_list)
        self.select_all_button.clicked.connect(self.select_all_domains)
        self.set_api_key_action.triggered.connect(self.set_api_key)


    def get_current_ip(self):
        response = requests.get('https://httpbin.org/ip')
        if response.status_code == 200:
            self.current_ip = response.json()['origin']
            self.ip_label.setText(self.current_ip)

    def update_all_domains(self):
        cf = CloudFlare(token=self.api_key)
        zones = cf.zones.get()
        for zone in zones:
            zone_id = zone['id']
            dns_records = cf.zones.dns_records.get(zone_id)
            for dns_record in dns_records:
                if dns_record['type'] == 'A':
                    # Check if the domain is selected
                    for i in range(self.domain_list.count()):
                        item = self.domain_list.item(i)
                        checkbox = self.domain_list.itemWidget(item)
                        if checkbox.text().startswith(dns_record['name']) and checkbox.isChecked():
                            # Update the DNS record
                            dns_record['content'] = self.current_ip
                            cf.zones.dns_records.put(zone_id, dns_record['id'], data=dns_record)

    def update_domain_list(self):
        self.update_domain_list_thread = UpdateDomainListThread(self.api_key, self.domain_list, self.update_domains_button, self.select_all_button)
        self.update_domain_list_thread.progress_signal.connect(self.progress_bar.setValue)
        self.update_domain_list_thread.start()


    def select_all_domains(self):
        for i in range(self.domain_list.count()):
            item = self.domain_list.item(i)
            checkbox = self.domain_list.itemWidget(item)
            checkbox.setChecked(True)

    def set_api_key(self):
        self.api_key, ok = QInputDialog.getText(self, "Set API Key", "Enter your Cloudflare API Key:")
        if ok:
            # Save the API key for later use
            # You might want to securely store this key instead of just saving it in memory

            self.api_key = self.api_key.strip()
            self.update_list_button.setEnabled(True)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
