import datetime
import json
from os import path
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5 import uic
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt5.QtCore import Qt, QVariant, QDateTime, QDate, QJsonValue

script_dir = path.dirname(__file__)
ui_file = path.join(script_dir, "views/ResultsTable.ui")


class ResultsTable(QWidget):
    def __init__(self, connection_helper):
        super().__init__()
        self.connection_helper = connection_helper
        self.model = QStandardItemModel()
        self.model.itemChanged.connect(self.edit_cell)

        self.init_ui()

    def init_ui(self):
        uic.loadUi(ui_file, self)
        self.ResultsTable.setSortingEnabled(True)
        self.ResultsTable.sortByColumn(0, Qt.AscendingOrder)

    def edit_cell(self, item):
        column = item.column()
        row = item.row()
        row_values = [self.model.item(row, column).text() for column in range(self.model.columnCount())]
        column_value = self.model.horizontalHeaderItem(column).text()
        value = item.data(Qt.EditRole)

        result = self.connection_helper.update_query(None, column, column_value, row, value, row_values)
        print(result)

    def set_headers(self, headers):
        self.headers = headers
        for idx, header in enumerate(headers):
            self.model.setHorizontalHeaderItem(idx, QStandardItem(header))

    def set_blank(self):
        self.set_headers(['Results'])
        self.set_rows([{'value': 'No Results'}])

    def clear(self):
        self.model.clear()

    def set_rows(self, rows):
        for idx, row in enumerate(rows):
            items = []
            for column, item in row.items():
                standard_item = QStandardItem()

                if item is None:
                    font = QFont()
                    font.setItalic(True)
                    font.setBold(True)
                    standard_item.setData(QVariant("NULL"), Qt.EditRole)
                    standard_item.setFont(font)
                elif isinstance(item, datetime.datetime):
                    standard_item.setData(QDateTime(item), Qt.EditRole)
                elif isinstance(item, datetime.date):
                    standard_item.setData(QDate(item), Qt.EditRole)
                elif isinstance(item, str):
                    if column == 'json_col':
                        standard_item.setData(QJsonValue(item), Qt.EditRole)
                    else:
                        standard_item.setData(QVariant(item), Qt.EditRole)
                else:
                    standard_item.setData(QVariant(item), Qt.EditRole)
                items.append(standard_item)
            self.model.insertRow(idx, items)

    def display(self):
        self.ResultsTable.setModel(self.model)
