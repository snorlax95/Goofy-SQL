import os
import pytest
from sqlalchemy import create_engine
from unittest.mock import patch


engine = create_engine(os.environ['CONNECTION_STRING'], echo=True)


def mock_verify_email(email):
    return True


def pytest_configure():
    pytest.VERSION_NUMBER = '1.1.1'
    pytest.NAME = 'blahblah'
    os.system('alembic upgrade head')


def pytest_sessionfinish(session, exitstatus):
    tables = engine.table_names()
    conn = engine.connect()
    for table in tables:
        conn.execute(f"DROP TABLE {table}")


@pytest.fixture
def app():
    os.environ['VERSION_NUMBER'] = pytest.VERSION_NUMBER
    os.environ['NAME'] = pytest.NAME
    from app.api.app_server import create_app
    app = create_app('')
    app.debug = True
    return app


@pytest.fixture(autouse=True)
def run_around_tests():
    tables = engine.table_names()
    conn = engine.connect()
    for table in tables:
         conn.execute(f"DELETE FROM {table}")
         conn.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 0")
