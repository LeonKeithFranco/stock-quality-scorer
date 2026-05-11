from pprint import pp

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from scripts.utils import get_training_data_path


def _build_pipeline() -> Pipeline:
    model = RandomForestClassifier()

    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", model),
        ]
    )


def _print_results(reults: tuple[np.ndarray, np.ndarray], title: str) -> None:
    df_results = (
        pd.DataFrame(
            {
                "Avg Predicted Probability": reults[1],
                "Actual Outperformance Rate": reults[0],
            }
        )
        .round(4)
        .T
    )
    df_results.columns = [f"Fold {i + 1}" for i in range(df_results.shape[1])]

    print(f"===== {title} =====")
    pp(df_results)


def main():
    df = pd.read_parquet(get_training_data_path())

    X = df.drop(columns=["ticker", "beatSnp500"])
    y = df["beatSnp500"]

    raw_pipeline = _build_pipeline()
    raw_pipeline.fit(X, y)
    raw_probs = raw_pipeline.predict_proba(X)

    calibrated_pipeline = CalibratedClassifierCV(
        _build_pipeline(),
        method="sigmoid",
        cv=5,
    )
    calibrated_pipeline.fit(X, y)
    calibrated_probs = calibrated_pipeline.predict_proba(X)

    _print_results(calibration_curve(y, raw_probs[:, 1]), "Raw Results")
    print("\n")
    _print_results(calibration_curve(y, calibrated_probs[:, 1]), "Calibrated Results")


if __name__ == "__main__":
    main()
