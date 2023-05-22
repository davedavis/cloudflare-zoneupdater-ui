from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QLineEdit, QMenuBar, QMenu, QAction, QInputDialog
from CloudFlare import CloudFlare
import requests
import sys


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cloudflare IP Updater")
        self.setGeometry(200, 200, 600, 200)

        # Create buttons
        self.get_ip_button = QPushButton("Get Current IP", self)
        self.get_ip_button.move(20, 20)

        self.update_domains_button = QPushButton("Update All Domains", self)
        self.update_domains_button.move(20, 70)
        self.update_domains_button.setEnabled(False)

        # Create label
        self.ip_label = QLabel(self)
        self.ip_label.move(200, 25)

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
                if dns_record['type'] == 'A':
                    dns_record['content'] = self.current_ip
                    cf.zones.dns_records.put(zone_id, dns_record['id'], data=dns_record)

    def set_api_key(self):
        self.api_key, ok = QInputDialog.getText(self, "Set API Key", "Enter your Cloudflare API Key:")
        if ok:
            # Save the API key for later use
            # You might want to securely store this key instead of just saving it in memory
            self.api_key = self.api_key.strip()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
