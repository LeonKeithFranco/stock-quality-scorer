from pprint import pp

import pandas as pd
import pytest
from dateutil.relativedelta import relativedelta
from pandas.core.dtypes.api import is_float_dtype
from scripts._utils import get_fundamentals_path, get_prices_path, get_tickers


@pytest.fixture(scope="session")
def tickers() -> list[str]:
    return get_tickers()


@pytest.fixture(scope="session")
def fundamentals() -> pd.DataFrame:
    return pd.read_parquet(get_fundamentals_path())


@pytest.fixture(scope="session")
def prices() -> pd.DataFrame:
    return pd.read_parquet(get_prices_path())


class TestSNP500CSV:
    def test_correct_amount_of_tickers(self, tickers: list[str]) -> None:
        # companies can have multiple classes of stocks, hence why it's possible to have
        # more tha 500 in the S&P 500
        min_amount = 500

        assert len(tickers) >= min_amount


class TestSNP500FundamentalsParquet:
    def test_structure_of_fundamentals_data(
        self, fundamentals: pd.DataFrame, tickers: list[str]
    ) -> None:
        expected_column_names = {
            "ticker",
            "trailingPE",
            "priceToBook",
            "returnOnEquity",
            "debtToEquity",
            "revenueGrowth",
            "grossMargins",
            "operatingMargins",
            "profitMargins",
        }
        expected_numerical_columns = expected_column_names - {"ticker"}

        assert set(fundamentals.columns) == expected_column_names
        assert set(fundamentals["ticker"]) == set(tickers)

        for col in expected_numerical_columns:
            assert is_float_dtype(fundamentals[col])


class TestSNP500PricesParquest:
    def test_expected_tickers(self, prices: pd.DataFrame, tickers: list[str]) -> None:
        assert set(prices["ticker"]) == set(tickers + ["^GSPC"])

    def test_expected_column_names(self, prices: pd.DataFrame) -> None:
        expected_column_names = {
            "date",
            "ticker",
            "close",
        }

        assert set(prices.columns) == expected_column_names

    def test_date_range(self, prices: pd.DataFrame) -> None:
        expected_year_diff = 5

        min_date = prices["date"].min()
        max_date = prices["date"].max()
        date_diff = relativedelta(max_date, min_date)

        assert date_diff.years == expected_year_diff

    def test_no_duplicate_date_ticker_entries(self, prices: pd.DataFrame) -> None:
        dates = prices["date"]
        tickers = prices["ticker"]
        date_ticker_entries = set(zip(dates, tickers))

        assert len(date_ticker_entries) == len(prices)
