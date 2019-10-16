from os import path
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5 import uic
from results_widget import ResultsTable

script_dir = path.dirname(__file__)
ui_path = "views/ContentView.ui"
ui_file = path.join(script_dir, ui_path)


class ContentWidget(QWidget):
    def __init__(self, connection_helper):
        super().__init__()
        self.connection_helper = connection_helper
        self.table = ResultsTable(self.connection_helper)
        self.current_table = self.connection_helper.selected_table
        self.interval = 100
        self.current_interval = 0
        self.results_count = 0
        self.total_count = 0
        self.init_ui()
        self.refresh()

    def init_ui(self):
        uic.loadUi(ui_file, self)
        self.RefreshButton.clicked.connect(self.refresh)
        self.BackButton.clicked.connect(self.page_back)
        self.ForwardButton.clicked.connect(self.page_forward)
        self.layout().addWidget(self.table)

    def set_results_text(self):
        if self.total_count <= self.interval:
            # only one page of results
            text = f"{self.total_count} rows"
        else:
            if (self.current_interval + self.interval) >= self.total_count:
                text = f"{self.current_interval + 1} - {self.total_count} of {self.total_count} rows"
            else:
                text = f"{self.current_interval + 1} - {self.current_interval + self.interval} of {self.total_count} rows"
        self.ResultsText.setText(text)

    def refresh(self):
        results = self.connection_helper.select_all(self.current_interval, self.interval)
        count = self.connection_helper.select_total_count()
        schema = self.connection_helper.get_table_schema()

        if isinstance(count, str):
            QMessageBox.about(self, 'Oops!', f'You have an error: \n {count}')
        elif isinstance(schema, str):
            QMessageBox.about(self, 'Oops!', f'You have an error: \n {schema}')
        elif isinstance(results, str):
            QMessageBox.about(self, 'Oops!', f'You have an error: \n {results}')
        else:
            self.total_count = count
            self.set_results_text()
            self.results_count = len(results)
            self.table.clear()
            self.table.set_headers([header['Field'] for header in schema])
            self.table.set_schema(schema)
            self.table.set_rows(results)
            self.table.display()
            self.manage_buttons()

    def manage_buttons(self):
        if self.current_interval == 0:
            self.BackButton.setEnabled(False)
        else:
            self.BackButton.setEnabled(True)

        if self.results_count == self.interval:
            self.ForwardButton.setEnabled(True)
        else:
            self.ForwardButton.setEnabled(False)

    def page_back(self):
        self.current_interval -= self.interval
        self.refresh()

    def page_forward(self):
        self.current_interval += self.interval
        self.refresh()

    def update(self):
        if self.current_table != self.connection_helper.selected_table:
            self.current_interval = 0
        self.refresh()
