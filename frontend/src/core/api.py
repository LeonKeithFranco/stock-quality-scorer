from dataclasses import dataclass
from typing import Any, Self

import httpx
import streamlit as st

from src.core.config import get_settings


@dataclass(frozen=True, slots=True)
class PredictionResponse:
    """A single stock outperformance prediction returned by the backend."""

    ticker: str
    outperformance_probability: float
    predicted_class: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Construct a PredictionResponse from a raw API response dictionary.

        Args:
            data: The JSON-decoded response dictionary from the backend.

        Returns:
            PredictionResponse: A new instance populated from the dictionary.
        """
        return cls(
            ticker=data["ticker"],
            outperformance_probability=data["outperformance_probability"],
            predicted_class=data["predicted_class"],
        )


class APIClient:
    """HTTP client for communicating with the FastAPI backend.

    Wraps an httpx.Client configured with the backend's base URL and timeout. Intended to
    be used as a context manager so the underlying connection is properly closed after
    use.

    Attributes:
        client: The underlying httpx.Client instance.
    """

    def __init__(self, timeout: float | None = None) -> None:
        """Initialize the client with an optional timeout.

        Args:
            timeout: Request timeout in seconds. Defaults to the value from settings if not
                provided.
        """
        self.client = httpx.Client(
            base_url=get_settings().api_base_url,
            timeout=get_settings().api_timeout if timeout is not None else timeout,
        )

    def close(self) -> None:
        """Close the underlying HTTP connection."""
        self.client.close()

    def predict(self, ticker: str) -> PredictionResponse:
        """Fetch an outperformance prediction for a single ticker from the backend.

        Args:
            ticker: The stock ticker symbol to predict for.

        Returns:
            PredictionResponse: The parsed prediction result from the backend.
        """
        response = self.client.post("/predict/", json={"ticker": ticker})
        response.raise_for_status()

        return PredictionResponse.from_dict(response.json())

    def predict_snp_500(self) -> list[PredictionResponse]:
        """Fetch outperformance predictions for all S&P 500 tickers from the backend.

        Returns:
            list[PredictionResponse]: The parsed prediction results for each S&P 500
                constituent.
        """
        response = self.client.post("/predict/snp-500")
        response.raise_for_status()

        return [PredictionResponse.from_dict(data) for data in response.json()]

    def __enter__(self) -> Self:
        """Enter the context manager.

        Returns:
            APIClient: The APIClient instance itself.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Exit the context manager and close the HTTP connection.

        Args:
            exc_type: The exception type if an exception occurred, None otherwise.
            exc_val: The exception value if an exception occurred, None otherwise.
            exc_tb: The exception traceback if an exception occurred, None otherwise.

        Returns:
            bool: False to propagate exceptions.
        """
        self.close()

        return False


@st.cache_data(ttl=86400, show_spinner=False)
def predict(ticker: str) -> PredictionResponse:
    """Fetch a cached single-ticker prediction from the backend.

    Args:
        ticker: The stock ticker symbol to predict for.

    Returns:
        PredictionResponse: The prediction result from the backend.
    """
    with APIClient(timeout=10.0) as client:
        return client.predict(ticker)


@st.cache_data(ttl=86400, show_spinner=False)
def predict_snp_500() -> list[PredictionResponse]:
    """Fetch cached S&P 500 predictions from the backend.

    Returns:
        list[PredictionResponse]: The prediction results for all S&P 500 constituents.
    """
    with APIClient() as client:
        return client.predict_snp_500()
