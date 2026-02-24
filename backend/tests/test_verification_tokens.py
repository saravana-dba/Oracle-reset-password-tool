import pytest

from app.services.verification_tokens import VerificationTokenError, VerificationTokenStore


class TestVerificationTokenStore:
    def test_token_can_be_used_once(self):
        store = VerificationTokenStore(ttl_seconds=300)
        token = store.create_token("scott", "avis")

        store.consume_token(token, "scott", "avis")

        with pytest.raises(VerificationTokenError, match="Verification expired"):
            store.consume_token(token, "scott", "avis")

    def test_token_rejected_for_wrong_brand(self):
        store = VerificationTokenStore(ttl_seconds=300)
        token = store.create_token("scott", "avis")

        with pytest.raises(VerificationTokenError, match="provided brand"):
            store.consume_token(token, "scott", "budget")

    def test_token_rejected_for_wrong_username(self):
        store = VerificationTokenStore(ttl_seconds=300)
        token = store.create_token("scott", "avis")

        with pytest.raises(VerificationTokenError, match="provided username"):
            store.consume_token(token, "other_user", "avis")
