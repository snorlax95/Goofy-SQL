from functools import partial
from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
from PyQt5.QtCore import Qt
from controllers.mysql_connection import MySQL
from controllers.query_widget import QueryWidget
from controllers.table_label import TableLabel


class MainWidget(QWidget):
    def __init__(self, connection, connection_details):
        super().__init__()
        # current_view should be the main widget
        # should have a method for update_table
        # creating a new one should pass in the current table
        self.connection_details = connection_details
        self.connection_helper = MySQL(connection)
        self.selected_database = self.connection_details.database
        self.selected_table = None
        self.tables = []
        self.current_view = None
        self.init_ui()

    def init_ui(self):
        uic.loadUi('../app/views/MainLayout.ui', self)
        self.set_database_options()

        # TopBar buttons
        self.DatabaseRefreshButton.clicked.connect(self.refresh_database_options)
        self.QueryButton.clicked.connect(self.set_query_view)
        self.InfoButton.clicked.connect(self.set_info_view)

    def refresh_database_options(self):
        self.DatabaseDropdown.currentIndexChanged.disconnect()
        self.set_database_options()

    def set_database_options(self):
        # database selection combo box
        databases = self.connection_helper.get_databases()
        self.DatabaseDropdown.clear()
        self.DatabaseDropdown.addItems(databases['common'])
        self.DatabaseDropdown.addItems(databases['unique'])
        self.DatabaseDropdown.currentIndexChanged.connect(self.select_database)

    def select_database(self):
        self.connection_details.database = self.DatabaseDropdown.currentText()
        self.connection_helper.select_database(self.connection_details.database)
        tables = self.connection_helper.get_tables()
        for table in tables:
            label = TableLabel(table)
            label.clicked.connect(self.select_table)
            self.LeftBar.addWidget(label, 1, Qt.AlignTop)
            self.tables.append(label)
        self.select_table(tables[0])

    def select_table(self, name):
        for table in self.tables:
            table.deselect()
            if table.objectName() == f'table_{name}':
                table.select()
                self.selected_table = name

    def set_query_view(self):
        widget = QueryWidget(self.connection_helper)
        self.MainFrame.setVisible(False)
        self.current_view = widget
        self.MainLayout.addWidget(widget)

    def set_info_view(self):
        print('info')
