from typing import Annotated

import pandas as pd
from fastapi import Depends

from app.core.api import get_fundamentals
from app.core.constants import TARGET_INFO_KEYS
from app.core.model import predict
from app.domain.schemas import PredictionResponse


def _dict_to_df_with_col_expected_order(dict_fundamentals: dict) -> pd.DataFrame:
    df_fundamentals = pd.DataFrame([dict_fundamentals])

    return df_fundamentals[TARGET_INFO_KEYS]


class Service:
    async def predict_outperformance(self, ticker: str) -> PredictionResponse:
        stock_fundamentals = await get_fundamentals(ticker)
        df_fundamentals = _dict_to_df_with_col_expected_order(stock_fundamentals)
        predicted_outperform = predict(df_fundamentals)

        return PredictionResponse(
            ticker=ticker,
            outperformance_probability=predicted_outperform,
            predicted_class=1 if predicted_outperform > 0.5 else 0,
        )


ServiceDependency = Annotated[Service, Depends(Service)]
