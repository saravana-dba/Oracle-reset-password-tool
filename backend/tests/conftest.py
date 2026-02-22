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
        mock_conn.__enter__.return_value = mock_conn

        def _exit(exc_type, exc, tb):
            """Mirror context manager behavior by closing the mocked connection."""
            mock_conn.close()
            return False

        mock_conn.__exit__.side_effect = _exit
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


@pytest.fixture()
def mock_create_verification_token():
    """Mock verification token creation for deterministic API tests."""
    with patch("app.main.verification_store.create_token", return_value="token-123") as mock_create:
        yield mock_create


@pytest.fixture()
def mock_consume_verification_token():
    """Mock verification token consumption to avoid state coupling in API tests."""
    with patch("app.main.verification_store.consume_token", return_value="tiger") as mock_consume:
        yield mock_consume
