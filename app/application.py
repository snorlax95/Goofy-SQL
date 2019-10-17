import sys
from .widgets.window import MainWindow
from PyQt5.QtWidgets import QApplication


class App(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        if sys.platform == 'darwin':
            self.setStyle('Macintosh')
        else:
            self.setStyle('Fusion')
        self.windows = []
        self.new_window()
        self.exec_()

    def new_window(self, evt=None):
        window = MainWindow()
        window.new_window.connect(self.new_window)
        window.show()
        self.windows.append(window)
