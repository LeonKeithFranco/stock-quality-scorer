from pathlib import Path

import streamlit as st
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class _Settings(BaseSettings):
    """Frontend application settings loaded from environment variables or .env.

    Attributes:
        app_name: The display name of the application.
        app_debug: Whether to enable debug mode.
        api_base_url: The base URL of the FastAPI backend.
        api_timeout: Request timeout in seconds for backend calls.
    """

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(min_length=1, max_length=50)
    app_debug: bool = True

    api_base_url: str = "http://127.0.0.1:8000"
    api_timeout: float = 60.0


@st.cache_data
def get_settings() -> _Settings:
    """Return the cached application settings singleton.

    Returns:
        _Settings: The frontend settings instance.
    """
    return _Settings()  # ty: ignore[missing-argument]
