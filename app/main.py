import os
import sys
from PyQt5.QtWidgets import QApplication
try:
    from .widgets.window import MainWindow
except ModuleNotFoundError:
    from widgets.window import MainWindow


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

    def new_window(self):
        window = MainWindow()
        window.new_window.connect(self.new_window)
        window.show()
        self.windows.append(window)


if __name__ == '__main__':
    App()
