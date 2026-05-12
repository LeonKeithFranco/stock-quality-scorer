from app.core.constants import TARGET_INFO_KEYS
from app.domain.service import _dict_to_df_with_col_expected_order


def test_dict_to_df() -> None:
    fake_fundamental_info = {
        "ticker": "FAKE",
        "trailingPE": 1.0,
        "priceToBook": 1.0,
        "returnOnEquity": 1.0,
        "debtToEquity": 1.0,
        "revenueGrowth": 1.0,
        "grossMargins": 1.0,
        "operatingMargins": 1.0,
        "profitMargins": 1.0,
    }

    df_fake_fundamental = _dict_to_df_with_col_expected_order(fake_fundamental_info)

    for actual_col_name, expected_col_name in zip(
        df_fake_fundamental.columns, TARGET_INFO_KEYS
    ):
        assert actual_col_name == expected_col_name
