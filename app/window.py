from os import path
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import Qt
from connection_widget import ConnectionWidget
from main_layout import MainWidget

script_dir = path.dirname(__file__)
ui_file = path.join(script_dir, "views/MainWindow.ui")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Sample App"
        self.server = None
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.left = 10
        self.top = 10
        self.width = 900
        self.height = 640
        self.init_ui()

    def closeEvent(self, evt):
        if self.server is not None:
            self.server.close()

    def init_ui(self):
        uic.loadUi(ui_file, self)
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        connection_view = ConnectionWidget()
        connection_view.connected.connect(self.established_connection)
        self.setCentralWidget(connection_view)

    def established_connection(self, connection, connection_details, server):
        self.server = server
        main_view = MainWidget(connection, connection_details)
        self.setCentralWidget(main_view)
