import sys
from window import MainWindow
from PyQt5.QtWidgets import QAction, QApplication


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

    def new_window(self, evt=None):
        window = MainWindow()
        window.new_window.connect(self.new_window)
        window.show()
        self.windows.append(window)
