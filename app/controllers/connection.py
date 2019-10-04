import pymysql
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal
from models.connection import ConnectionModel


class ConnectionController(QWidget):
    isConnected = pyqtSignal(object, name="connection")

    def __init__(self):
        super().__init__()
        self.current_connection_details = None
        self.connection = None
        self.saved_connections = []

        self.init_ui()
        self.new_connection()
        self.ConnectionTypeTabs.setCurrentIndex(0)

    def init_ui(self):
        uic.loadUi('../app/views/ConnectionView.ui', self)
        self.ConnectionTypeTabs.currentChanged.connect(self.change_connection_type)
        self.NewConnectionButton.clicked.connect(self.new_connection)
        self.ConnectionButton.clicked.connect(self.connect)
        self.ConnectionTestButton.clicked.connect(self.connect_test)
        self.ConnectionSaveButton.clicked.connect(self.save_connection)

    def save_connection(self):
        # take current connection details, convert to dict
        # save to whereever we save those dicts
        # add_connection_to_side with the dict (check if it's already added possibly)?? just update
        # if it's already saved
        print('saving')

    def connect(self):
        self.get_input_values()
        try:
            self.connection = pymysql.connect(host=self.current_connection_details.host,
                                              user=self.current_connection_details.username,
                                              password=self.current_connection_details.password,
                                              port=self.current_connection_details.port)
            self.isConnected.emit(self.connection)
        except:
            print('cannot connect')

    def connect_test(self):
        self.get_input_values()
        try:
            self.connection = pymysql.connect(host=self.current_connection_details.host,
                                          user=self.current_connection_details.username,
                                          password=self.current_connection_details.password,
                                          port=self.current_connection_details.port)
            print('connected')
            self.connection.close()
        except:
            print('cannot connect')

    def add_connection_to_side(self, saved_connection):
        connection_item = QLabel()
        connection_item.setText(saved_connection['name'])
        self.SavedConnections.addWidget(connection_item, 1, Qt.AlignTop)

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

    def open_saved_connection(self, saved_connection):
        connection_model = ConnectionModel(saved_connection)
        self.current_connection_details = connection_model
        self.set_input_values()

    def set_input_values(self):
        if self.current_connection_details.connection_type == 'tcp':
            self.tcp_name.setText(self.current_connection_details.name)
            self.tcp_host.setText(self.current_connection_details.host)
            self.tcp_username.setText(self.current_connection_details.username)
            self.tcp_password.setText(self.current_connection_details.password)
            self.tcp_database.setText(self.current_connection_details.database)
            self.tcp_port.setText(self.current_connection_details.port)
        elif self.current_connection_details.connection_type == 'ssh':
            self.ssh_name.setText(self.current_connection_details.name)
            self.ssh_host.setText(self.current_connection_details.host)
            self.ssh_username.setText(self.current_connection_details.username)
            self.ssh_password.setText(self.current_connection_details.password)
            self.ssh_database.setText(self.current_connection_details.database)
            self.ssh_port.setText(self.current_connection_details.port)

    def get_input_values(self):
        if self.current_connection_details.connection_type == 'tcp':
            self.current_connection_details.name = self.tcp_name.text()
            self.current_connection_details.host = self.tcp_host.text()
            self.current_connection_details.username = self.tcp_username.text()
            self.current_connection_details.password = self.tcp_password.text()
            self.current_connection_details.database = self.tcp_database.text()
            self.current_connection_details.port = int(self.tcp_port.text()) if self.tcp_port.text() != '' else None
        elif self.current_connection_details.connection_type == 'ssh':
            self.current_connection_details.name = self.ssh_name.text()
            self.current_connection_details.host = self.ssh_host.text()
            self.current_connection_details.username = self.ssh_username.text()
            self.current_connection_details.password = self.ssh_password.text()
            self.current_connection_details.database = self.ssh_database.text()
            self.current_connection_details.port = int(self.ssh_port.text()) if self.ssh_port.text() != '' else None

    def new_connection(self):
        self.open_saved_connection(None)
