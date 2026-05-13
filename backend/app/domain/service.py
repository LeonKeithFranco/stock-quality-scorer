import asyncio
from typing import Annotated

import httpx
import pandas as pd
from bs4 import BeautifulSoup
from cachetools import TTLCache
from cachetools_async import cached
from fastapi import Depends

from app.core.api import get_fundamentals
from app.core.constants import TARGET_INFO_KEYS
from app.core.exceptions import DataSourceError
from app.core.model import predict
from app.domain.schemas import PredictionResponse


def _dict_to_df_with_col_expected_order(dict_fundamentals: dict) -> pd.DataFrame:
    df_fundamentals = pd.DataFrame([dict_fundamentals])

    return df_fundamentals[TARGET_INFO_KEYS]


@cached(cache=TTLCache(maxsize=1, ttl=86_400))
async def _get_snp_500_ticker_list() -> list[str]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
                headers={
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:150.0) Gecko/20100101 Firefox/150.0",
                },
            )
            response.raise_for_status()
    except Exception as e:
        raise DataSourceError(source="wikipedia", details=str(e))

    soup = BeautifulSoup(response.text, "lxml")
    table = soup.find("table", id="constituents")

    if table is None:
        raise DataSourceError(
            source="wikipedia", details="Constituent table not found."
        )

    rows = table.find_all("tr")

    tickers = []

    for row in rows[1:]:
        ticker = row.find_all("td")[0].get_text(strip=True)
        tickers.append(ticker)

    return tickers


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

    async def predict_outperformance_of_snp_500(self) -> list[PredictionResponse]:
        tickers = await _get_snp_500_ticker_list()

        results = await asyncio.gather(
            *(self.predict_outperformance(ticker) for ticker in tickers),
            return_exceptions=True,
        )

        prediction_resps = [
            pred_resp
            for pred_resp in results
            if not isinstance(pred_resp, BaseException)
        ]

        return prediction_resps


ServiceDependency = Annotated[Service, Depends(Service)]
