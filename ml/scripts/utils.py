import csv
from datetime import datetime
from pathlib import Path

_DATE_FORMAT = "%y%m%d"

FILE_BASE_NAME = "snp_500_constituents_"

DATA_FOLDER_PATH = Path(__file__).parent.parent / "data"
CSV_FOLDER_PATH = DATA_FOLDER_PATH / "csvs"
PARQUET_FOLDER_PATH = DATA_FOLDER_PATH / "parquets"
MODELS_FOLDER_PATH = DATA_FOLDER_PATH / "models"


def get_today_date_as_str() -> str:
    """Return today's date as a compact string in YYMMDD format.

    Returns:
        str: The formatted date string.
    """
    return datetime.now().date().strftime(_DATE_FORMAT)


def _get_most_recent_file(
    file_name_glob_pattern: str,
    folder: Path,
    err_msg: str = "There are no files in the directory.",
) -> Path:
    """Return the most recent file in a folder matching a glob pattern.

    Files are sorted lexicographically (chronologically due to having dates in the file
    names) and the last one (most recent) is returned. If only one file matches, it is
    returned directly.

    Args:
        file_name_glob_pattern: The glob pattern to match files against.
        folder: The directory to search in.
        err_msg: The error message to raise if no files match.

    Returns:
        Path: The path to the most recent file.

    Raises:
        FileNotFoundError: If no files match the glob pattern.
    """
    files = list(folder.glob(file_name_glob_pattern))

    if not files:
        raise FileNotFoundError(err_msg)

    return files[0] if len(files) == 1 else sorted(files)[-1]


def get_tickers() -> list[str]:
    """Read the S&P 500 ticker symbols from the most recent constituents CSV.

    Returns:
        list[str]: The ticker symbols parsed from the CSV.

    Raises:
        FileNotFoundError: If no constituents CSV file exists.
    """
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
    """Return the path to the most recent price history parquet file.

    Returns:
        Path: The path to the prices parquet.

    Raises:
        FileNotFoundError: If no prices file exists.
    """
    return _get_most_recent_file(
        "*prices*.parquet",
        PARQUET_FOLDER_PATH,
        err_msg="There are no snp_500_constituents_prices_*.parquet. Please run get_price_history.py script first.",
    )


def get_fundamentals_path() -> Path:
    """Return the path to the most recent fundamentals parquet file.

    Returns:
        Path: The path to the fundamentals parquet.

    Raises:
        FileNotFoundError: If no fundamentals parquet file exists.
    """
    return _get_most_recent_file(
        "*fundamentals*.parquet",
        PARQUET_FOLDER_PATH,
        err_msg="There are no snp_500_constituents_fundamentals_*.parquet. Please run get_fundamentals.py script first.",
    )


def get_training_data_path() -> Path:
    """Return the path to the training dataset parquet file.

    Returns:
        Path: The path to the training dataset parquet.

    Raises:
        FileNotFoundError: If the training dataset parquet does not exist.
    """
    training_data_path = PARQUET_FOLDER_PATH / "training_dataset.parquet"

    if not training_data_path.exists():
        raise FileNotFoundError(
            "There is no training data parquet. Please run generate_training_dataset.py script first."
        )

    return training_data_path
