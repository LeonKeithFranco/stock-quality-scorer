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


def _get_most_recent_file(
    file_name_glob_pattern: str,
    folder: Path,
    err_msg: str = "There are no files in the directory.",
) -> Path:
    files = list(folder.glob(file_name_glob_pattern))

    if not files:
        raise FileNotFoundError(err_msg)

    return files[0] if len(files) == 1 else sorted(files)[-1]


def get_tickers() -> list[str]:
    most_recent_file = _get_most_recent_file(
        "*.csv",
        CSV_FOLDER_PATH,
        err_msg="There are no snp_500_constituents_*.csv files. Please run get_snp_500.py script first.",
    )

    tickers: list[str] = []

    with open(most_recent_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tickers.append(row["Symbol"])

    return tickers


def get_prices_path() -> Path:
    return _get_most_recent_file(
        "*prices*.parquet",
        PARQUET_FOLDER_PATH,
        err_msg="There are no snp_500_constituents_prices_*.parquet. Please run get_price_history.py script first.",
    )


def get_fundamentals_path() -> Path:
    return _get_most_recent_file(
        "*fundamentals*.parquet",
        PARQUET_FOLDER_PATH,
        err_msg="There are no snp_500_constituents_fundamentals_*.parquet. Please run get_fundamentals.py script first.",
    )


def get_training_data_path() -> Path:
    training_data_path = PARQUET_FOLDER_PATH / "training_dataset.parquet"

    if not training_data_path.exists():
        raise FileNotFoundError(
            "There is no training data parquest. Please run generate_training_dataset.py script first."
        )

    return training_data_path
