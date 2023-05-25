from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QMainWindow, QLabel, QPushButton, QLineEdit,
                             QProgressBar, QMenuBar, QMenu, QAction,
                             QInputDialog, QListWidget, QListWidgetItem,
                             QCheckBox, QStatusBar)
from CloudFlare import CloudFlare
import requests
import sys
import keyring

from get_current_ip_thread import GetCurrentIpThread
from update_domains_list_thread import UpdateDomainListThread
from update_domains_thread import UpdateDomainsThread


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('dd-cf.png'))
        self.current_ip = None

        self.get_current_ip_thread = GetCurrentIpThread()
        self.get_current_ip_thread.ip_signal.connect(self.ip_received)

        self.setWindowTitle("Cloudflare IP Updater")
        self.setGeometry(200, 200, 500, 640)

        # Create status bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        # Create buttons
        self.get_ip_button = QPushButton("Get Current IP", self)
        self.get_ip_button.move(20, 30)
        self.get_ip_button.resize(200, 30)
        self.get_ip_button.setToolTip('Gets your current IP address')

        self.update_list_button = QPushButton("Get domain/zone list", self)
        self.update_list_button.move(20, 80)
        self.update_list_button.resize(200, 30)
        self.update_list_button.setEnabled(False)
        self.update_list_button.setToolTip('Fetches the list of domains/zones from Cloudflare')

        self.update_domains_button = QPushButton("Update Selected Domains", self)
        self.update_domains_button.move(20, 130)
        self.update_domains_button.resize(200, 30)
        self.update_domains_button.setEnabled(False)
        self.update_domains_button.setToolTip('Updates the IP address for the selected domains/zones')

        self.select_all_button = QPushButton("Select All Domains", self)
        self.select_all_button.move(20, 180)
        self.select_all_button.resize(200, 30)
        self.select_all_button.setEnabled(False)
        self.select_all_button.setToolTip('Selects all domains/zones in the list')

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
        self.set_api_key_action = QAction("Set API token", self)
        self.options_menu.addAction(self.set_api_key_action)
        self.about_action = QAction("About", self)
        self.options_menu.addAction(self.about_action)

        # Connect signals and slots
        self.get_ip_button.clicked.connect(self.get_current_ip)
        self.update_domains_button.clicked.connect(self.update_all_domains)
        self.update_list_button.clicked.connect(self.update_domain_list)
        self.select_all_button.clicked.connect(self.select_all_domains)
        self.set_api_key_action.triggered.connect(self.set_api_key)
        self.about_action.triggered.connect(self.show_about_dialog)

        # Try to retrieve the API key from the keyring
        self.api_key = keyring.get_password("Cloudflare", "API Key")
        if self.api_key is not None:
            self.update_list_button.setEnabled(True)

    def on_domain_list_update_finished(self):
        self.status_bar.showMessage('All zones fetched successfully.')

    def on_domains_update_finished(self):
        self.status_bar.showMessage('Selected zones updated with new IP.')

    def get_current_ip(self):
        self.status_bar.showMessage('Fetching current IP...')
        self.get_current_ip_thread.start()

    def ip_received(self, message):
        if message.startswith('HTTP error occurred:') or message.startswith('An error occurred:'):
            self.status_bar.showMessage(message)
        else:
            self.current_ip = message
            self.ip_label.setText(self.current_ip)
            self.status_bar.showMessage('Current IP fetched successfully.')

    def update_domain_in_list(self, domain, ip):
        for i in range(self.domain_list.count()):
            item = self.domain_list.item(i)
            checkbox = self.domain_list.itemWidget(item)
            if checkbox.text().split(' ')[0] == domain:
                checkbox.setText(f"{domain} ({ip})")

    def update_all_domains(self):
        self.status_bar.showMessage('Updating selected domains...')
        selected_domains = []
        for i in range(self.domain_list.count()):
            item = self.domain_list.item(i)
            checkbox = self.domain_list.itemWidget(item)
            if checkbox.isChecked():
                selected_domains.append(checkbox.text().split(' ')[0])
        self.update_domains_thread = UpdateDomainsThread(self.api_key, self.current_ip, selected_domains)
        self.update_domains_thread.progress_signal.connect(self.progress_bar.setValue)
        self.update_domains_thread.update_signal.connect(self.update_domain_in_list)
        self.update_domains_thread.finished.connect(self.on_domains_update_finished)
        self.update_domains_thread.start()

    def update_domain_list(self):
        self.status_bar.showMessage('Fetching domain list...')
        self.domain_list.clear()
        self.update_domain_list_thread = UpdateDomainListThread(self.api_key)
        self.update_domain_list_thread.progress_signal.connect(self.progress_bar.setValue)
        self.update_domain_list_thread.data_signal.connect(self.add_to_domain_list)
        self.update_domain_list_thread.finished.connect(self.on_domain_list_update_finished)
        self.update_domain_list_thread.start()

    def add_to_domain_list(self, dns_record):
        checkbox = QCheckBox(dns_record['name'] + ' (' + dns_record['content'] + ')', self)
        list_item = QListWidgetItem(self.domain_list)
        list_item.setSizeHint(checkbox.sizeHint())
        self.domain_list.addItem(list_item)
        self.domain_list.setItemWidget(list_item, checkbox)

    def on_domain_list_update_finished(self):
        self.status_bar.showMessage('All zones fetched successfully.')
        if self.current_ip is not None:
            self.update_domains_button.setEnabled(True)
            self.select_all_button.setEnabled(True)

    def on_update_finished(self):
        if self.current_ip is not None:
            self.update_domains_button.setEnabled(True)
            self.select_all_button.setEnabled(True)
        else:
            self.get_current_ip()
            # Enable the buttons when the update is finished
            self.update_domains_button.setEnabled(True)
            self.select_all_button.setEnabled(True)






    def select_all_domains(self):
        for i in range(self.domain_list.count()):
            item = self.domain_list.item(i)
            checkbox = self.domain_list.itemWidget(item)
            checkbox.setChecked(True)

    def set_api_key(self):
        self.api_key, ok = QInputDialog.getText(self, "Set API Key", "Enter your Cloudflare API Key:")
        if ok:
            self.api_key = self.api_key.strip()
            # Save the API key for later use using keyring
            keyring.set_password("Cloudflare", "API Key", self.api_key)
            self.update_list_button.setEnabled(True)

    def show_about_dialog(self):
        about_dialog = QtWidgets.QDialog(self)
        about_dialog.setWindowTitle("About")

        layout = QtWidgets.QVBoxLayout()

        copyright_label = QLabel()
        copyright_label.setText("Copyright 2023 Dave Davis")
        layout.addWidget(copyright_label)

        website_label = QLabel()
        website_label.setText('<a href="https://www.davedavis.io">https://www.davedavis.io</a>')
        website_label.setTextFormat(QtCore.Qt.RichText)
        website_label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        website_label.setOpenExternalLinks(True)
        layout.addWidget(website_label)

        license_label = QLabel()
        license_label.setText(
            "This work is licensed under a Creative Commons Attribution 4.0 International License.\n "
            "You are free to do what you like with this software as long as attribution is provided.")
        layout.addWidget(license_label)

        about_dialog.setLayout(layout)

        about_dialog.exec_()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())