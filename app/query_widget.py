from os import path
from PyQt5.QtWidgets import QWidget, QStyleOption, QStyle, QMessageBox
from PyQt5 import uic
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QPainter

script_dir = path.dirname(__file__)
ui_path = "views/QueryView.ui"
ui_file = path.join(script_dir, ui_path)


class QueryWidget(QWidget):
    def __init__(self, connection_helper):
        super().__init__()
        self.connection_helper = connection_helper
        self.query = None
        self.init_ui()

    def init_ui(self):
        uic.loadUi(ui_file, self)
        self.RunQueryButton.clicked.connect(self.run_query)
        self.QueryEdit.setFocus()

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

    def run_query(self):
        self.query = self.QueryEdit.toPlainText()
        results = self.connection_helper.custom_query(self.query)
        if isinstance(results, str):
            QMessageBox.about(self, 'Oops!', f'You have an error: \n {results}')
        else:
            headers = list(results[0].keys())

            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(headers)
            for result in results:
                model.insertRow(0, [QStandardItem(item) for item in list(result.values())])
            self.QueryResultsTable.setModel(model)

    def update_connection(self, connection_helper):
        self.connection_helper = connection_helper
