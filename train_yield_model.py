import argparse
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from services.ml_service import DATA_FILE, MODEL_FILE, YIELD_FEATURES

TARGET = "Yield_tons"


def train_yield_model(
    data_path: Path = DATA_FILE,
    artifact_path: Path = MODEL_FILE,
) -> dict[str, float | int]:
    data_path = Path(data_path)
    artifact_path = Path(artifact_path)
    if not data_path.is_file():
        raise FileNotFoundError(f"Training data was not found: {data_path}")

    df = pd.read_csv(data_path)
    required_columns = [*YIELD_FEATURES, TARGET]
    missing_columns = [column for column in required_columns if column not in df]
    if missing_columns:
        raise ValueError(f"Training data is missing columns: {', '.join(missing_columns)}")
    if len(df) < 5:
        raise ValueError("At least five rows with yield labels are required for a holdout.")

    X = df.loc[:, YIELD_FEATURES].apply(pd.to_numeric, errors="coerce")
    X = X.replace([np.inf, -np.inf], np.nan)
    y = pd.to_numeric(df[TARGET], errors="coerce").replace([np.inf, -np.inf], np.nan)
    valid_target = y.notna()
    X, y = X.loc[valid_target], y.loc[valid_target]
    if len(y) < 5:
        raise ValueError("At least five rows with numeric Yield_tons targets are required.")
    if (y < 0).any():
        raise ValueError("Yield_tons must be non-negative.")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )
    model = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median", keep_empty_features=True)),
            (
                "regressor",
                RandomForestRegressor(
                    n_estimators=300,
                    min_samples_leaf=2,
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    metrics = {
        "mae": float(mean_absolute_error(y_test, predictions)),
        "rmse": float(mean_squared_error(y_test, predictions) ** 0.5),
        "r2": float(r2_score(y_test, predictions)),
        "test_rows": int(len(y_test)),
    }

    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "feature_cols": YIELD_FEATURES,
            "target": TARGET,
            "metrics": metrics,
            "split": {"test_size": 0.2, "random_state": 42},
            "training_rows": int(len(y_train)),
            "trained_at_utc": datetime.now(timezone.utc).isoformat(),
            "dataset_note": (
                "The bundled training dataset is generated sample data; holdout "
                "metrics are not real-world agricultural or credit-risk validation."
            ),
        },
        artifact_path,
    )
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train and holdout-evaluate the AgriShield crop-yield model."
    )
    parser.add_argument("--data", type=Path, default=DATA_FILE)
    parser.add_argument("--output", type=Path, default=MODEL_FILE)
    args = parser.parse_args()

    metrics = train_yield_model(args.data, args.output)
    print("Yield model holdout evaluation (80/20 split, random_state=42):")
    print(f"  MAE:      {metrics['mae']:.4f} tons")
    print(f"  RMSE:     {metrics['rmse']:.4f} tons")
    print(f"  R-squared:{metrics['r2']:.4f}")
    print(f"  Test rows:{metrics['test_rows']}")
    print(
        "Warning: these results evaluate the supplied dataset only. "
        "The checked-in sample data is synthetic, so this is not real-world validation."
    )
    print(f"Saved yield model to: {args.output.resolve()}")


if __name__ == "__main__":
    main()
