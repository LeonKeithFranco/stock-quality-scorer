import asyncio

import yfinance as yf
from cachetools import TTLCache
from cachetools_async import cached

_MAX_NUM_OF_STOCK_INFO = 525
_TTL_IN_SECONDS = 86_400
_TARGET_INFO_KEYS = [
    "ticker",
    "trailingPE",
    "priceToBook",
    "returnOnEquity",
    "debtToEquity",
    "revenueGrowth",
    "grossMargins",
    "operatingMargins",
    "profitMargins",
]


def _get_fundamentals_helper(ticker: str) -> dict:
    return yf.Ticker(ticker).info


@cached(cache=TTLCache(maxsize=_MAX_NUM_OF_STOCK_INFO, ttl=_TTL_IN_SECONDS))
async def get_fundamentals(ticker: str) -> dict:
    funadmental_info = await asyncio.to_thread(_get_fundamentals_helper, ticker)
    target_info = {key: funadmental_info[key] for key in _TARGET_INFO_KEYS}

    return target_info
