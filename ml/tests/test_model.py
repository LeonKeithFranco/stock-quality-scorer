from contextlib import nullcontext as does_not_raise

import joblib
import numpy as np
import pandas as pd
import pytest
from scripts.utils import MODELS_FOLDER_PATH, get_training_data_path
from sklearn.calibration import CalibratedClassifierCV


@pytest.fixture(scope="session")
def model() -> CalibratedClassifierCV:
    """Load the calibrated Random Forest model from disk and verify its type."""
    model = joblib.load(MODELS_FOLDER_PATH / "rf_calibrated.joblib")

    assert isinstance(model, CalibratedClassifierCV)

    return model


@pytest.fixture(scope="session")
def data() -> pd.DataFrame:
    """Load the training dataset parquet into a DataFrame."""
    return pd.read_parquet(get_training_data_path())


@pytest.fixture(scope="session")
def features(data: pd.DataFrame) -> pd.DataFrame:
    """Extract the feature columns from the training dataset."""
    return data.drop(columns=["ticker", "beatSnp500"])


class TestModel:
    """Tests for the calibrated Random Forest model's prediction behaviour."""

    def test_prediction(
        self, model: CalibratedClassifierCV, features: pd.DataFrame
    ) -> None:
        """Verify predictions produce valid class probabilities that sum to 1.0."""
        preds = model.predict_proba(features.iloc[[0]]).squeeze()

        assert len(preds) == 2
        assert sum(preds) == pytest.approx(1.0)
        assert np.all((preds >= 0.0) & (preds <= 1.0))

    def test_feature_with_nan(
        self, model: CalibratedClassifierCV, features: pd.DataFrame
    ) -> None:
        """Verify the model handles NaN feature values without raising."""
        feature_with_nan = features.copy()
        feature_with_nan.iat[0, 0] = float("nan")

        with does_not_raise():
            model.predict_proba(feature_with_nan.iloc[[0]])

    def test_bad_input_shape_raises(
        self, model: CalibratedClassifierCV, features: pd.DataFrame
    ) -> None:
        """Verify too few or too many feature columns raise ValueError."""
        df_not_enough_features = (
            features.copy().iloc[[0]].drop(features.columns[1], axis="columns")
        )

        df_too_many_features = features.copy()
        df_too_many_features["someCol"] = pd.DataFrame({1})

        with pytest.raises(ValueError):
            model.predict_proba(df_not_enough_features)

        with pytest.raises(ValueError):
            model.predict_proba(df_too_many_features)
