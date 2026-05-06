from typing import cast

import pandas as pd
import yfinance as yf

from scripts._utils import (
    FILE_BASE_NAME,
    PARQUET_FOLDER_PATH,
    get_tickers,
    get_today_date_as_str,
)


def main():
    today_date_str = get_today_date_as_str()
    full_file_name = f"{FILE_BASE_NAME}prices_{today_date_str}.parquet"
    file_path = PARQUET_FOLDER_PATH / full_file_name

    if file_path.exists():
        return

    tickers = get_tickers()

    try:
        df_price_info = cast(
            pd.DataFrame,
            yf.download(
                tickers=["^GSPC"] + tickers,
                period="5y",
                group_by="ticker",
                actions=False,
            ),
        )
    except Exception as exc:
        print(f"Download failed: {exc}")
        return

    df_price_info.to_parquet(file_path)


if __name__ == "__main__":
    main()
