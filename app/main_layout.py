from os import path
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5 import uic
from PyQt5.QtCore import Qt
from query_widget import QueryWidget
from content_widget import ContentWidget
from create_database_widget import CreateDatabaseWidget
from dynamic_label import DynamicLabel

script_dir = path.dirname(__file__)
ui_file = path.join(script_dir, "views/MainLayout.ui")


class MainWidget(QWidget):
    def __init__(self, connection_helper):
        super().__init__()
        self.connection_helper = connection_helper
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
        self.DatabaseCreateButton.clicked.connect(self.create_database)
        self.RefreshTables.clicked.connect(self.refresh_tables)

        self.QueryButton.clicked.connect(self.set_query_view)
        self.InfoButton.clicked.connect(self.set_info_view)
        self.ContentButton.clicked.connect(self.set_content_view)

        self.disable_buttons()

    def enable_buttons(self):
        self.RefreshTables.setEnabled(True)
        self.QueryButton.setEnabled(True)
        self.InfoButton.setEnabled(True)
        self.ContentButton.setEnabled(True)

    def disable_buttons(self):
        self.RefreshTables.setEnabled(False)
        self.QueryButton.setEnabled(False)
        self.InfoButton.setEnabled(False)
        self.ContentButton.setEnabled(False)

    def manage_buttons(self):
        self.disable_buttons()
        if self.connection_helper.selected_database is not None:
            self.RefreshTables.setEnabled(True)
        if self.connection_helper.selected_table is not None:
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
            table.setParent(None)

        self.tables = []
        for table in tables:
            label = DynamicLabel(table)
            label.clicked.connect(self.select_table)
            self.LeftBar.addWidget(label)
            self.tables.append(label)
        if self.connection_helper.selected_table is None:
            if tables:
                self.select_table(tables[0])
            else:
                self.manage_buttons()
        else:
            self.select_table(self.connection_helper.selected_table)
            self.select_table(self.connection_helper.selected_table)

    def set_database_options(self):
        databases = self.connection_helper.get_databases()
        self.DatabaseDropdown.clear()
        self.DatabaseDropdown.addItems(databases['common'])
        self.DatabaseDropdown.addItems(databases['unique'])
        self.DatabaseDropdown.currentIndexChanged.connect(self.select_database)
        if self.connection_helper.selected_database is not None:
            self.DatabaseDropdown.setCurrentText(self.connection_helper.selected_database)
        
    def new_database(self, name):
        self.DatabaseDropdown.addItem(name)
        self.DatabaseDropdown.setCurrentText(name)
        if self.current_view is not None:
            self.current_view.setParent(None)

    def select_database(self):
        self.enable_buttons()
        is_valid = self.connection_helper.select_database(self.DatabaseDropdown.currentText())
        if is_valid:
            self.refresh_tables()
            self.update_current_view()
        else:
            QMessageBox.about(self, 'Oops!', "Error trying to connect to database")

    def select_table(self, name):
        for table in self.tables:
            table.deselect()
            if table.name == name:
                table.select()
                self.connection_helper.selected_table = name
        self.update_current_view()

    def create_database(self):
        if self.connection_helper.selected_database is not None:
            self.enable_buttons()
        if self.current_view is not None:
            self.current_view.setParent(None)
        widget = CreateDatabaseWidget(self.connection_helper)
        widget.created.connect(self.new_database)
        self.current_view = widget
        self.MainFrame.layout().addWidget(widget)

    def set_query_view(self):
        self.enable_buttons()
        self.QueryButton.setEnabled(False)
        if self.current_view is not None:
            self.current_view.setParent(None)
        widget = QueryWidget(self.connection_helper)
        self.current_view = widget
        self.MainFrame.layout().addWidget(widget)

    def set_info_view(self):
        self.enable_buttons()
        self.InfoButton.setEnabled(False)

    def set_content_view(self):
        self.enable_buttons()
        self.ContentButton.setEnabled(False)
        if self.current_view is not None:
            self.current_view.setParent(None)
        widget = ContentWidget(self.connection_helper)
        self.current_view = widget
        self.MainFrame.layout().addWidget(widget)
