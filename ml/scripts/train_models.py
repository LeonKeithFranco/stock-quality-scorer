from pprint import pp

import pandas as pd
from anyio.functools import lru_cache
from sklearn.base import ClassifierMixin
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from scripts.utils import get_training_data_path


@lru_cache
def _get_features_and_labels() -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_parquet(get_training_data_path())

    X = df.drop(columns=["ticker", "beatSnp500"])
    y = df["beatSnp500"]

    return X, y


def _cross_val_score_runner(
    model: ClassifierMixin, skf: StratifiedKFold = StratifiedKFold(n_splits=5)
):
    X, y = _get_features_and_labels()

    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()

    pipeline = Pipeline([("imputer", imputer), ("scaler", scaler), ("model", model)])

    return cross_val_score(pipeline, X, y, cv=skf, scoring="roc_auc")


def main():
    lr_scores = _cross_val_score_runner(model=LogisticRegression())
    rf_scores = _cross_val_score_runner(model=RandomForestClassifier())
    gb_scores = _cross_val_score_runner(model=GradientBoostingClassifier())

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
