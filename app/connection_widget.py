import pymysql
import json
from sshtunnel import SSHTunnelForwarder, BaseSSHTunnelForwarderError, HandlerSSHTunnelForwarderError
from os import path
from PyQt5.QtWidgets import QWidget, QLabel, QMessageBox
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, QSettings, Qt
from models.connection import ConnectionModel
from dynamic_label import DynamicLabel

script_dir = path.dirname(__file__)
ui_path = "views/ConnectionView.ui"
ui_file = path.join(script_dir, ui_path)


class ConnectionWidget(QWidget):
    isConnected = pyqtSignal(object, object, name="connection")

    def __init__(self):
        super().__init__()
        self.current_connection_details = None
        self.connection = None
        self.saved_connections = []
        self.saved_connection_labels = []
        self.settings = QSettings("goofy-goobers", "goofy-sql")

        self.init_ui()
        self.new_connection()
        self.ConnectionTypeTabs.setCurrentIndex(1)
        self.get_connections()

    def init_ui(self):
        uic.loadUi(ui_file, self)
        self.ConnectionTypeTabs.currentChanged.connect(self.change_connection_type)
        self.NewConnectionButton.clicked.connect(self.new_connection)
        self.ConnectionButton.clicked.connect(self.connect)
        self.ConnectionTestButton.clicked.connect(self.connect_test)
        self.ConnectionSaveButton.clicked.connect(self.save_connection)
        self.SavedConnections.setAlignment(Qt.AlignTop)

    def refresh_saved_connections(self):
        for connection in self.saved_connection_labels:
            connection.setParent(None)

        self.saved_connection_labels = []
        for connection in self.saved_connections:
            label = DynamicLabel(connection['name'])
            label.clicked.connect(self.open_saved_connection)
            self.SavedConnections.addWidget(label)
            self.saved_connection_labels.append(label)

    def delete_connection(self):
        print('deleting connection')

    def save_connection(self):
        self.get_input_values()
        is_already_saved = False
        for idx, connection in enumerate(self.saved_connections):
            if connection['name'] == self.current_connection_details.name:
                is_already_saved = True
                self.saved_connections[idx] = self.current_connection_details.get_details_dict()
        if self.current_connection_details.name == '':
            QMessageBox.about(self, 'Oops!', 'Please enter name before saving')
            return False

        if is_already_saved is False:
            self.saved_connections.append(self.current_connection_details.get_details_dict())
        self.settings.setValue("connections", json.dumps(self.saved_connections))
        self.refresh_saved_connections()

    def get_connections(self):
        connections = self.settings.value("connections")
        if connections is not None:
            self.saved_connections = json.loads(connections)
            self.refresh_saved_connections()

    def connect(self):
        self.get_input_values()
        try:
            if self.current_connection_details.connection_type == 'tcp':
                connection = self.connect_tcp()
            elif self.current_connection_details.connection_type == 'ssh':
                connection = self.connect_ssh()
            self.connection = connection
            self.isConnected.emit(self.connection, self.current_connection_details)
        except (pymysql.MySQLError, pymysql.Warning, pymysql.Error, pymysql.InterfaceError, pymysql.DatabaseError,
                pymysql.DataError, pymysql.OperationalError, pymysql.IntegrityError, pymysql.InternalError,
                pymysql.ProgrammingError, pymysql.NotSupportedError, BaseSSHTunnelForwarderError,
                HandlerSSHTunnelForwarderError) as e:
            QMessageBox.about(self, 'Oops!', 'Got error {!r}, errno is {}'.format(e, e.args[0]))

    def connect_test(self):
        self.get_input_values()
        try:
            if self.current_connection_details.connection_type == 'tcp':
                connection = self.connect_tcp()
            elif self.current_connection_details.connection_type == 'ssh':
                connection = self.connect_ssh()
            connection.close()
            QMessageBox.about(self, 'Success!', "You're connected")
        except (pymysql.MySQLError, pymysql.Warning, pymysql.Error, pymysql.InterfaceError, pymysql.DatabaseError,
                pymysql.DataError, pymysql.OperationalError, pymysql.IntegrityError, pymysql.InternalError,
                pymysql.ProgrammingError, pymysql.NotSupportedError, BaseSSHTunnelForwarderError,
                HandlerSSHTunnelForwarderError) as e:
            QMessageBox.about(self, 'Oops!', 'Got error {!r}, errno is {}'.format(e, e.args[0]))

    def connect_tcp(self):
        connection = pymysql.connect(host=self.current_connection_details.host,
                                     user=self.current_connection_details.username,
                                     password=self.current_connection_details.password,
                                     port=self.current_connection_details.port,
                                     database=self.current_connection_details.database)
        return connection

    def connect_ssh(self):
        host = self.current_connection_details.host \
            if self.current_connection_details.host != self.current_connection_details.ssh_host else '127.0.0.1'
        port = self.current_connection_details.port if self.current_connection_details.port is not None else 3306
        ssh_host = self.current_connection_details.ssh_host
        ssh_user = self.current_connection_details.ssh_user
        ssh_password = self.current_connection_details.ssh_password
        ssh_port = self.current_connection_details.ssh_port \
            if self.current_connection_details.ssh_port is not None else 22

        server = SSHTunnelForwarder((ssh_host, ssh_port),
                                    ssh_password=ssh_password,
                                    ssh_username=ssh_user,
                                    remote_bind_address=(host, port))

        server.start()
        connection = pymysql.connect(host=host,
                                     user=self.current_connection_details.username,
                                     password=self.current_connection_details.password,
                                     port=server.local_bind_port,
                                     database=self.current_connection_details.database)
        return connection

    def change_connection_type(self, i):
        self.get_input_values()
        if i == 0:
            connection_type = 'tcp'
            self.ConnectionFrame.setMaximumSize(400, 400)
        elif i == 1:
            connection_type = 'ssh'
            self.ConnectionFrame.setMaximumSize(400, 500)
        self.current_connection_details.connection_type = connection_type
        self.set_input_values()

    def open_connection(self, saved_connection):
        connection_model = ConnectionModel(saved_connection)
        if saved_connection is None:
            current_index = self.ConnectionTypeTabs.currentIndex()
            if current_index == 0:
                connection_model.connection_type = 'tcp'
            elif current_index == 1:
                connection_model.connection_type = 'ssh'

        self.current_connection_details = connection_model
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

    def new_connection(self):
        self.open_connection(None)

    def open_saved_connection(self, name):
        for connection in self.saved_connection_labels:
            connection.deselect()
            if connection.name == name:
                connection.select()

        for connection in self.saved_connections:
            if connection['name'] == name:
                if connection['connection_type'] == 'tcp':
                    self.ConnectionTypeTabs.setCurrentIndex(0)
                elif connection['connection_type'] == 'ssh':
                    self.ConnectionTypeTabs.setCurrentIndex(1)
                self.open_connection(connection)
