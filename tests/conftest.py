import os
import pytest
from unittest.mock import patch


def pytest_configure():
    os.system('echo conftest')


def pytest_sessionfinish():
    pass


@pytest.fixture()
def run_around_tests():
    pass
