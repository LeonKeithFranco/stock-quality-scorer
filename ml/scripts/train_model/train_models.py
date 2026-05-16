from pprint import pp

import numpy as np
import pandas as pd
from sklearn.base import ClassifierMixin
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from scripts.utils import get_training_data_path


def _cross_val_score_runner(
    model: ClassifierMixin, features: pd.DataFrame, labels: pd.Series
) -> np.ndarray:
    """Run stratified 5-fold cross-validation for a classifier and return ROC AUC scores.

    Wraps the classifier in a pipeline with median imputation and standard scaling before
    scoring.

    Args:
        model: The scikit-learn classifier to evaluate.
        features: The feature matrix.
        labels: The target labels.

    Returns:
        np.ndarray: An array of ROC AUC scores, one per fold.
    """
    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()

    pipeline = Pipeline([("imputer", imputer), ("scaler", scaler), ("model", model)])

    skf: StratifiedKFold = StratifiedKFold(n_splits=5)

    return cross_val_score(pipeline, features, labels, cv=skf, scoring="roc_auc")


def main():
    """Compare classifiers on the training dataset and print fold scores.

    Evaluates Logistic Regression, Random Forest, and Gradient Boosting using stratified
    5-fold cross-validation with ROC AUC scoring. Prints per-fold scores and summary
    statistics (mean and standard deviation) for each model.
    """
    df = pd.read_parquet(get_training_data_path())

    X = df.drop(columns=["ticker", "beatSnp500"])
    y = df["beatSnp500"]

    lr_scores = _cross_val_score_runner(
        model=LogisticRegression(), features=X, labels=y
    )
    rf_scores = _cross_val_score_runner(
        model=RandomForestClassifier(), features=X, labels=y
    )
    gb_scores = _cross_val_score_runner(
        model=GradientBoostingClassifier(), features=X, labels=y
    )

    scores_dict = {
        "Logistic": lr_scores,
        "Random Forest": rf_scores,
        "Gradient Boosting": gb_scores,
    }
    df_folds_scores = pd.DataFrame(scores_dict).round(4).T
    df_folds_scores.columns = [f"Fold {i + 1}" for i in range(df_folds_scores.shape[1])]

    print("===== Fold Scores =====")
    pp(df_folds_scores)

    stats_dict = {
        "mean": df_folds_scores.mean(axis=1),
        "std": df_folds_scores.std(axis=1),
    }
    df_stats = pd.DataFrame(stats_dict)

    print("\n===== Stats (mean & std) =====")
    pp(df_stats)


if __name__ == "__main__":
    main()
