from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe
from threading import Lock


class VerificationTokenError(ValueError):
    """Raised when a verification token is invalid, expired, or mismatched."""


@dataclass(slots=True)
class VerifiedCredential:
    """Credential payload stored against a short-lived verification token."""

    username: str
    current_password: str
    expires_at: datetime


class VerificationTokenStore:
    """In-memory store for short-lived one-time verification tokens."""

    def __init__(self, ttl_seconds: int) -> None:
        """Initialize token storage with a token time-to-live in seconds."""
        self._ttl = timedelta(seconds=ttl_seconds)
        self._tokens: dict[str, VerifiedCredential] = {}
        self._lock = Lock()

    def create_token(self, username: str, current_password: str) -> str:
        """Create and persist a short-lived token for verified user credentials."""
        token = token_urlsafe(32)
        credential = VerifiedCredential(
            username=username,
            current_password=current_password,
            expires_at=datetime.now(UTC) + self._ttl,
        )
        with self._lock:
            self._cleanup_expired_locked()
            self._tokens[token] = credential
        return token

    def consume_token(self, token: str, username: str) -> str:
        """Return password for a valid token and invalidate it in one operation."""
        with self._lock:
            self._cleanup_expired_locked()
            credential = self._tokens.pop(token, None)

        if credential is None:
            raise VerificationTokenError("Verification expired. Please verify credentials again.")
        if credential.username != username:
            raise VerificationTokenError("Verification does not match the provided username.")
        return credential.current_password

    def _cleanup_expired_locked(self) -> None:
        """Delete all expired tokens while lock ownership is held by caller."""
        now = datetime.now(UTC)
        expired_tokens = [
            token
            for token, credential in self._tokens.items()
            if credential.expires_at <= now
        ]
        for token in expired_tokens:
            self._tokens.pop(token, None)
