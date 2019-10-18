from PyQt5 import QtTest
from unittest.mock import patch
from app.main import App


class TestApplication():
    app = App()

    def test_open(self):
        self.app.new_window()
        assert len(self.app.windows) == 2
        assert self.app.windows[1].isVisible() is True
        self.app.quit()

    @patch('sys.platform')
    def test_open_windows_style(self, mock_sys_platform):
        mock_sys_platform.return_value = 'win32'
        new_app = App()
        assert len(new_app.windows) == 1
        new_app.quit()
