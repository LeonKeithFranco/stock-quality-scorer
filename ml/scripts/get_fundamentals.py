import time

import pandas as pd
import yfinance as yf
from yfinance.exceptions import YFRateLimitError

from scripts._utils import (
    FILE_BASE_NAME,
    PARQUET_FOLDER_PATH,
    get_tickers,
    get_today_date_as_str,
)

_MAX_ATTEMPTS = 6
_TARGET_KEYS = [
    "trailingPE",
    "priceToBook",
    "returnOnEquity",
    "debtToEquity",
    "revenueGrowth",
    "grossMargins",
    "operatingMargins",
    "profitMargins",
]


def main():
    today_date_str = get_today_date_as_str()
    full_file_name = f"{FILE_BASE_NAME}fundamentals_{today_date_str}.parquet"
    file_path = PARQUET_FOLDER_PATH / full_file_name

    if file_path.exists():
        return

    tickers = get_tickers()

    snp_500_constituents_info = []

    for ticker in tickers:
        wait_time = 1
        info_retrieved = False
        attempts = 0

        while not info_retrieved and attempts < _MAX_ATTEMPTS:
            attempts += 1
            try:
                yf_stock_info = yf.Ticker(ticker).info
                info_retrieved = True
            except YFRateLimitError:
                time.sleep(wait_time)
                wait_time *= 1.5

        if not info_retrieved:
            print(
                f"Could not get info for '{ticker}'. "
                "Consider trying again after a few minutes or "
                "raising the number of attempts."
            )
            continue

        stock_info = {"ticker": ticker} | {
            k: yf_stock_info.get(k, None) for k in _TARGET_KEYS
        }
        snp_500_constituents_info.append(stock_info)

    df = pd.DataFrame(snp_500_constituents_info)

    df.to_parquet(file_path)


if __name__ == "__main__":
    main()
