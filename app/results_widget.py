import datetime
from os import path
from PyQt5.QtWidgets import QWidget, QMessageBox, QHeaderView
from PyQt5 import uic
from PyQt5.QtGui import QStandardItemModel, QStandardItem

script_dir = path.dirname(__file__)
ui_file = path.join(script_dir, "views/ResultsTable.ui")


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
        for idx, row in enumerate(rows):
            items = []
            date_format = "%Y-%m-%d %H:%M:%S %Z"
            for item in row.values():
                if isinstance(item, int):
                    items.append(QStandardItem(str(item)))
                elif isinstance(item, datetime.date):
                    items.append(QStandardItem(item.strftime(date_format)))
                elif isinstance(item, datetime.datetime):
                    items.append(QStandardItem(item.strftime(date_format)))
                else:
                    items.append(QStandardItem(item))
            self.model.insertRow(idx, items)

    def display(self):
        self.ResultsTable.setModel(self.model)
