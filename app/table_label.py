from PyQt5.QtWidgets import QLabel, QSizePolicy
from PyQt5.QtCore import pyqtSignal


class TableLabel(QLabel):
    clicked = pyqtSignal(str, name='name')

    def __init__(self, name):
        super().__init__()
        self.setObjectName(f'table_{name}')
        self.setText(name)
        self.setMargin(5)
        self.name = name
        self.selected = False

    def mousePressEvent(self, ev):
        self.clicked.emit(self.name)

    def deselect(self):
        self.selected = False
        self.setStyleSheet("background-color:none;")

    def select(self):
        self.selected = True
        self.setStyleSheet("background-color:black;")



