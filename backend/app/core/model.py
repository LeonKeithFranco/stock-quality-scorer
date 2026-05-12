from pathlib import Path

import joblib
import pandas as pd
from cachetools import LRUCache, cached
from sklearn.calibration import CalibratedClassifierCV

_MODEL_FILE_PATH = Path(__file__).parent.parent.parent / "data" / "rf_calibrated.joblib"


@cached(cache=LRUCache(maxsize=1))
def get_model() -> CalibratedClassifierCV:
    return joblib.load(_MODEL_FILE_PATH)


@cached(cache=LRUCache(maxsize=525))
def predict(fundamentals: pd.DataFrame) -> float:
    prediction = get_model().predict_proba(fundamentals)
    outperform_probability = prediction[:, 1]

    return float(outperform_probability)
