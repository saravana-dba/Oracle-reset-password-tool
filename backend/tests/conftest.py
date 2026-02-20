import os

# Set a dummy DSN so config.py doesn't fail on import.
os.environ.setdefault("ORACLE_DSN", "localhost:1521/testdb")

from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture()
def client():
    """Test client using FastAPI's TestClient (sync wrapper over ASGI)."""
    from starlette.testclient import TestClient

    with TestClient(app) as c:
        yield c


@pytest.fixture()
def mock_oracle_success():
    """Mock oracledb.connect to succeed (password changed)."""
    with patch("app.services.oracle.oracledb.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        yield mock_connect


@pytest.fixture()
def mock_oracle_error():
    """Factory fixture: mock oracledb.connect to raise a DatabaseError with a given ORA code."""
    import oracledb

    def _make(code: int):
        error = MagicMock()
        error.code = code
        exc = oracledb.DatabaseError(error)
        return patch("app.services.oracle.oracledb.connect", side_effect=exc)

    return _make
