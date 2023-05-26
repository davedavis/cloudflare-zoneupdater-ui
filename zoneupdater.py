from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QMainWindow,
    QLabel,
    QPushButton,
    QProgressBar,
    QMenu,
    QAction,
    QInputDialog,
    QListWidget,
    QListWidgetItem,
    QCheckBox,
    QStatusBar,
)
import sys
import keyring

from get_current_ip_thread import GetCurrentIpThread
from update_domains_list_thread import UpdateDomainListThread
from update_domains_thread import UpdateDomainsThread

import qdarktheme


class MyApp(QMainWindow):
    """Main class for the Cloudflare IP Updater application."""

    def __init__(self):
        """
        Initializes the application window and its widgets.
        Tries to retrieve the Cloudflare API key from the keyring.
        """
        super().__init__()

        # Set window properties
        self.setWindowIcon(QIcon("dd-cf.png"))
        self.setWindowTitle("Cloudflare IP Updater")
        self.setGeometry(200, 200, 500, 640)

        self.current_ip = None  # Holds the current IP address when fetched
        self.ip_fetched = False  # Track if IP has been fetched
        self.domain_list_updated = False  # Track if domain list is updated

        # Instantiate thread to get current IP address
        self.get_current_ip_thread = GetCurrentIpThread()
        self.get_current_ip_thread.ip_signal.connect(
            self.ip_received
        )  # Connect signal to slot

        # Create status bar
        self.status_bar = QStatusBar(self)  # Instance of QStatusBar
        self.setStatusBar(self.status_bar)  # Set the status bar for the app

        # Create buttons with their tooltips
        self.get_ip_button = QPushButton(
            "Get Current IP", self
        )  # Button to get current IP address
        self.get_ip_button.move(20, 40)
        self.get_ip_button.resize(200, 30)
        self.get_ip_button.setToolTip("Gets your current IP address")
        # Create label for the current IP address
        self.ip_label = QLabel(self)
        self.ip_label.move(230, 40)

        self.update_list_button = QPushButton(
            "Get domain/zone list", self
        )  # Button to get domain/zone list
        self.update_list_button.move(20, 90)
        self.update_list_button.resize(200, 30)
        self.update_list_button.setEnabled(False)  # Initially disabled
        self.update_list_button.setToolTip(
            "Fetches the list of domains/zones from Cloudflare"
        )

        self.update_domains_button = QPushButton(
            "Update Selected Domains", self
        )  # Button to update selected domains
        self.update_domains_button.move(20, 140)
        self.update_domains_button.resize(200, 30)
        self.update_domains_button.setEnabled(False)  # Initially disabled
        self.update_domains_button.setToolTip("Get current IP to enable")

        self.select_all_button = QPushButton(
            "Select All Domains", self
        )  # Button to select all domains
        self.select_all_button.move(20, 190)
        self.select_all_button.resize(200, 30)
        self.select_all_button.setEnabled(False)  # Initially disabled
        self.select_all_button.setToolTip("Get current IP to enable")

        # Create list widget for the domain list
        self.domain_list = QListWidget(self)  # Instance of QListWidget
        self.domain_list.move(20, 230)
        self.domain_list.resize(460, 350)

        # Create menu bar with options
        self.menu_bar = self.menuBar()  # Instance of QMenuBar
        self.options_menu = QMenu("Options", self)  # Instance of QMenu
        self.menu_bar.addMenu(self.options_menu)

        # Create progress bar with initial value set to 0
        self.progress_bar = QProgressBar(self)
        self.progress_bar.move(20, 590)
        self.progress_bar.resize(460, 20)
        self.progress_bar.setValue(0)

        # Create actions for the options menu
        self.set_api_key_action = QAction(
            "Set API token", self
        )  # Action to set API token
        self.options_menu.addAction(self.set_api_key_action)
        self.about_action = QAction("About", self)  # Show about dialog
        self.options_menu.addAction(self.about_action)

        # Connect signals and slots for the widgets
        self.get_ip_button.clicked.connect(self.get_current_ip)
        self.update_domains_button.clicked.connect(self.update_all_domains)
        self.update_list_button.clicked.connect(self.update_domain_list)
        self.select_all_button.clicked.connect(self.select_all_domains)
        self.set_api_key_action.triggered.connect(self.set_api_key)
        self.about_action.triggered.connect(self.show_about_dialog)

        # Try to retrieve the API key from the keyring
        self.api_key = keyring.get_password("Cloudflare", "API Key")
        if self.api_key is not None:
            self.update_list_button.setEnabled(
                True
            )  # Enable the update list button if the API key is not None

    def check_enable_buttons(self) -> None:
        """
        Checks if both the IP has been fetched and the domain list has been
        updated. If both conditions are met, enables the "Update Selected
        Domains" and "Select All Domains" buttons. Also updates tooltips
        based on the status.
        """
        if self.ip_fetched and self.domain_list_updated:
            self.update_domains_button.setEnabled(True)
            self.select_all_button.setEnabled(True)
            self.update_domains_button.setToolTip(
                "Updates the IP address for the selected domains/zones"
            )
            self.select_all_button.setToolTip("Selects all zones in the list")
        elif self.ip_fetched and not self.domain_list_updated:
            self.update_domains_button.setToolTip(
                "Please get your list of domains/zones to enable"
            )
            self.select_all_button.setToolTip(
                "Please get your list of domains/zones to enable"
            )
        else:
            self.update_domains_button.setToolTip("Get current IP to enable")
            self.select_all_button.setToolTip("Get current IP to enable")

    def on_domain_list_update_finished(self) -> None:
        """
        Handles the end of the domain list update process.
        Updates the status bar with a success message.
        """
        self.status_bar.showMessage("All zones fetched successfully.")
        self.domain_list_updated = True  # Set the flag to True
        self.check_enable_buttons()  # Check if the buttons should be enabled

    def on_domains_update_finished(self) -> None:
        """
        Handles the end of the domain update process.
        Updates the status bar with a success message.
        """
        self.status_bar.showMessage("Selected zones updated with new IP.")

    def get_current_ip(self) -> None:
        """Initiates the process of retrieving the current IP address."""
        self.current_ip_thread = GetCurrentIpThread()
        self.current_ip_thread.ip_signal.connect(self.ip_received)
        self.current_ip_thread.start()
        self.status_bar.showMessage("Fetching current IP...")

    def ip_received(self, message: str) -> None:
        """
        Handles the receipt of the current IP.

        Args:
            message: The message containing the current IP or an error message.
        """
        if message.startswith("HTTP error occurred:") or message.startswith(
            "An error occurred:"
        ):
            self.status_bar.showMessage(message)
        else:
            self.current_ip = message
            self.ip_label.setText(self.current_ip)
            self.status_bar.showMessage("Current IP fetched successfully.")
            self.ip_fetched = True  # Set the flag to True
            self.check_enable_buttons()  # Check if buttons should be enabled.

    def update_domain_in_list(self, domain: str, ip: str) -> None:
        """
        Updates a specific domain in the domain list with a new IP.

        Args:
            domain: The domain to update.
            ip: The new IP to assign to the domain.
        """
        for i in range(self.domain_list.count()):
            item = self.domain_list.item(i)
            checkbox = self.domain_list.itemWidget(item)
            if checkbox.text().split(" ")[0] == domain:
                checkbox.setText(f"{domain} ({ip})")

    def update_all_domains(self) -> None:
        """
        Initiates the process of updating all selected domains with the
        current IP. Updates the status bar to indicate the progress.
        """
        self.status_bar.showMessage("Updating selected domains...")
        selected_domains = []
        for i in range(self.domain_list.count()):
            item = self.domain_list.item(i)
            checkbox = self.domain_list.itemWidget(item)
            if checkbox.isChecked():
                selected_domains.append(checkbox.text().split(" ")[0])
        self.update_domains_thread = UpdateDomainsThread(
            self.api_key, self.current_ip, selected_domains
        )
        self.update_domains_thread.progress_signal.connect(self.progress_bar.setValue)
        self.update_domains_thread.update_signal.connect(self.update_domain_in_list)
        self.update_domains_thread.finished.connect(self.on_domains_update_finished)
        self.update_domains_thread.start()

    def update_domain_list(self) -> None:
        """
        Initiates the process of updating the domain list.
        Updates the status bar to indicate the operation in progress.
        """
        self.status_bar.showMessage("Fetching domain list...")
        self.domain_list.clear()
        self.update_domain_list_thread = UpdateDomainListThread(self.api_key)
        self.update_domain_list_thread.progress_signal.connect(
            self.progress_bar.setValue
        )
        self.update_domain_list_thread.data_signal.connect(self.add_to_domain_list)
        self.update_domain_list_thread.finished.connect(
            self.on_domain_list_update_finished
        )
        self.update_domain_list_thread.start()

    def add_to_domain_list(self, dns_record: dict) -> None:
        """
        Adds a new DNS record to the domain list.

        Args:
            dns_record: The DNS record to add.
        """
        checkbox = QCheckBox(
            dns_record["name"] + " (" + dns_record["content"] + ")", self
        )
        list_item = QListWidgetItem(self.domain_list)
        list_item.setSizeHint(checkbox.sizeHint())
        self.domain_list.addItem(list_item)
        self.domain_list.setItemWidget(list_item, checkbox)

    def on_update_finished(self) -> None:
        """
        Handles the end of the update process. Enables the update domains
        button and fetches the current IP if it is not set.
        """
        if self.current_ip is not None:
            self.update_domains_button.setEnabled(True)
            self.select_all_button.setEnabled(True)
        else:
            self.get_current_ip()
            # Enable the buttons when the update is finished
            self.update_domains_button.setEnabled(True)
            self.select_all_button.setEnabled(True)

    def select_all_domains(self) -> None:
        """
        Selects all domains in the domain list.
        """
        for i in range(self.domain_list.count()):
            item = self.domain_list.item(i)
            checkbox = self.domain_list.itemWidget(item)
            checkbox.setChecked(True)

    def set_api_key(self) -> None:
        """
        Prompts the user to set the Cloudflare API Key. If the user provides
        a key, it is saved for later use and the update list button is enabled.
        """
        self.api_key, ok = QInputDialog.getText(
            self, "Set API Key", "Enter your Cloudflare API Key:"
        )
        if ok:
            self.api_key = self.api_key.strip()
            # Save the API key for later use using keyring
            keyring.set_password("Cloudflare", "API Key", self.api_key)
            self.update_list_button.setEnabled(True)

    def show_about_dialog(self) -> None:
        """
        Shows an "About" dialog with information about me.
        """
        about_dialog = QtWidgets.QDialog(self)
        about_dialog.setWindowTitle("About")

        layout = QtWidgets.QVBoxLayout()

        copyright_label = QLabel()
        copyright_label.setText("Copyright 2023 Dave Davis")
        layout.addWidget(copyright_label)

        website_label = QLabel()
        website_label.setText(
            '<a href="https://www.davedavis.io">https://www.davedavis.io</a>'
        )
        website_label.setTextFormat(QtCore.Qt.RichText)
        website_label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        website_label.setOpenExternalLinks(True)
        layout.addWidget(website_label)

        license_label = QLabel()
        license_label.setText(
            "This work is licensed under a Creative Commons Attribution 4.0 "
            "International License.\n You are free to do what you like with "
            "this software as long as attribution is provided."
        )
        layout.addWidget(license_label)

        about_dialog.setLayout(layout)

        about_dialog.exec_()  # Start the dialog event loop


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # Just giving it a CF feel.
    qdarktheme.setup_theme("auto", custom_colors={"primary": "#F4A15D"})
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
