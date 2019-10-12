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
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.main_view = None
        self.left = 10
        self.top = 10
        self.width = 900
        self.height = 640
        self.init_ui()

    def closeEvent(self, evt):
        if self.main_view is not None:
            # we are for sure connected
            self.main_view.connection_helper.connection.close()
            if self.main_view.connection_helper.server is not None:
                self.main_view.connection_helper.server.close()

    def init_ui(self):
        uic.loadUi(ui_file, self)
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        connection_view = ConnectionWidget()
        connection_view.connected.connect(self.established_connection)
        self.setCentralWidget(connection_view)

    def established_connection(self, connection_helper):
        self.main_view = MainWidget(connection_helper)
        self.setCentralWidget(self.main_view)
