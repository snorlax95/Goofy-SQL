import sys
from window import MainWindow
from PyQt5.QtWidgets import QAction, QApplication
from PyQt5.QtGui import QIcon


class App:
    def __init__(self):
        app = QApplication(sys.argv)
        if sys.platform == 'darwin':
            app.setStyle('Macintosh')
        else:
            app.setStyle('Fusion')
        self.windows = []
        self.new_window()
        app.exec_()

    def new_window(self):
        window = MainWindow()
        self.create_menu(window)
        window.show()
        self.windows.append(window)

    def create_menu(self, window):
        top_menu = window.menuBar()
        top_menu.setNativeMenuBar(True)

        new_window = QAction(QIcon(None), 'New Window', top_menu)
        new_window.setShortcut('Ctrl+w')
        new_window.setStatusTip('New Connection Window')
        new_window.triggered.connect(self.new_window)

        file_menu = top_menu.addMenu('File')
        file_menu.addAction(new_window)
