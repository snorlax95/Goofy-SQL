from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
from PyQt5.QtGui import QStandardItemModel, QStandardItem


class QueryWidget(QWidget):
    def __init__(self, connection_helper):
        super().__init__()
        self.connection_helper = connection_helper
        self.query = None
        self.init_ui()

    def init_ui(self):
        uic.loadUi('../app/views/QueryView.ui', self)
        self.RunQueryButton.clicked.connect(self.run_query)

    def run_query(self):
        self.query = self.QueryEdit.toPlainText()
        results = self.connection_helper.custom_query(self.query)
        headers = list(results[0].keys())

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)
        for result in results:
            model.insertRow(0, [QStandardItem(item) for item in list(result.values())])
        self.QueryResultsTable.setModel(model)

    def update_connection(self, connection_helper):
        self.connection_helper = connection_helper
