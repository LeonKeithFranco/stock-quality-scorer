from typing import Literal

from pydantic import BaseModel, Field


class StockBase(BaseModel):
    """Base schema for stock-related requests and response.

    Attributes:
        ticker: The stock's exchange ticker symbol.
    """

    ticker: str = Field(min_length=1, max_length=10)


class PredictionRequest(StockBase):
    """Pydantic request model for the POST /predict endpoint."""

    pass


class PredictionResponse(StockBase):
    """Pydantic response model for the POST /predict endpoints.

    Attributes:
        outperformance_probability: The predicted probability that the stock will
            outperform the S&P 500, between 0.0 and 1.0.
        predicted_class: Binary label where 1 indicates predict outperformance and 0
            indicates otherwise.
    """

    outperformance_probability: float = Field(ge=0.0, le=1.0)
    predicted_class: Literal[0, 1]
