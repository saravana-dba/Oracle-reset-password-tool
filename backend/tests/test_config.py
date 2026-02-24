import pytest
from pydantic import ValidationError

from app.config import Settings


class TestSettings:
    def test_legacy_oracle_dsn_only_is_rejected(self, monkeypatch):
        monkeypatch.delenv("ORACLE_DSN_AVIS", raising=False)
        monkeypatch.delenv("ORACLE_DSN_BUDGET", raising=False)
        monkeypatch.delenv("ORACLE_DSN", raising=False)
        with pytest.raises(ValidationError, match="oracle_dsn_avis"):
            Settings(_env_file=None, oracle_dsn="localhost:1521/legacy")

    def test_explicit_brand_dsns_are_preserved(self, monkeypatch):
        monkeypatch.delenv("ORACLE_DSN_AVIS", raising=False)
        monkeypatch.delenv("ORACLE_DSN_BUDGET", raising=False)
        monkeypatch.delenv("ORACLE_DSN", raising=False)
        settings = Settings(
            _env_file=None,
            oracle_dsn_avis="localhost:1521/avisdb",
            oracle_dsn_budget="localhost:1521/budgetdb",
        )
        assert settings.get_dsn("avis") == "localhost:1521/avisdb"
        assert settings.get_dsn("budget") == "localhost:1521/budgetdb"

    def test_missing_brand_dsn_configuration_is_rejected(self, monkeypatch):
        monkeypatch.delenv("ORACLE_DSN_AVIS", raising=False)
        monkeypatch.delenv("ORACLE_DSN_BUDGET", raising=False)
        monkeypatch.delenv("ORACLE_DSN", raising=False)
        with pytest.raises(ValidationError, match="oracle_dsn_budget"):
            Settings(_env_file=None, oracle_dsn_avis="localhost:1521/avisdb")
