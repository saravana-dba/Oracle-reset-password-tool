from unittest.mock import patch


ENDPOINT = "/reset-password"

VALID_BODY = {
    "username": "scott",
    "current_password": "tiger",
    "new_password": "newpass123",
}


class TestResetPasswordEndpoint:
    def test_success(self, client, mock_oracle_success):
        res = client.post(ENDPOINT, json=VALID_BODY)
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["message"] == "Password changed successfully."

    def test_oracle_error_returns_200_with_failure(self, client, mock_oracle_error):
        with mock_oracle_error(1017):
            res = client.post(ENDPOINT, json=VALID_BODY)
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is False
        assert "Invalid username" in data["message"]

    def test_missing_username_returns_422(self, client):
        body = {**VALID_BODY}
        del body["username"]
        res = client.post(ENDPOINT, json=body)
        assert res.status_code == 422

    def test_empty_username_returns_422(self, client):
        body = {**VALID_BODY, "username": ""}
        res = client.post(ENDPOINT, json=body)
        assert res.status_code == 422

    def test_short_new_password_returns_422(self, client):
        body = {**VALID_BODY, "new_password": "short"}
        res = client.post(ENDPOINT, json=body)
        assert res.status_code == 422

    def test_empty_body_returns_422(self, client):
        res = client.post(ENDPOINT, json={})
        assert res.status_code == 422

    def test_wrong_http_method(self, client):
        res = client.get(ENDPOINT)
        assert res.status_code == 405
