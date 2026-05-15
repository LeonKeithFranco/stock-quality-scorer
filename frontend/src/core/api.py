from dataclasses import dataclass
from typing import Any, Self

import httpx
import streamlit as st

from src.core.config import get_settings


@dataclass(frozen=True, slots=True)
class PredictionResponse:
    ticker: str
    outperformance_probability: float
    predicted_class: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            ticker=data["ticker"],
            outperformance_probability=data["outperformance_probability"],
            predicted_class=data["predicted_class"],
        )


class APIClient:
    def __init__(self, timeout: float | None = None) -> None:
        self.client = httpx.Client(
            base_url=get_settings().api_base_url,
            timeout=get_settings().api_timeout if timeout is not None else timeout,
        )

    def close(self) -> None:
        self.client.close()

    def predict(self, ticker: str) -> PredictionResponse:
        response = self.client.post("/predict/", json={"ticker": ticker})
        response.raise_for_status()

        return PredictionResponse.from_dict(response.json())

    def predict_snp_500(self) -> list[PredictionResponse]:
        response = self.client.post("/predict/snp-500")
        response.raise_for_status()

        return [PredictionResponse.from_dict(data) for data in response.json()]

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.close()

        return False


@st.cache_data(ttl=86400, show_spinner=False)
def predict(ticker: str) -> PredictionResponse:
    with APIClient(timeout=10.0) as client:
        return client.predict(ticker)


@st.cache_data(ttl=86400, show_spinner=False)
def predict_snp_500() -> list[PredictionResponse]:
    with APIClient() as client:
        return client.predict_snp_500()
