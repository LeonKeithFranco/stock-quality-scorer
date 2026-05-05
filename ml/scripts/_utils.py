from datetime import datetime

_DATE_FORMAT = "%y%m%d"

FILE_BASE_NAME = "snp_500_constituents_"


def get_today_date_as_str() -> str:
    return datetime.now().date().strftime(_DATE_FORMAT)
