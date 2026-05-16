import hashlib
from pathlib import Path

import joblib
import pandas as pd
from cachetools import LFUCache, LRUCache, cached
from pandas.core.util.hashing import hash_pandas_object
from sklearn.calibration import CalibratedClassifierCV

_MODEL_FILE_PATH = Path(__file__).parent.parent.parent / "data" / "rf_calibrated.joblib"


def _custom_df_hash(df: pd.DataFrame) -> str:
    """Compute a SHA-256 hash of a DataFrame for use as a cache key.

    Args:
        df: The DataFrame to hash.

    Returns:
        str: A hex-encoded SHA-256 digest of the DataFrame's contents.
    """
    hashes = hash_pandas_object(df)

    return hashlib.sha256(hashes.values.tobytes()).hexdigest()


@cached(cache=LRUCache(maxsize=1))
def get_model() -> CalibratedClassifierCV:
    """Load and return the cached calibrated random forest model.

    Returns:
        CalibratedClassifierCV: The pre-trained calibrated classifier loaded from disk.
    """
    return joblib.load(_MODEL_FILE_PATH)


@cached(cache=LFUCache(maxsize=525), key=_custom_df_hash)
def predict(fundamentals: pd.DataFrame) -> float:
    """Predict the probability a stock will outperform the S&P 500.

    Results are cached using an LFU strategy keyed by the DataFrame's content hash.

    Args:
        fundamentals: A single-row DataFrame containing the stock's fundamental metrics in
            the expected column order.

    Returns:
        float: The predicted probability of outperformance, between 0.0 and 1.0.
    """
    prediction = get_model().predict_proba(fundamentals)
    outperform_probability = prediction[:, 1][0]

    return float(outperform_probability)
