from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

SERVICE_DIR = Path(__file__).resolve().parents[2]

BASE_DIR = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
        env_file=SERVICE_DIR / ".env",
    )
    redis_url: str
    cart_ttl_seconds: int = 60 * 60 * 24 * 7
    cart_catalog_url: str = "http://catalog:8000/api/v1"

    jwt_public_key_path: Path = BASE_DIR / "keys" / "public.pem"


settings: Settings = Settings()  # pyright: ignore[reportCallIssue]
