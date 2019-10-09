from os import path
from PyQt5.QtWidgets import QWidget, QMessageBox, QHeaderView
from PyQt5 import uic
from PyQt5.QtGui import  QStandardItemModel, QStandardItem

script_dir = path.dirname(__file__)
ui_path = "views/ResultsTable.ui"
ui_file = path.join(script_dir, ui_path)


class ResultsTable(QWidget):
    def __init__(self):
        super().__init__()
        self.model = QStandardItemModel()
        self.init_ui()

    def init_ui(self):
        uic.loadUi(ui_file, self)

    def set_headers(self, headers):
        headers.append('')
        self.model.setHorizontalHeaderLabels(headers)

    def set_rows(self, rows):
        print(rows)
        for row in rows:
            self.model.insertRow(0, [QStandardItem(row) for row in list(row.values())])

    def display(self):
        self.ResultsTable.setModel(self.model)