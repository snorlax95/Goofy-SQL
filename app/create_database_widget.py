from os import path
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal

script_dir = path.dirname(__file__)
ui_path = "views/CreateDatabaseView.ui"
ui_file = path.join(script_dir, ui_path)


class CreateDatabaseWidget(QWidget):
    created = pyqtSignal(str)

    def __init__(self, connection_helper):
        super().__init__()
        self.connection_helper = connection_helper
        self.init_ui()

    def init_ui(self):
        # assumes we have a connection
        uic.loadUi(ui_file, self)
        self.CreateDatabaseButton.clicked.connect(self.create_database)
        self.DatabaseName.setFocus()

        charset_collation = self.connection_helper.charset_collation
        self.DatabaseEncoding.clear()
        self.DatabaseEncoding.addItems(charset_collation.keys())
        self.DatabaseEncoding.setCurrentText(self.connection_helper.default_charset)
        self.DatabaseEncoding.currentIndexChanged.connect(self.set_collation_options)
        self.set_collation_options()

    def set_collation_options(self):
        charset = self.DatabaseEncoding.currentText()
        charset_collation = self.connection_helper.charset_collation
        self.DatabaseCollation.clear()
        self.DatabaseCollation.addItems(charset_collation[charset]['collations'])
        self.DatabaseCollation.setCurrentText(charset_collation[charset]['default'])

    def create_database(self):
        name = self.DatabaseName.text()
        encoding = self.DatabaseEncoding.currentText()
        collation = self.DatabaseCollation.currentText()
        if name == '' or name is None:
           QMessageBox.about(self, 'Oops!', "Please enter a name")
        elif encoding == '' or encoding is None:
            QMessageBox.about(self, 'Oops!', "Please select an encoding option")
        elif collation == '' or collation is None:
            QMessageBox.about(self, 'Oops!', "Please select a collation option")
        else:
            created = self.connection_helper.create_database(name, encoding, collation)
            if isinstance(created, str):
                QMessageBox.about(self, 'Oops!', f'You have an error: \n {created}')
            else:
                QMessageBox.about(self, 'Success!', f'Database {name} has been created')
                self.created.emit(name)

    def update_connection(self, connection_helper):
        self.connection_helper = connection_helper
