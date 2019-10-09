from os import path
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5 import uic

script_dir = path.dirname(__file__)
ui_path = "views/CreateDatabaseView.ui"
ui_file = path.join(script_dir, ui_path)


class CreateDatabaseWidget(QWidget):
    def __init__(self, connection_helper):
        super().__init__()
        self.connection_helper = connection_helper
        self.init_ui()

    def init_ui(self):
        uic.loadUi(ui_file, self)
        self.CreateDatabaseButton.clicked.connect(self.create_database)
        self.DatabaseName.setFocus()

    def create_database(self):
        name = self.DatabaseName.text()
        encoding = self.DatabaseEncoding.currentText()
        collation = self.DatabaseCollation.currentText()
        if name == '':
            print('gotta enter a name bro')
        created = self.connection_helper.create_database(name, encoding, collation)
        if isinstance(created, str):
            QMessageBox.about(self, 'Oops!', f'You have an error: \n {created}')
        else:
            print('created')

    def update_connection(self, connection_helper):
        self.connection_helper = connection_helper
