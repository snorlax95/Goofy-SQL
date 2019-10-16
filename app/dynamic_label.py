from PyQt5.QtWidgets import QLabel, QSizePolicy, QMenu, QAction
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont, QIcon, QCursor


class DynamicLabel(QLabel):
    clicked = pyqtSignal(str)
    deleted = pyqtSignal(str)

    def __init__(self, name):
        super().__init__()
        self.setText(name)
        self.setMargin(3)
        self.name = name
        self.menu = QMenu(self)
        self.selected = False
        self.setSizePolicy(QSizePolicy.Minimum,
                           QSizePolicy.Minimum)
        self.setMinimumHeight(22)
        self.setMaximumHeight(22)
        font = QFont()
        font.setPointSize(12)
        self.setFont(font)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu)

        self.menu.setStyleSheet("background-color: white; color:black;")

    def context_menu(self, point):
        delete_action = QAction('Delete')
        delete_action.triggered.connect(self.delete_item)
        self.menu.addAction(delete_action)
        self.menu.exec_(self.mapToGlobal(point))

    def delete_item(self):
        self.deleted.emit(self.name)

    def mousePressEvent(self, ev):
        self.clicked.emit(self.name)
        self.select()

    def deselect(self):
        self.selected = False
        self.setStyleSheet("background-color: none; color:none;")

    def select(self):
        self.selected = True
        self.setStyleSheet("background-color: rgb(0, 122, 255); color:white;")
