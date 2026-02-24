from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    oracle_dsn_avis: str | None = None
    oracle_dsn_budget: str | None = None
    oracle_dsn: str | None = None
    cors_origins: list[str] = ["*"]

    model_config = {"env_file": ".env", "extra": "ignore"}

    @model_validator(mode="after")
    def apply_legacy_dsn_fallback(self) -> "Settings":
        """Support legacy ORACLE_DSN while enforcing complete DSN configuration."""
        if self.oracle_dsn_avis is None and self.oracle_dsn is not None:
            self.oracle_dsn_avis = self.oracle_dsn
        if self.oracle_dsn_budget is None and self.oracle_dsn is not None:
            self.oracle_dsn_budget = self.oracle_dsn

        if self.oracle_dsn_avis is None or self.oracle_dsn_budget is None:
            raise ValueError(
                "Set both ORACLE_DSN_AVIS and ORACLE_DSN_BUDGET, "
                "or set legacy ORACLE_DSN for temporary fallback."
            )
        return self

    def get_dsn(self, brand: str) -> str:
        """Return the Oracle DSN for a given brand name.

        Args:
            brand: The brand identifier ("avis" or "budget").

        Returns:
            The corresponding Oracle DSN connection string.

        Raises:
            ValueError: If the brand is not recognized.
        """
        dsn_map = {
            "avis": self.oracle_dsn_avis,
            "budget": self.oracle_dsn_budget,
        }
        dsn = dsn_map.get(brand)
        if dsn is None:
            raise ValueError(f"Unknown brand: {brand}")
        return dsn


settings = Settings()
