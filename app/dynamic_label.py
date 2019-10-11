from PyQt5.QtWidgets import QLabel, QSizePolicy
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont


class DynamicLabel(QLabel):
    clicked = pyqtSignal(str, name='name')

    def __init__(self, name):
        super().__init__()
        self.setText(name)
        self.setMargin(5)
        self.name = name
        self.selected = False
        self.setSizePolicy(QSizePolicy.Minimum,
                           QSizePolicy.Minimum)
        self.setMinimumHeight(25)
        self.setMaximumHeight(25)
        font = QFont()
        font.setPointSize(12)
        self.setFont(font)

    def mousePressEvent(self, ev):
        self.clicked.emit(self.name)
        self.select()

    def deselect(self):
        self.selected = False
        self.setStyleSheet("background-color: none; color:none;")

    def select(self):
        self.selected = True
        self.setStyleSheet("background-color: rgb(0, 122, 255); color:white;")



