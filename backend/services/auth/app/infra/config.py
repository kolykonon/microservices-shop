from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[4]

SERVICE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=SERVICE_DIR / ".env",
        case_sensitive=False,
    )

    postgres_url: str

    jwt_private_key_path: Path = BASE_DIR / "keys" / "private.pem"
    jwt_public_key_path: Path = BASE_DIR / "keys" / "public.pem"
    jwt_encode_algorithm: str = "RS256"
    jwt_access_token_type: str = "access"
    jwt_refresh_token_type: str = "refresh"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7


settings = (
    Settings()
)  # pyright: ignore[reportCallIssue] pyright видит как обычный __init__()
