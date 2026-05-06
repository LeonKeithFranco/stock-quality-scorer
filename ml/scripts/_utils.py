import csv
from datetime import datetime
from pathlib import Path

_DATE_FORMAT = "%y%m%d"

FILE_BASE_NAME = "snp_500_constituents_"

DATA_FOLDER_PATH = Path(__file__).parent.parent / "data"
CSV_FOLDER_PATH = DATA_FOLDER_PATH / "csvs"
PARQUET_FOLDER_PATH = DATA_FOLDER_PATH / "parquets"


def get_today_date_as_str() -> str:
    return datetime.now().date().strftime(_DATE_FORMAT)


def get_tickers() -> list[str]:
    snp_500_constituents_files = list(CSV_FOLDER_PATH.glob("*.csv"))

    if not snp_500_constituents_files:
        raise FileNotFoundError(
            "There are no snp_500_constituents_*.csv files. Please run get_snp_500.py script first."
        )

    most_recent_file = (
        snp_500_constituents_files[0]
        if len(snp_500_constituents_files) == 1
        else sorted(snp_500_constituents_files)[-1]
    )

    tickers: list[str] = []

    with open(most_recent_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tickers.append(row["Symbol"])

    return tickers


def get_prices() -> Path:
    snp_500_constituents_prices_files = list(
        PARQUET_FOLDER_PATH.glob("*prices*.parquet")
    )

    if not snp_500_constituents_prices_files:
        raise FileNotFoundError(
            "There are no snp_500_constituents_prices_*.parquet. Please run get_price_history.py script first."
        )

    return (
        snp_500_constituents_prices_files[0]
        if len(snp_500_constituents_prices_files) == 1
        else sorted(snp_500_constituents_prices_files)[-1]
    )


def get_fundamentals() -> Path:
    snp_500_constituents_fundamentals_files = list(
        PARQUET_FOLDER_PATH.glob("*fundamentals*.parquet")
    )

    if not snp_500_constituents_fundamentals_files:
        raise FileNotFoundError(
            "There are no snp_500_constituents_fundamentals_*.parquet. Please run get_fundamentals.py script first."
        )

    return (
        snp_500_constituents_fundamentals_files[0]
        if len(snp_500_constituents_fundamentals_files) == 1
        else sorted(snp_500_constituents_fundamentals_files)[-1]
    )
