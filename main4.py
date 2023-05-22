from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QLineEdit, QMenuBar, QMenu, QAction, QInputDialog, QListWidget, QListWidgetItem, QCheckBox
from CloudFlare import CloudFlare
import requests
import sys


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cloudflare IP Updater")
        self.setGeometry(200, 200, 500, 400)  # Adjust the size to fit the new elements

        # Create buttons
        self.get_ip_button = QPushButton("Get Current IP", self)
        self.get_ip_button.move(20, 20)
        self.get_ip_button.resize(200, 30)  # Make the button wider

        self.update_domains_button = QPushButton("Update Selected Domains", self)  # Change button text
        self.update_domains_button.move(20, 70)
        self.update_domains_button.resize(200, 30)  # Make the button wider
        self.update_domains_button.setEnabled(False)

        self.update_list_button = QPushButton("Update Domain List", self)
        self.update_list_button.move(20, 120)
        self.update_list_button.resize(200, 30)  # Make the button wider
        self.update_list_button.setEnabled(False)  # Disable the button until an API key is entered

        # Create label
        self.ip_label = QLabel(self)
        self.ip_label.move(230, 25)  # Move the label to avoid overlap

        # Create list widget
        self.domain_list = QListWidget(self)
        self.domain_list.move(20, 170)
        self.domain_list.resize(460, 200)

        # Create menu bar
        self.menu_bar = self.menuBar()
        self.options_menu = QMenu("Options", self)
        self.menu_bar.addMenu(self.options_menu)

        # Create action
        self.set_api_key_action = QAction("Set API Key", self)
        self.options_menu.addAction(self.set_api_key_action)

        # Connect signals and slots
        self.get_ip_button.clicked.connect(self.get_current_ip)
        self.update_domains_button.clicked.connect(self.update_all_domains)
        self.update_list_button.clicked.connect(self.update_domain_list)
        self.set_api_key_action.triggered.connect(self.set_api_key)

    def get_current_ip(self):
        response = requests.get('https://httpbin.org/ip')
        if response.status_code == 200:
            self.current_ip = response.json()['origin']
            self.ip_label.setText(self.current_ip)
            self.update_domains_button.setEnabled(True)

    def update_all_domains(self):
        cf = CloudFlare(token=self.api_key)
        zones = cf.zones.get()
        for zone in zones:
            zone_id = zone['id']
            dns_records = cf.zones.dns_records.get(zone_id)
            for dns_record in dns_records:
                if dns_record['type'] == 'A' and dns_record['name'] == zone['name']:  # only process the root A record
                    # Check if the domain is selected
                    for i in range(self.domain_list.count()):
                        item = self.domain_list.item(i)
                        checkbox = self.domain_list.itemWidget(item)
                        if checkbox.text().startswith(dns_record['name']) and checkbox.isChecked():
                            dns_record['content'] = self.current_ip
                            response = cf.zones.dns_records.put(zone_id, dns_record['id'], data=dns_record)
                            print(response)  # Print API response to the console for debugging

    def update_domain_list(self):
        # Clear the list before updating it
        self.domain_list.clear()

        cf = CloudFlare(token=self.api_key)
        zones = cf.zones.get()
        for zone in zones:
            zone_id = zone['id']
            dns_records = cf.zones.dns_records.get(zone_id)
            for dns_record in dns_records:
                if dns_record['type'] == 'A' and dns_record['name'] == zone['name']:
                    item = QListWidgetItem(dns_record['name'])
                    checkbox = QCheckBox()
                    checkbox.setText(dns_record['name'])
                    self.domain_list.addItem(item)
                    self.domain_list.setItemWidget(item, checkbox)
            self.update_domains_button.setEnabled(True)

    def set_api_key(self):
        api_key, ok = QInputDialog.getText(self, "API Key", "Enter your API Key:")
        if ok:
            self.api_key = api_key
            self.update_list_button.setEnabled(True)  # Enable the button once the API key is entered

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MyApp()
    window.show()

    sys.exit(app.exec_())
