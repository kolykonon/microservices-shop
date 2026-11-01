from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic_settings.main import SettingsConfigDict

SERVICE_DIR = Path(__file__).parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=SERVICE_DIR / ".env", case_sensitive=False
    )
    db_url: str


settings = Settings()  # pyright: ignore[reportCallIssue]
