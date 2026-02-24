from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    oracle_dsn_avis: str
    oracle_dsn_budget: str
    cors_origins: list[str] = ["*"]

    model_config = {"env_file": ".env", "extra": "ignore"}

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
