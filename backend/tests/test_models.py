import pytest
from pydantic import ValidationError

from app.models import CredentialCheckRequest, PasswordResetRequest, PasswordResetResponse


class TestPasswordResetRequest:
    def test_valid_request(self):
        req = PasswordResetRequest(
            brand="avis",
            username="scott",
            current_password="tiger",
            new_password="newpass123",
            verification_token="token-123",
        )
        assert req.brand == "avis"
        assert req.username == "scott"
        assert req.current_password == "tiger"
        assert req.new_password == "newpass123"
        assert req.verification_token == "token-123"

    def test_budget_brand_accepted(self):
        req = PasswordResetRequest(
            brand="budget",
            username="scott",
            current_password="tiger",
            new_password="newpass123",
            verification_token="token-123",
        )
        assert req.brand == "budget"

    def test_missing_brand_rejected(self):
        with pytest.raises(ValidationError):
            PasswordResetRequest(
                username="scott", current_password="tiger", new_password="newpass123", verification_token="token-123"
            )

    def test_invalid_brand_rejected(self):
        with pytest.raises(ValidationError):
            PasswordResetRequest(
                brand="hertz",
                username="scott",
                current_password="tiger",
                new_password="newpass123",
                verification_token="token-123",
            )

    def test_empty_username_rejected(self):
        with pytest.raises(ValidationError):
            PasswordResetRequest(
                brand="avis", username="", current_password="tiger", new_password="newpass123", verification_token="token-123"
            )

    def test_empty_current_password_rejected(self):
        with pytest.raises(ValidationError):
            PasswordResetRequest(
                brand="avis", username="scott", current_password="", new_password="newpass123", verification_token="token-123"
            )

    def test_empty_verification_token_rejected(self):
        with pytest.raises(ValidationError):
            PasswordResetRequest(
                brand="avis", username="scott", current_password="tiger", new_password="newpass123", verification_token=""
            )

    def test_short_new_password_rejected(self):
        with pytest.raises(ValidationError):
            PasswordResetRequest(
                brand="avis", username="scott", current_password="tiger", new_password="short", verification_token="token-123"
            )

    def test_exactly_8_char_new_password_accepted(self):
        req = PasswordResetRequest(
            brand="avis",
            username="scott",
            current_password="tiger",
            new_password="12345678",
            verification_token="token-123",
        )
        assert len(req.new_password) == 8

    def test_invalid_username_pattern_rejected(self):
        with pytest.raises(ValidationError):
            PasswordResetRequest(
                brand="avis", username="1scott", current_password="tiger", new_password="newpass123", verification_token="token-123"
            )

    def test_username_with_spaces_rejected(self):
        with pytest.raises(ValidationError):
            PasswordResetRequest(
                brand="avis", username="sc ott", current_password="tiger", new_password="newpass123", verification_token="token-123"
            )

    def test_username_with_special_chars_rejected(self):
        with pytest.raises(ValidationError):
            PasswordResetRequest(
                brand="avis", username="scott;DROP", current_password="tiger", new_password="newpass123", verification_token="token-123"
            )

    def test_username_with_allowed_special_chars_accepted(self):
        req = PasswordResetRequest(
            brand="avis",
            username="SCOTT_$DBA#1",
            current_password="tiger",
            new_password="newpass123",
            verification_token="token-123",
        )
        assert req.username == "SCOTT_$DBA#1"

    def test_username_exceeding_max_length_rejected(self):
        with pytest.raises(ValidationError):
            PasswordResetRequest(
                brand="avis", username="A" * 129, current_password="tiger", new_password="newpass123", verification_token="token-123"
            )


class TestPasswordResetResponse:
    def test_success_response(self):
        res = PasswordResetResponse(success=True, message="Password changed successfully.")
        assert res.success is True

    def test_failure_response(self):
        res = PasswordResetResponse(success=False, message="Invalid username or current password.")
        assert res.success is False


class TestCredentialCheckRequest:
    def test_valid_request(self):
        req = CredentialCheckRequest(brand="avis", username="scott", current_password="tiger")
        assert req.brand == "avis"
        assert req.username == "scott"
        assert req.current_password == "tiger"

    def test_budget_brand_accepted(self):
        req = CredentialCheckRequest(brand="budget", username="scott", current_password="tiger")
        assert req.brand == "budget"

    def test_missing_brand_rejected(self):
        with pytest.raises(ValidationError):
            CredentialCheckRequest(username="scott", current_password="tiger")

    def test_invalid_brand_rejected(self):
        with pytest.raises(ValidationError):
            CredentialCheckRequest(brand="hertz", username="scott", current_password="tiger")

    def test_empty_username_rejected(self):
        with pytest.raises(ValidationError):
            CredentialCheckRequest(brand="avis", username="", current_password="tiger")

    def test_empty_current_password_rejected(self):
        with pytest.raises(ValidationError):
            CredentialCheckRequest(brand="avis", username="scott", current_password="")

    def test_invalid_username_pattern_rejected(self):
        with pytest.raises(ValidationError):
            CredentialCheckRequest(brand="avis", username="1scott", current_password="tiger")

    def test_username_with_special_chars_rejected(self):
        with pytest.raises(ValidationError):
            CredentialCheckRequest(brand="avis", username="scott;DROP", current_password="tiger")

    def test_username_with_allowed_special_chars_accepted(self):
        req = CredentialCheckRequest(brand="avis", username="SCOTT_$DBA#1", current_password="tiger")
        assert req.username == "SCOTT_$DBA#1"
