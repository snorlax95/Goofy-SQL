import os
import pytest
from unittest.mock import patch
from app.application import App



def pytest_configure():
    os.system('echo conftest')


def pytest_sessionfinish():
    pass


@pytest.fixture
def app():
    app = App()
    return app


@pytest.fixture()
def run_around_tests():
    pass
