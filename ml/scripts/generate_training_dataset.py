from typing import cast

import pandas as pd

from scripts.utils import PARQUET_FOLDER_PATH, get_fundamentals_path, get_prices_path


def _get_annual_rate_of_return(df_prices: pd.DataFrame) -> float | None:
    try:
        df_most_recent = df_prices.iloc[-1]
        current_price = df_most_recent["close"]

        year_ago_date = df_most_recent["date"] - pd.DateOffset(years=1)
        year_ago_price = df_prices[df_prices["date"] <= year_ago_date]["close"].iloc[-1]

        return current_price / year_ago_price - 1.0
    except IndexError:
        return None


def main():
    df_prices = pd.read_parquet(get_prices_path()).sort_values("date")

    df_snp_500_prices = df_prices[df_prices["ticker"] == "^GSPC"]
    snp_500_rate_of_return = cast(float, _get_annual_rate_of_return(df_snp_500_prices))

    df_fundamentals = pd.read_parquet(get_fundamentals_path())

    tickers = df_fundamentals["ticker"]

    beat_snp_500 = {}
    for ticker in tickers:
        df_ticker_prices = df_prices[df_prices["ticker"] == ticker]
        current_ticker_rate_of_return = _get_annual_rate_of_return(df_ticker_prices)

        beat_snp_500.update(
            {ticker: float("nan")}
            if current_ticker_rate_of_return is None
            else {
                ticker: 1
                if current_ticker_rate_of_return > snp_500_rate_of_return
                else 0
            }
        )

    df_training_dataset = df_fundamentals.copy()
    df_training_dataset["beatSnp500"] = df_fundamentals["ticker"].map(beat_snp_500)
    df_training_dataset = df_training_dataset.dropna(subset=["beatSnp500"])

    df_training_dataset.to_parquet(PARQUET_FOLDER_PATH / "training_dataset.parquet")


if __name__ == "__main__":
    main()
