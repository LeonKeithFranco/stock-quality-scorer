from datetime import datetime
from pathlib import Path

_DATE_FORMAT = "%y%m%d"

FILE_BASE_NAME = "snp_500_constituents_"

DATA_FOLDER_PATH = Path(__file__).parent.parent / "data"
CSV_FOLDER_PATH = DATA_FOLDER_PATH / "csvs"
PARQUET_FOLDER_PATH = DATA_FOLDER_PATH / "parquets"


def get_today_date_as_str() -> str:
    return datetime.now().date().strftime(_DATE_FORMAT)
