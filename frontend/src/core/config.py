from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class _Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(min_length=1, max_length=50)
    app_debug: bool = True
    api_base_url: str = "http://127.0.0.1:8000"


@lru_cache
def get_settings() -> _Settings:
    return _Settings()  # ty: ignore[missing-argument]
