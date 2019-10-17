from PyQt5 import QtTest
from unittest.mock import patch
from app.main import App


class TestApplication():

    def test_open(self):
        app = App()
        app.new_window()
        assert len(app.windows) == 2
        assert app.windows[1].isVisible() is True
        app.quit()

    @patch('sys.platform')
    def test_open_windows_style(self, mock_sys_platform):
        mock_sys_platform.return_value = 'win32'
        app = App()
        assert len(app.windows) == 1
        app.quit()
