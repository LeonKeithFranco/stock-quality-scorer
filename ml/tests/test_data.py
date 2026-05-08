import pandas as pd
import pytest
from scripts._utils import get_fundamentals_path, get_tickers


@pytest.fixture(scope="session")
def tickers() -> list[str]:
    return get_tickers()


@pytest.fixture(scope="session")
def fundamentals() -> pd.DataFrame:
    return pd.read_parquet(get_fundamentals_path())


class TestSNP500CSV:
    def test_correct_amount_of_tickers(self, tickers: list[str]) -> None:
        # companies can have multiple classes of stocks, hence why it's possible to have
        # more tha 500 in the S&P 500
        min_amount = 500

        assert len(tickers) >= min_amount


# class TestSNP500FundamentalsParquest:
#     def test_c
