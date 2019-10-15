import json
from os import path
from PyQt5.QtWidgets import QWidget, QLabel, QMessageBox
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, QSettings, Qt
from connections.mysql_connection import MySQL
from models.connection import ConnectionModel
from dynamic_label import DynamicLabel

script_dir = path.dirname(__file__)
ui_file = path.join(script_dir, "views/ConnectionView.ui")


class ConnectionWidget(QWidget):
    connected = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.current_connection_details = None
        self.connection_helper = MySQL()
        self.saved_connections = {}
        self.saved_connection_labels = {}
        self.settings = QSettings("goofy-goobers", "goofy-sql")

        self.init_ui()
        self.get_connections()
        self.open_connection(None)

    def init_ui(self):
        uic.loadUi(ui_file, self)
        self.ConnectionTypeTabs.currentChanged.connect(self.change_connection_type)
        self.NewConnectionButton.clicked.connect(self.open_new_connection)
        self.ConnectionButton.clicked.connect(self.connect)
        self.ConnectionTestButton.clicked.connect(self.connect_test)
        self.ConnectionSaveButton.clicked.connect(self.save_connection)
        self.SavedConnections.setAlignment(Qt.AlignTop)

    def refresh_saved_connections(self):
        for connection in self.saved_connection_labels:
            connection.setParent(None)

        self.saved_connection_labels = {}
        for connection in self.saved_connections.values():
            label = DynamicLabel(connection['name'])
            label.clicked.connect(self.open_saved_connection)
            self.SavedConnections.addWidget(label)
            self.saved_connection_labels[connection['name']] = label

    def save_connection(self):
        self.get_input_values()
        if self.current_connection_details.name == '':
            QMessageBox.about(self, 'Oops!', 'Please enter name before saving')
            return False

        connection_details = self.current_connection_details.get_details_dict()
        self.saved_connections[self.current_connection_details.name] = connection_details
        self.settings.setValue("connections", json.dumps(self.saved_connections))
        self.refresh_saved_connections()

    def open_new_connection(self):
        self.open_connection(None)

    def open_connection(self, saved_connection):
        self.current_connection_details = ConnectionModel(saved_connection)
        if saved_connection is None:
            if self.ConnectionTypeTabs.currentIndex() == 0:
                self.current_connection_details.connection_type = 'tcp'
            elif self.ConnectionTypeTabs.currentIndex() == 1:
                self.current_connection_details.connection_type = 'ssh'
        self.set_input_values()

    def open_saved_connection(self, name):
        for connection in self.saved_connection_labels.values():
            connection.deselect()

        connection = self.saved_connections[name]
        self.open_connection(connection)
        if connection['connection_type'] == 'tcp':
            self.ConnectionTypeTabs.setCurrentIndex(0)
        elif connection['connection_type'] == 'ssh':
            self.ConnectionTypeTabs.setCurrentIndex(1)

    def get_connections(self):
        connections = self.settings.value("connections")
        if connections is not None:
            self.saved_connections = json.loads(connections)
            self.refresh_saved_connections()
        else:
            self.open_connection(None)
            self.ConnectionTypeTabs.setCurrentIndex(1)

    def connect(self):
        self.get_input_values()
        try:
            if self.current_connection_details.connection_type == 'tcp':
                self.connection_helper.connect_tcp(self.current_connection_details)
            elif self.current_connection_details.connection_type == 'ssh':
                self.connection_helper.connect_ssh(self.current_connection_details)
            self.connection_helper.get_database_options()
            self.connected.emit(self.connection_helper)
        except Exception as e:
            QMessageBox.about(self, 'Oops!', 'Got error {!r}, errno is {}'.format(e, e.args[0]))

    def connect_test(self):
        self.get_input_values()
        try:
            if self.current_connection_details.connection_type == 'tcp':
                self.connection_helper.connect_tcp(self.current_connection_details)
            elif self.current_connection_details.connection_type == 'ssh':
                self.connection_helper.connect_ssh(self.current_connection_details)
                self.connection_helper.server.close()
            self.connection_helper.connection.close()
            QMessageBox.about(self, 'Success!', "You're connected")
        except Exception as e:
            QMessageBox.about(self, 'Oops!', 'Got error {!r}, errno is {}'.format(e, e.args[0]))

    def change_connection_type(self, i):
        self.get_input_values()
        if i == 0:
            self.current_connection_details.connection_type = 'tcp'
            self.ConnectionFrame.setMaximumSize(400, 375)
        elif i == 1:
            self.current_connection_details.connection_type = 'ssh'
            self.ConnectionFrame.setMaximumSize(400, 500)
        self.set_input_values()

    def set_input_values(self):
        if self.current_connection_details.connection_type == 'tcp':
            self.tcp_name.setText(self.current_connection_details.name)
            self.tcp_host.setText(self.current_connection_details.host)
            self.tcp_username.setText(self.current_connection_details.username)
            self.tcp_password.setText(self.current_connection_details.password)
            self.tcp_database.setText(self.current_connection_details.database)
            self.tcp_port.setText(
                str(self.current_connection_details.port)
                if self.current_connection_details.port is not None else '')
        elif self.current_connection_details.connection_type == 'ssh':
            self.ssh_name.setText(self.current_connection_details.name)
            self.ssh_host.setText(self.current_connection_details.host)
            self.ssh_username.setText(self.current_connection_details.username)
            self.ssh_password.setText(self.current_connection_details.password)
            self.ssh_database.setText(self.current_connection_details.database)
            self.ssh_port.setText(
                str(self.current_connection_details.port)
                if self.current_connection_details.port is not None else '')
            self.ssh_ssh_host.setText(self.current_connection_details.ssh_host)
            self.ssh_ssh_user.setText(self.current_connection_details.ssh_user)
            self.ssh_ssh_password.setText(self.current_connection_details.ssh_password)
            self.ssh_ssh_port.setText(
                str(self.current_connection_details.ssh_port)
                if self.current_connection_details.ssh_port is not None else '')

    def get_input_values(self):
        if self.current_connection_details.connection_type == 'tcp':
            self.current_connection_details.name = self.tcp_name.text()
            self.current_connection_details.host = self.tcp_host.text()
            self.current_connection_details.username = self.tcp_username.text()
            self.current_connection_details.password = self.tcp_password.text()
            self.current_connection_details.database = self.tcp_database.text() if self.tcp_database.text() != '' else None
            self.current_connection_details.port = int(self.tcp_port.text()) if self.tcp_port.text() != '' else None
        elif self.current_connection_details.connection_type == 'ssh':
            self.current_connection_details.name = self.ssh_name.text()
            self.current_connection_details.host = self.ssh_host.text()
            self.current_connection_details.username = self.ssh_username.text()
            self.current_connection_details.password = self.ssh_password.text()
            self.current_connection_details.database = self.ssh_database.text() if self.ssh_database.text() != '' else None
            self.current_connection_details.port = int(self.ssh_port.text()) if self.ssh_port.text() != '' else None
            self.current_connection_details.ssh_host = self.ssh_ssh_host.text()
            self.current_connection_details.ssh_user = self.ssh_ssh_user.text()
            self.current_connection_details.ssh_password = self.ssh_ssh_password.text()
            self.current_connection_details.ssh_port = int(
                self.ssh_ssh_port.text()) if self.ssh_ssh_port.text() != '' else None
