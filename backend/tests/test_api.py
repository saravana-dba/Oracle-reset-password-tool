from unittest.mock import patch


RESET_ENDPOINT = "/reset-password"
VERIFY_ENDPOINT = "/verify-credentials"

VALID_RESET_BODY = {
    "username": "scott",
    "current_password": "tiger",
    "new_password": "newpass123",
    "verification_token": "token-123",
}


class TestResetPasswordEndpoint:
    def test_success(self, client, mock_oracle_success, mock_consume_verification_token):
        res = client.post(RESET_ENDPOINT, json=VALID_RESET_BODY)
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["message"] == "Password changed successfully."
        mock_consume_verification_token.assert_called_once_with("token-123", "scott")

    def test_oracle_error_returns_200_with_failure(self, client, mock_oracle_error, mock_consume_verification_token):
        with mock_oracle_error(1017):
            res = client.post(RESET_ENDPOINT, json=VALID_RESET_BODY)
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is False
        assert "Invalid username" in data["message"]

    def test_invalid_token_returns_200_with_failure(self, client, mock_oracle_success):
        with patch(
            "app.main.verification_store.consume_token",
            side_effect=ValueError("Verification expired. Please verify credentials again."),
        ):
            res = client.post(RESET_ENDPOINT, json=VALID_RESET_BODY)
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is False
        assert "Verification expired" in data["message"]

    def test_missing_username_returns_422(self, client):
        body = {**VALID_RESET_BODY}
        del body["username"]
        res = client.post(RESET_ENDPOINT, json=body)
        assert res.status_code == 422

    def test_empty_username_returns_422(self, client):
        body = {**VALID_RESET_BODY, "username": ""}
        res = client.post(RESET_ENDPOINT, json=body)
        assert res.status_code == 422

    def test_short_new_password_returns_422(self, client):
        body = {**VALID_RESET_BODY, "new_password": "short"}
        res = client.post(RESET_ENDPOINT, json=body)
        assert res.status_code == 422

    def test_missing_verification_token_returns_422(self, client):
        body = {**VALID_RESET_BODY}
        del body["verification_token"]
        res = client.post(RESET_ENDPOINT, json=body)
        assert res.status_code == 422

    def test_empty_verification_token_returns_422(self, client):
        body = {**VALID_RESET_BODY, "verification_token": ""}
        res = client.post(RESET_ENDPOINT, json=body)
        assert res.status_code == 422

    def test_empty_body_returns_422(self, client):
        res = client.post(RESET_ENDPOINT, json={})
        assert res.status_code == 422

    def test_wrong_http_method(self, client):
        res = client.get(RESET_ENDPOINT)
        assert res.status_code == 405


class TestVerifyCredentialsEndpoint:
    def test_success(self, client, mock_oracle_success, mock_create_verification_token):
        res = client.post(
            VERIFY_ENDPOINT,
            json={"username": "scott", "current_password": "tiger"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["message"] == "Credentials verified."
        assert data["verification_token"] == "token-123"
        mock_create_verification_token.assert_called_once_with("scott")

    def test_oracle_error_returns_200_with_failure(self, client, mock_oracle_error):
        with mock_oracle_error(1017):
            res = client.post(
                VERIFY_ENDPOINT,
                json={"username": "scott", "current_password": "wrongpw"},
            )
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is False
        assert "Invalid username" in data["message"]

    def test_missing_username_returns_422(self, client):
        res = client.post(
            VERIFY_ENDPOINT,
            json={"current_password": "tiger"},
        )
        assert res.status_code == 422

    def test_empty_username_returns_422(self, client):
        res = client.post(
            VERIFY_ENDPOINT,
            json={"username": "", "current_password": "tiger"},
        )
        assert res.status_code == 422

    def test_missing_current_password_returns_422(self, client):
        res = client.post(
            VERIFY_ENDPOINT,
            json={"username": "scott"},
        )
        assert res.status_code == 422

    def test_empty_current_password_returns_422(self, client):
        res = client.post(
            VERIFY_ENDPOINT,
            json={"username": "scott", "current_password": ""},
        )
        assert res.status_code == 422
