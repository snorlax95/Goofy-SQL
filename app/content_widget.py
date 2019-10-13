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
        self.table = ResultsTable()
        self.interval = 10
        self.current_interval = 0
        self.results_count = 0
        self.init_ui()
        self.refresh()

    def init_ui(self):
        uic.loadUi(ui_file, self)
        self.RefreshButton.clicked.connect(self.refresh)
        self.BackButton.clicked.connect(self.page_back)
        self.ForwardButton.clicked.connect(self.page_forward)
        self.layout().addWidget(self.table)

    def refresh(self):
        results = self.connection_helper.select_all(self.current_interval, self.current_interval+self.interval)
        if isinstance(results, str):
            QMessageBox.about(self, 'Oops!', f'You have an error: \n {results}')
        else:
            self.results_count = len(results)
            self.table.clear_rows()
            headers = list(results[0].keys())
            self.table.set_headers(headers)
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

    def update_connection(self, connection_helper):
        self.connection_helper = connection_helper
