from os import path
from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
from PyQt5.QtCore import Qt
from connections.mysql_connection import MySQL
from query_widget import QueryWidget
from table_label import TableLabel

script_dir = path.dirname(__file__)
ui_path = "views/MainLayout.ui"
ui_file = path.join(script_dir, ui_path)


class MainWidget(QWidget):
    def __init__(self, connection, connection_details):
        super().__init__()
        # current_view should be the main widget
        # should have a method for update_table
        # creating a new one should pass in the current table
        self.connection_details = connection_details
        self.connection_helper = MySQL(connection)
        self.selected_database = self.connection_details.database
        self.databases = []
        self.tables = []
        self.current_view = None
        self.init_ui()

    def init_ui(self):
        uic.loadUi(ui_file, self)
        self.set_database_options()
        self.LeftBar.setAlignment(Qt.AlignTop)

        # TopBar buttons
        self.DatabaseRefreshButton.clicked.connect(self.refresh_database_options)
        self.RefreshTables.clicked.connect(self.refresh_tables)
        self.RefreshTables.setEnabled(False)

        self.QueryButton.clicked.connect(self.set_query_view)
        self.QueryButton.setEnabled(False)
        self.InfoButton.clicked.connect(self.set_info_view)
        self.InfoButton.setEnabled(False)
        self.ContentButton.clicked.connect(self.set_content_view)
        self.ContentButton.setEnabled(False)

    def enable_buttons(self):
        self.RefreshTables.setEnabled(True)
        self.QueryButton.setEnabled(True)
        self.InfoButton.setEnabled(True)
        self.ContentButton.setEnabled(True)

    def update_current_view(self):
        if self.current_view is not None:
            self.current_view.update_connection(self.connection_helper)

    def refresh_database_options(self):
        self.DatabaseDropdown.currentIndexChanged.disconnect()
        self.set_database_options()

    def refresh_tables(self):
        tables = self.connection_helper.get_tables()
        for table in self.tables:
            print(table.name)
            self.LeftBar.removeWidget(table)

        self.tables = []
        for table in tables:
            label = TableLabel(table)
            label.clicked.connect(self.select_table)
            self.LeftBar.addWidget(label, 1, Qt.AlignTop)
            self.tables.append(label)
        if self.connection_helper.selected_table is None:
            self.select_table(tables[0])
        else:
            self.select_table(self.connection_helper.selected_table)

    def set_database_options(self):
        # database selection combo box
        databases = self.connection_helper.get_databases()
        self.DatabaseDropdown.clear()
        self.DatabaseDropdown.addItems(databases['common'])
        self.DatabaseDropdown.addItems(databases['unique'])
        self.DatabaseDropdown.currentIndexChanged.connect(self.select_database)

    def select_database(self):
        self.enable_buttons()
        self.connection_details.database = self.DatabaseDropdown.currentText()
        self.connection_helper.select_database(self.connection_details.database)
        self.refresh_tables()
        self.update_current_view()

    def select_table(self, name):
        for table in self.tables:
            table.deselect()
            if table.objectName() == f'table_{name}':
                table.select()
                self.connection_helper.selected_table = name
        self.update_current_view()

    def set_query_view(self):
        self.enable_buttons()
        self.QueryButton.setEnabled(False)
        if self.current_view is not None:
            self.MainLayout.removeWidget(self.current_view)
        widget = QueryWidget(self.connection_helper)
        self.MainFrame.setVisible(False)
        self.current_view = widget
        self.MainLayout.addWidget(widget)

    def set_info_view(self):
        self.enable_buttons()
        self.InfoButton.setEnabled(False)

    def set_content_view(self):
        self.enable_buttons()
        self.ContentButton.setEnabled(False)
