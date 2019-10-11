from os import path
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import Qt
from connection_widget import ConnectionWidget
from main_layout import MainWidget

script_dir = path.dirname(__file__)
ui_path = "views/MainWindow.ui"
ui_file = path.join(script_dir, ui_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Sample App"
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.left = 10
        self.top = 10
        self.width = 900
        self.height = 640
        self.init_ui()

    def init_ui(self):
        uic.loadUi(ui_file, self)
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        connection_view = ConnectionWidget()
        connection_view.isConnected.connect(self.established_connection)
        self.setCentralWidget(connection_view)

    def established_connection(self, connection, connection_details):
        main_view = MainWidget(connection, connection_details)
        self.setCentralWidget(main_view)
