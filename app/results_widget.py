import datetime
from os import path
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5 import uic
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt5.QtCore import Qt, QVariant
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel

script_dir = path.dirname(__file__)
ui_file = path.join(script_dir, "views/ResultsTable.ui")


class ResultsTable(QWidget):
    def __init__(self, connection_helper):
        super().__init__()
        self.connection_helper = connection_helper
        self.model = QStandardItemModel()
        self.model.itemChanged.connect(self.edit_cell)
        self.table_schema = None

        # self.database = QSqlDatabase("QPSQL")
        # self.database.setHostName('127.0.0.1')
        # self.database.setUserName('root')
        # self.database.setPassword('root')
        # self.database.setPort(5432)
        # self.database.setDatabaseName('pydb')
        # self.database.open()
        # self.sql_model = QSqlTableModel(None, self.database)
        # self.sql_model.setHeaderData(0, Qt.Horizontal, "id")
        # self.sql_model.setTable('testing')
        # print(self.sql_model.selectStatement())
        # self.sql_model.select()
        # print(self.sql_model.selectStatement())
        # print(self.sql_model.lastError().text())
        # print(self.sql_model.rowCount())
        # print(self.sql_model.columnCount())

        self.init_ui()

    def init_ui(self):
        uic.loadUi(ui_file, self)
        self.ResultsTable.setSortingEnabled(True)
        # self.ResultsTable.sortByColumn(0, Qt.AscendingOrder)

    def edit_cell(self, item):
        # if key exists, use that as identifier
        # if key does not exist, use every row as identifier and LIMIT 1
        # get type of columns to convert values accordingly...convert method should be in connection helper
        # revert update command if failed to reset cell and display warning message
        column = item.column()
        row = item.row()
        value = item.data(Qt.EditRole)
        print(value)

        row_values = [self.model.item(row, column).text() for column in range(self.model.columnCount())]
        column_value = self.model.horizontalHeaderItem(column)

    def set_schema(self, table_schema):
        self.table_schema = table_schema

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
            date_format = "%Y-%m-%d %H:%M:%S %Z"
            for item in row.values():
                standard_item = QStandardItem()
                if isinstance(item, datetime.date) or isinstance(item, datetime.datetime):
                    standard_item.setData(QVariant(item.strftime(date_format)), Qt.EditRole)
                    items.append(standard_item)
                elif item is None:
                    font = QFont()
                    font.setItalic(True)
                    font.setBold(True)
                    standard_item.setData(QVariant("NULL"), Qt.EditRole)
                    standard_item.setFont(font)
                    items.append(standard_item)
                else:
                    standard_item.setData(QVariant(item), Qt.EditRole)
                    items.append(standard_item)
            self.model.insertRow(idx, items)

    def display(self):
        self.ResultsTable.setModel(self.sql_model)
        self.ResultsTable.show()
