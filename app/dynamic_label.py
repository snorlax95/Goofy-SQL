from PyQt5.QtWidgets import QLabel, QSizePolicy
from PyQt5.QtCore import pyqtSignal


class DynamicLabel(QLabel):
    clicked = pyqtSignal(str, name='name')

    def __init__(self, name):
        super().__init__()
        self.setText(name)
        self.setMargin(5)
        self.name = name
        self.selected = False

    def mousePressEvent(self, ev):
        self.clicked.emit(self.name)

    def deselect(self):
        self.selected = False
        self.setStyleSheet("color:none;")

    def select(self):
        self.selected = True
        self.setStyleSheet("color:blue;")



