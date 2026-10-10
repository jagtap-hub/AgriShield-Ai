import tempfile
import unittest
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from services.ml_service import YIELD_FEATURES
from train_yield_model import train_yield_model


class YieldTrainingTests(unittest.TestCase):
    def test_training_uses_holdout_and_saves_predictive_pipeline(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_path = root / "sample.csv"
            artifact_path = root / "models" / "yield.joblib"
            rows = []
            for index in range(40):
                row = {feature: float(index + position) for position, feature in enumerate(YIELD_FEATURES)}
                row["Yield_tons"] = 0.25 * row["Farm_Size_acres"] + 0.1 * row["Soil_Moisture"]
                if index == 3:
                    row["Rainfall_mm"] = np.nan
                rows.append(row)
            pd.DataFrame(rows).to_csv(data_path, index=False)

            metrics = train_yield_model(data_path, artifact_path)
            artifact = joblib.load(artifact_path)

        self.assertGreater(metrics["test_rows"], 0)
        self.assertGreaterEqual(metrics["mae"], 0)
        self.assertGreaterEqual(metrics["rmse"], 0)
        self.assertTrue(np.isfinite(metrics["r2"]))
        self.assertEqual(artifact["feature_cols"], YIELD_FEATURES)
        self.assertEqual(artifact["target"], "Yield_tons")
        self.assertEqual(artifact["split"]["random_state"], 42)
        self.assertEqual(artifact["training_rows"], 32)
        self.assertIn("generated sample data", artifact["dataset_note"])
        self.assertTrue(artifact["trained_at_utc"].endswith("+00:00"))
        self.assertTrue(hasattr(artifact["model"].named_steps["imputer"], "statistics_"))
        self.assertTrue(hasattr(artifact["model"].named_steps["regressor"], "feature_importances_"))
        prediction_input = pd.DataFrame([{feature: 1.0 for feature in YIELD_FEATURES}])
        prediction_input.loc[0, "Rainfall_mm"] = np.nan
        self.assertTrue(np.isfinite(artifact["model"].predict(prediction_input)[0]))

    def test_bad_target_and_missing_features_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_path = Path(temp_dir) / "bad.csv"
            rows = [{feature: 1.0 for feature in YIELD_FEATURES} for _ in range(8)]
            for row in rows:
                row["Yield_tons"] = -1
            pd.DataFrame(rows).to_csv(data_path, index=False)

            with self.assertRaisesRegex(ValueError, "non-negative"):
                train_yield_model(data_path, Path(temp_dir) / "model.joblib")

            pd.DataFrame({"Yield_tons": [1, 2, 3, 4, 5]}).to_csv(data_path, index=False)
            with self.assertRaisesRegex(ValueError, "missing columns"):
                train_yield_model(data_path, Path(temp_dir) / "model.joblib")


if __name__ == "__main__":
    unittest.main()
