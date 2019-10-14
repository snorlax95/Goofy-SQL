from os import path
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal

script_dir = path.dirname(__file__)
ui_path = "views/CreateTableView.ui"
ui_file = path.join(script_dir, ui_path)


class CreateTableWidget(QWidget):
    created = pyqtSignal(str)

    def __init__(self, connection_helper):
        super().__init__()
        self.connection_helper = connection_helper
        self.init_ui()

    def init_ui(self):
        # assumes we have a connection
        uic.loadUi(ui_file, self)
        self.CreateTableButton.clicked.connect(self.create_table)
        self.TableName.setFocus()

        self.TableType.clear()
        self.TableType.addItems(self.connection_helper.engines)
        self.TableType.setCurrentText(self.connection_helper.default_engine)

        charset_collation = self.connection_helper.charset_collation
        self.TableEncoding.clear()
        self.TableEncoding.addItems(charset_collation.keys())
        self.TableEncoding.setCurrentText(self.connection_helper.default_charset)
        self.TableEncoding.currentIndexChanged.connect(self.set_collation_options)
        self.set_collation_options()

    def set_collation_options(self):
        charset = self.TableEncoding.currentText()
        charset_collation = self.connection_helper.charset_collation
        self.TableCollation.clear()
        self.TableCollation.addItems(charset_collation[charset]['collations'])
        self.TableCollation.setCurrentText(charset_collation[charset]['default'])

    def create_table(self):
        name = self.TableName.text()
        encoding = self.TableEncoding.currentText()
        collation = self.TableCollation.currentText()
        engine = self.TableType.currentText()
        if name == '' or name is None:
           QMessageBox.about(self, 'Oops!', "Please enter a name")
        elif encoding == '' or encoding is None:
            QMessageBox.about(self, 'Oops!', "Please select an encoding option")
        elif collation == '' or collation is None:
            QMessageBox.about(self, 'Oops!', "Please select a collation option")
        elif engine == '' or engine is None:
            QMessageBox.about(self, 'Oops!', "Please select an engine option")
        else:
            created = self.connection_helper.create_table(name, encoding, collation, engine)
            if isinstance(created, str):
                QMessageBox.about(self, 'Oops!', f'You have an error: \n {created}')
            else:
                QMessageBox.about(self, 'Success!', f'Table {name} has been created')
                self.created.emit(name)

    def update_connection(self, connection_helper):
        self.connection_helper = connection_helper
