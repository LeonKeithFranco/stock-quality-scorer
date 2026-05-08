from pprint import pp

import pandas as pd
import pytest
from dateutil.relativedelta import relativedelta
from pandas.core.dtypes.api import is_float_dtype, is_integer_dtype
from scripts.utils import (
    get_fundamentals_path,
    get_prices_path,
    get_tickers,
    get_training_data_path,
)


@pytest.fixture(scope="session")
def tickers() -> list[str]:
    return get_tickers()


@pytest.fixture(scope="session")
def fundamentals() -> pd.DataFrame:
    return pd.read_parquet(get_fundamentals_path())


@pytest.fixture(scope="session")
def prices() -> pd.DataFrame:
    return pd.read_parquet(get_prices_path())


@pytest.fixture(scope="session")
def training_data() -> pd.DataFrame:
    return pd.read_parquet(get_training_data_path())


class TestSNP500CSV:
    def test_correct_amount_of_tickers(self, tickers: list[str]) -> None:
        # companies can have multiple classes of stocks, hence why it's possible to have
        # more than 500 in the S&P 500
        min_amount = 500

        assert len(tickers) >= min_amount


class TestSNP500FundamentalsParquet:
    def test_expected_tickers(
        self, fundamentals: pd.DataFrame, tickers: list[str]
    ) -> None:
        assert set(fundamentals["ticker"]) == set(tickers)

    def test_expected_column_names(self, fundamentals: pd.DataFrame) -> None:
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

        assert set(fundamentals.columns) == expected_column_names

    def test_expected_column_types(self, fundamentals: pd.DataFrame) -> None:
        expected_numerical_columns = {
            "trailingPE",
            "priceToBook",
            "returnOnEquity",
            "debtToEquity",
            "revenueGrowth",
            "grossMargins",
            "operatingMargins",
            "profitMargins",
        }

        for col in expected_numerical_columns:
            assert is_float_dtype(fundamentals[col])


class TestSNP500PricesParquet:
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
        expected_year_diff_min = 4

        min_date = prices["date"].min()
        max_date = prices["date"].max()
        date_diff = relativedelta(max_date, min_date)

        assert date_diff.years >= expected_year_diff_min

    def test_no_duplicate_date_ticker_entries(self, prices: pd.DataFrame) -> None:
        dates = prices["date"]
        tickers = prices["ticker"]
        date_ticker_entries = set(zip(dates, tickers))

        assert len(date_ticker_entries) == len(prices)


class TestTrainingDataset:
    def test_at_most_same_length_as_fundamental(
        self, training_data: pd.DataFrame, fundamentals: pd.DataFrame
    ) -> None:
        assert len(training_data) <= len(fundamentals)

    def test_training_data_tickers_is_subset_of_fundamentals(
        self, training_data: pd.DataFrame, fundamentals: pd.DataFrame
    ) -> None:
        training_tickers = set(training_data["ticker"])
        fundamental_tickers = set(fundamentals["ticker"])

        assert training_tickers.issubset(fundamental_tickers)

    def test_beat_snp_500_col(self, training_data: pd.DataFrame) -> None:
        col = training_data["beatSnp500"]

        col_values = set(col)
        expected_col_values = {0, 1}

        assert is_integer_dtype(col)
        assert col_values.issubset(expected_col_values)

    def test_cols_for_nan(self, training_data: pd.DataFrame) -> None:
        nans = training_data.isna().sum()

        assert nans["ticker"] == 0
        assert nans["beatSnp500"] == 0

        nans = nans.drop(["ticker", "beatSnp500"])

        assert (nans >= 0).all()

    def test_no_featureless_rows(self, training_data: pd.DataFrame) -> None:
        # only 2 non-nan columns should be exist, 'ticker' and 'beatSnp500'
        mask = training_data.notna().sum(axis=1) == 2

        assert len(training_data[mask]) == 0
