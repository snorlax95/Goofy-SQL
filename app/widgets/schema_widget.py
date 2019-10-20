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
        self.column_labels = ["Field", "Type", "Length", "Unsigned", 
        "Zerofill", "Binary", "Allow Null", "Key", "Default", 
        "Extra", "Encoding", "Collation"]

        self.init_ui()
        self.refresh()
        
    def init_ui(self):
        uic.loadUi(ui_file, self)
        self.RefreshButton.clicked.connect(self.refresh)
        self.model.setHorizontalHeaderLabels(self.column_labels)

    def edit_cell(self):
        print('edit')
        # editing item

    def refresh(self):
        self.SchemaTable.setModel(self.model)

    def manage_buttons(self):
        pass

    def update(self):
        pass
        # self.refresh()
