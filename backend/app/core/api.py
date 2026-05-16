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
    """Fetch stock fundamental data from yfinance with automatic retry logic.

    Attempts to retrieve the ticker's info dict, retrying with exponential backoff on
    rate-limit errors up to _MAX_ATTEMPTS times.

    Args:
        ticker: The stock ticker symbol to look up.

    Returns:
        dict: The raw info dictionary returned by yfinance.

    Raises:
        DataSourceError: If yfinance raises an unexpected error or all rate-limit retries
            are exhausted.
        StockMissingError: If the ticker does not exist in yfinance.
    """

    stock_info = None
    wait_time = 1
    attempts = 0

    while not stock_info and attempts < _MAX_ATTEMPTS:
        attempts += 1
        try:
            stock_info = yf.Ticker(ticker).info
            if "symbol" in stock_info:
                break
        except YFRateLimitError:
            time.sleep(wait_time)
            wait_time *= 1.5
            wait_time += random.uniform(0.0, wait_time * 0.1)
            continue
        except Exception as e:
            raise DataSourceError(source="yfinance", details=str(e))

        break

    if stock_info is None:
        raise DataSourceError(source="yfinance", details="Rate limit retries exceeded.")

    if not stock_info or "symbol" not in stock_info:
        raise StockMissingError(ticker=ticker)

    return stock_info


@cached(cache=TTLCache(maxsize=_MAX_NUM_OF_STOCK_INFO, ttl=_TTL_IN_SECONDS))
async def get_fundamentals(ticker: str) -> dict:
    """Retrieve the target fundamental metrics for a stock ticker.

    Delegates to the synchronous yfinance helper in a separate thread so the event loop
    is not blocked. Results are cached with a 24-hour TTL.

    Args:
        ticker: The stock ticker symbol to look up.

    Returns:
        dict: A dictionary containing only the keys defined in TARGET_INFO_KEYS, with None
            for any missing values.
    """
    fundamental_info = await asyncio.to_thread(_get_fundamentals_helper, ticker)

    target_info = {key: fundamental_info.get(key, None) for key in TARGET_INFO_KEYS}

    return target_info
