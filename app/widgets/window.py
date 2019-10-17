from os import path
from PyQt5.QtWidgets import QMainWindow, QAction, QFileDialog, QMessageBox
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal
from .connection_widget import ConnectionWidget
from .main_layout import MainWidget

script_dir = path.dirname(__file__)
ui_file = path.join(script_dir, "views/MainWindow.ui")


class MainWindow(QMainWindow):
    new_window = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.title = "Sample App"
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.main_view = None
        self.left = 10
        self.top = 10
        self.width = 900
        self.height = 640
        self.new_window_action = None
        self.import_sql_action = None
        self.export_sql_action = None
        self.init_ui()
        self.set_menu()

    def closeEvent(self, evt):
        if self.main_view is not None:
            # we are for sure connected
            self.main_view.connection_helper.connection.close()
            if self.main_view.connection_helper.server is not None:
                self.main_view.connection_helper.server.close()

    def init_ui(self):
        uic.loadUi(ui_file, self)
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        connection_view = ConnectionWidget()
        connection_view.connected.connect(self.established_connection)
        self.setCentralWidget(connection_view)

    def set_menu(self):
        top_menu = self.menuBar()
        top_menu.setNativeMenuBar(True)

        self.new_window_action = QAction(QIcon(None), 'New Window', top_menu)
        self.new_window_action.setShortcut('Ctrl+w')
        self.new_window_action.setStatusTip('New Connection Window')
        self.new_window_action.triggered.connect(self.new_window.emit)

        self.import_sql_action = QAction(QIcon(None), 'Import SQL', top_menu)
        self.import_sql_action.setStatusTip('Import SQL')
        self.import_sql_action.triggered.connect(self.import_sql)
        self.import_sql_action.setEnabled(False)

        self.export_sql_action = QAction(QIcon(None), 'Export SQL', top_menu)
        self.export_sql_action.setStatusTip('Export SQL')
        self.export_sql_action.triggered.connect(self.export_sql)
        self.export_sql_action.setEnabled(False)

        file_menu = top_menu.addMenu('File')
        file_menu.addAction(self.new_window_action)
        file_menu.addAction(self.import_sql_action)
        file_menu.addAction(self.export_sql_action)

    def import_sql(self):
        dialog = QFileDialog()
        options = dialog.Options()
        options |= dialog.DontUseNativeDialog
        dialog.setNameFilter("*.sql")
        file_name, _ = dialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                              "SQL Files (*.sql)", options=options)
        if file_name:
            f = open(file_name, 'r')
            sql = f.read()
            f.close()
            sql_commands = sql.split(';')
            for command in sql_commands:
                command.replace("\n", "")
                command.strip()
                if command != '' and command[0] != '#' and '/*' not in command:
                    result = self.main_view.connection_helper.custom_query(command)
                    if isinstance(result, str):
                        # query failed, stop import
                        QMessageBox.about(self, 'Oops!', result)
                        return False

    def export_sql(self):
        print('exporting')

    def established_connection(self, connection_helper):
        self.main_view = MainWidget(connection_helper)
        self.setCentralWidget(self.main_view)
        self.import_sql_action.setEnabled(True)
        self.export_sql_action.setEnabled(True)
