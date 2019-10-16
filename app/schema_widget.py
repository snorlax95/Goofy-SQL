from os import path
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5 import uic
from results_widget import ResultsTable

script_dir = path.dirname(__file__)
ui_path = "views/SchemaView.ui"
ui_file = path.join(script_dir, ui_path)


class SchemaWidget(QWidget):
    def __init__(self, connection_helper):
        super().__init__()
        self.connection_helper = connection_helper
        self.table = ResultsTable(self.connection_helper)
        self.init_ui()
        self.refresh()

    def init_ui(self):
        uic.loadUi(ui_file, self)
        self.RefreshButton.clicked.connect(self.refresh)
        self.layout().addWidget(self.table)

    def refresh(self):
        pass

    def manage_buttons(self):
        pass

    def update(self):
        self.refresh()
