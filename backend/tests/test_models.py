import pytest
from pydantic import ValidationError

from app.models import PasswordResetRequest, PasswordResetResponse


class TestPasswordResetRequest:
    def test_valid_request(self):
        req = PasswordResetRequest(
            username="scott",
            current_password="tiger",
            new_password="newpass123",
        )
        assert req.username == "scott"
        assert req.current_password == "tiger"
        assert req.new_password == "newpass123"

    def test_empty_username_rejected(self):
        with pytest.raises(ValidationError):
            PasswordResetRequest(username="", current_password="old", new_password="newpass123")

    def test_empty_current_password_rejected(self):
        with pytest.raises(ValidationError):
            PasswordResetRequest(username="scott", current_password="", new_password="newpass123")

    def test_short_new_password_rejected(self):
        with pytest.raises(ValidationError):
            PasswordResetRequest(username="scott", current_password="old", new_password="short")

    def test_exactly_8_char_new_password_accepted(self):
        req = PasswordResetRequest(username="scott", current_password="old", new_password="12345678")
        assert len(req.new_password) == 8


class TestPasswordResetResponse:
    def test_success_response(self):
        res = PasswordResetResponse(success=True, message="Password changed successfully.")
        assert res.success is True

    def test_failure_response(self):
        res = PasswordResetResponse(success=False, message="Invalid username or current password.")
        assert res.success is False
