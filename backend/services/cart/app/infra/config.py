from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR: Path = Path(__file__).resolve().parents[4]
SERVICE_DIR: Path = Path(__file__).parents[2]


class Settings(BaseSettings):
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=SERVICE_DIR / ".env",
        case_sensitive=False,
    )

    jwt_public_key_path: Path = BASE_DIR / "keys" / "public.pem"
    redis_url: str
    cart_ttl_seconds: int = 60 * 60 * 24 * 7
    cart_catalog_url: str = "http://catalog:8000/api/v1"


settings = Settings()  # pyright: ignore[reportCallIssue]
