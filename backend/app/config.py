from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    oracle_dsn: str
    cors_origins: list[str] = ["*"]

    model_config = {"env_file": ".env"}


settings = Settings()
