from os import path
from PyQt5.QtWidgets import QWidget, QMessageBox, QHeaderView
from PyQt5 import uic
from PyQt5.QtGui import QStandardItemModel, QStandardItem

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

    def set_blank(self):
        self.set_headers(['Results'])
        self.set_rows([{'value': 'No Results'}])

    def clear_rows(self):
        self.model.removeRows(0, self.model.rowCount())

    def clear_headers(self):
        self.model.setHorizontalHeaderLabels([])

    def set_rows(self, rows):
        for row in rows:
            items = []
            for item in row.values():
                if isinstance(item, int):
                    items.append(QStandardItem(str(item)))
                else:
                    items.append(QStandardItem(item))
            self.model.insertRow(0, items)

    def display(self):
        self.ResultsTable.setModel(self.model)
