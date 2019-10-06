from functools import partial
from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
from PyQt5.QtCore import Qt
from controllers.mysql_connection import MySQL
from controllers.table_label import TableLabel


class MainWidget(QWidget):
    def __init__(self, connection, connection_details):
        super().__init__()
        self.connection = connection
        self.connection_details = connection_details
        self.connection_helper = MySQL(self.connection)
        self.selected_database = self.connection_details.database
        self.init_ui()

    def init_ui(self):
        uic.loadUi('../app/views/MainLayout.ui', self)

        # database selection combo box
        databases = self.connection_helper.get_databases()
        self.DatabaseDropdown.addItems(databases['common'])
        self.DatabaseDropdown.addItems(databases['unique'])
        self.DatabaseDropdown.currentIndexChanged.connect(self.select_database)

        # TopBar buttons
        self.QueryButton.clicked.connect(self.set_query_view)
        self.InfoButton.clicked.connect(self.set_info_view)

    def select_database(self):
        self.connection_details.database = self.DatabaseDropdown.currentText()
        self.connection_helper.select_database(self.connection_details.database)
        tables = self.connection_helper.get_tables()
        for table in tables:
            label = TableLabel(table)
            label.clicked.connect(self.select_table)
            self.LeftBar.addWidget(label, 1, Qt.AlignTop)

    def select_table(self, name):
        print(f'table {name}')

    def set_query_view(self):
        print('query')

    def set_info_view(self):
        print('info')
