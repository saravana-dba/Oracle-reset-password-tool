import pytest

from app.services.oracle import reset_password, verify_credentials

TEST_DSN = "localhost:1521/testdb"


class TestResetPasswordSuccess:
    def test_returns_success_message(self, mock_oracle_success):
        result = reset_password("scott", "tiger", "newpass123", TEST_DSN)
        assert result == "Password changed successfully."

    def test_calls_connect_with_correct_args(self, mock_oracle_success):
        reset_password("scott", "tiger", "newpass123", TEST_DSN)
        mock_oracle_success.assert_called_once_with(
            user="scott",
            password="tiger",
            dsn=TEST_DSN,
            newpassword="newpass123",
        )

    def test_closes_connection(self, mock_oracle_success):
        reset_password("scott", "tiger", "newpass123", TEST_DSN)
        conn = mock_oracle_success.return_value
        conn.close.assert_called_once()


class TestResetPasswordOraErrors:
    def test_invalid_credentials(self, mock_oracle_error):
        with mock_oracle_error(1017):
            with pytest.raises(ValueError, match="Invalid username or current password"):
                reset_password("scott", "wrongpw", "newpass123", TEST_DSN)

    def test_complexity_not_met(self, mock_oracle_error):
        with mock_oracle_error(28003):
            with pytest.raises(ValueError, match="complexity requirements"):
                reset_password("scott", "tiger", "weak", TEST_DSN)

    def test_password_reuse(self, mock_oracle_error):
        with mock_oracle_error(28007):
            with pytest.raises(ValueError, match="cannot be reused"):
                reset_password("scott", "tiger", "oldpass123", TEST_DSN)

    def test_unknown_error_code(self, mock_oracle_error):
        with mock_oracle_error(99999):
            with pytest.raises(ValueError, match="unexpected database error"):
                reset_password("scott", "tiger", "newpass123", TEST_DSN)


class TestVerifyCredentials:
    def test_returns_success_message(self, mock_oracle_success):
        result = verify_credentials("scott", "tiger", TEST_DSN)
        assert result == "Credentials verified."

    def test_calls_connect_with_correct_args(self, mock_oracle_success):
        verify_credentials("scott", "tiger", TEST_DSN)
        mock_oracle_success.assert_called_once_with(
            user="scott",
            password="tiger",
            dsn=TEST_DSN,
        )

    def test_invalid_credentials(self, mock_oracle_error):
        with mock_oracle_error(1017):
            with pytest.raises(ValueError, match="Invalid username or current password"):
                verify_credentials("scott", "wrongpw", TEST_DSN)
