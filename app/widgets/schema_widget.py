from os import path
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5 import uic
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QVariant

script_dir = path.dirname(__file__)
ui_path = "views/SchemaView.ui"
ui_file = path.join(script_dir, ui_path)


class SchemaWidget(QWidget):
    def __init__(self, connection_helper):
        super().__init__()
        self.connection_helper = connection_helper
        self.model = QStandardItemModel()
        self.model.itemChanged.connect(self.edit_cell)
        self.schema = self.connection_helper.get_standardized_schema(None, None)
        self.column_labels = ["Field", "Type", "Unsigned", 
        "Zerofill", "Binary", "Allow Null", "Key", "Default", 
        "Extra", "Encoding", "Collation"]

        # need index form for adding new keys. Not a separate table..just a button
        # need columns resized
        self.init_ui()
        self.refresh()
        
    def init_ui(self):
        uic.loadUi(ui_file, self)
        self.RefreshButton.clicked.connect(self.refresh)
        self.model.setHorizontalHeaderLabels(self.column_labels)
        row_index = 0
        for key, val in self.schema['columns'].items():
            items = []
            # based on the data, display the proper content type / option in rows
            standard_item = QStandardItem()
            standard_item.setData(QVariant(key), Qt.EditRole)
            items.append(standard_item)

            standard_item = QStandardItem()
            standard_item.setData(QVariant(val['Type']), Qt.EditRole)
            items.append(standard_item)

            standard_item = QStandardItem()
            standard_item.setCheckable(True)
            items.append(standard_item)

            standard_item = QStandardItem()
            standard_item.setCheckable(True)
            items.append(standard_item)

            standard_item = QStandardItem()
            standard_item.setCheckable(True)
            items.append(standard_item)

            standard_item = QStandardItem()
            standard_item.setCheckable(True)
            items.append(standard_item)

            standard_item = QStandardItem()
            standard_item.setData(QVariant(val['Key']), Qt.EditRole)
            items.append(standard_item)

            standard_item = QStandardItem()
            standard_item.setData(QVariant(val['Default']), Qt.EditRole)
            items.append(standard_item)

            standard_item = QStandardItem()
            standard_item.setData(QVariant(val['Extra']), Qt.EditRole)
            items.append(standard_item)

            self.model.insertRow(row_index, items)
            row_index += 1

    def edit_cell(self, item):
        column = item.column()
        row = item.row()
        # row_values = [self.model.item(row, column).text() for column in range(self.model.columnCount())]
        column_value = self.model.horizontalHeaderItem(column).text()

        if item.isCheckable():
            value = True if item.checkState() == 2 else False
        else:
            value = item.data(Qt.EditRole)
        # send column name + that rows entire data for edit
        print(value)

    def refresh(self):
        self.SchemaTable.setModel(self.model)

    def manage_buttons(self):
        pass

    def update(self):
        pass
        # self.refresh()
