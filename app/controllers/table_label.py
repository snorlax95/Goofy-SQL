from PyQt5.QtWidgets import QLabel, QSizePolicy
from PyQt5.QtCore import pyqtSignal


class TableLabel(QLabel):
    clicked = pyqtSignal(str, name='name')

    def __init__(self, name):
        super().__init__()
        self.setText(name)
        self.setMargin(5)
        self.name = name

    def mousePressEvent(self, ev):
        self.clicked.emit(self.name)
        self.select()

    def deselect(self):
        self.setStyleSheet("background-color:none;")

    def select(self):
        self.setStyleSheet("background-color:black;")



