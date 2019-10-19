from os import path
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5 import uic
from .results_widget import ResultsTable

script_dir = path.dirname(__file__)
ui_path = "views/QueryView.ui"
ui_file = path.join(script_dir, ui_path)


class QueryWidget(QWidget):
    def __init__(self, connection_helper):
        super().__init__()
        self.connection_helper = connection_helper
        self.query = None
        self.table = ResultsTable(self.connection_helper)
        self.init_ui()

    def init_ui(self):
        uic.loadUi(ui_file, self)
        self.RunQueryButton.clicked.connect(self.run_query)
        self.QueryEdit.setFocus()
        self.layout().addWidget(self.table)

    def run_query(self):
        self.query = self.QueryEdit.toPlainText()
        results = self.connection_helper.custom_query(self.query)
        if isinstance(results, str):
            QMessageBox.about(self, 'Oops!', f'You have an error: \n {results}')
        else:
            self.table.clear()
            if self.query[:6] != 'SELECT':
                self.ResultsLabel.setText(f'Affected {results} rows')
                self.table.clear()
                self.table.display()
            else:
                # TODO: get table from selection to get proper schema
                # TODO: Figure out how to handle JOINS, as it wont be as simple as just getting the schema
                self.table.clear()
                table = 'testing'
                schema = self.connection_helper.get_simplified_schema(table, None)
                self.ResultsLabel.setText(f"{len(results)} results")
                self.table.set_headers(results)
                self.table.set_rows(results, schema)
                self.table.display()

    def update(self):
        pass
