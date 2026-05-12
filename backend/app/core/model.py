from functools import lru_cache
from pathlib import Path

import joblib
from sklearn.calibration import CalibratedClassifierCV

_MODEL_FILE_PATH = Path(__file__).parent.parent.parent / "data" / "rf_calibrated.joblib"


@lru_cache
def get_model() -> CalibratedClassifierCV:
    return joblib.load(_MODEL_FILE_PATH)
