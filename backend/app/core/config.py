from pathlib import Path

from cachetools import LRUCache, cached
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


@cached(cache=LRUCache(maxsize=1))
def get_settings() -> _Settings:
    return _Settings()  # ty: ignore[missing-argument]
