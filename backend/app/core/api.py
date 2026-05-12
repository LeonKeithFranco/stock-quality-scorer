import asyncio

import yfinance as yf
from cachetools import TTLCache
from cachetools_async import cached

from app.core.constants import TARGET_INFO_KEYS

_MAX_NUM_OF_STOCK_INFO = 525
_TTL_IN_SECONDS = 86_400


def _get_fundamentals_helper(ticker: str) -> dict:
    return yf.Ticker(ticker).info


@cached(cache=TTLCache(maxsize=_MAX_NUM_OF_STOCK_INFO, ttl=_TTL_IN_SECONDS))
async def get_fundamentals(ticker: str) -> dict:
    fundamental_info = await asyncio.to_thread(_get_fundamentals_helper, ticker)
    target_info = {key: fundamental_info.get(key, None) for key in TARGET_INFO_KEYS}

    return target_info
