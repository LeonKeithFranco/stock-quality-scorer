from typing import Literal

from pydantic import BaseModel, Field


class StockBase(BaseModel):
    ticker: str = Field(min_length=3, max_length=10)


class PredictionRequest(StockBase):
    pass


class PredictionResponse(StockBase):
    outperformance_probability: float = Field(ge=0.0)
    predicted_class: Literal[0, 1]
