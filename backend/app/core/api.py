import asyncio
import random
import time

import yfinance as yf
from cachetools import TTLCache
from cachetools_async import cached
from yfinance.exceptions import YFRateLimitError

from app.core.constants import TARGET_INFO_KEYS
from app.core.exceptions import DataSourceError, StockMissingError

_MAX_NUM_OF_STOCK_INFO = 525
_TTL_IN_SECONDS = 86_400
_MAX_ATTEMPTS = 7


def _get_fundamentals_helper(ticker: str) -> dict:
    stock_info = None
    wait_time = 1
    attempts = 0

    while not stock_info and attempts < _MAX_ATTEMPTS:
        attempts += 1
        try:
            stock_info = yf.Ticker(ticker).info
        except YFRateLimitError:
            time.sleep(wait_time)
            wait_time *= 1.5
            wait_time += random.uniform(0.0, wait_time * 0.1)
        except Exception as e:
            raise DataSourceError(source="yfinance", details=str(e))

    if not stock_info or "symbol" not in stock_info:
        raise StockMissingError(ticker=ticker)

    return stock_info


@cached(cache=TTLCache(maxsize=_MAX_NUM_OF_STOCK_INFO, ttl=_TTL_IN_SECONDS))
async def get_fundamentals(ticker: str) -> dict:
    fundamental_info = await asyncio.to_thread(_get_fundamentals_helper, ticker)

    target_info = {key: fundamental_info.get(key, None) for key in TARGET_INFO_KEYS}

    return target_info
