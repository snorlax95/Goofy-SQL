from PyQt5.QtWidgets import QMainWindow, QAction, QWidget
from PyQt5 import uic
from controllers.connection import ConnectionController


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Sample App"
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 640
        self.init_ui()
        self.connection = None


    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        uic.loadUi('../app/views/MainWindow.ui', self)
        connection_view = ConnectionController()
        connection_view.isConnected.connect(self.established_connection)
        self.setCentralWidget(connection_view)


    def create_new_window(self):
        print('Creating new Window')

    def established_connection(self, my_connection):
        self.connection = my_connection
        self.connection.close()
        print('We connected boi')
