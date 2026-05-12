import hashlib
from pathlib import Path

import joblib
import pandas as pd
from cachetools import LRUCache, cached
from pandas.core.util.hashing import hash_pandas_object
from sklearn.calibration import CalibratedClassifierCV

_MODEL_FILE_PATH = Path(__file__).parent.parent.parent / "data" / "rf_calibrated.joblib"


def _custom_df_hash(df: pd.DataFrame) -> str:
    hashes = hash_pandas_object(df)

    return hashlib.sha256(hashes.values.tobytes()).hexdigest()


@cached(cache=LRUCache(maxsize=1))
def get_model() -> CalibratedClassifierCV:
    return joblib.load(_MODEL_FILE_PATH)


@cached(cache=LRUCache(maxsize=525), key=_custom_df_hash)
def predict(fundamentals: pd.DataFrame) -> float:
    prediction = get_model().predict_proba(fundamentals)
    outperform_probability = prediction[:, 1]

    return float(outperform_probability)
