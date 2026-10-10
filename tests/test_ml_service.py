import math
import unittest

import pandas as pd

from services.ml_service import (
    YIELD_FEATURES,
    assess_farmer_risk,
    calculate_crop_repayment_coverage,
    calculate_yield_per_acre,
    compare_yield_scenario,
    predict_total_yield,
)


def farmer_profile(**overrides):
    profile = {
        "loan_amount": 100000,
        "outstanding_loan": 50000,
        "loan_repayment_history": "Mostly on time",
    }
    profile.update(overrides)
    return profile


class RiskAssessmentTests(unittest.TestCase):
    def test_score_boundaries_and_categories(self):
        low = assess_farmer_risk(
            farmer_profile(
                outstanding_loan=0,
                loan_repayment_history="Always on time",
            )
        )
        high = assess_farmer_risk(
            farmer_profile(
                outstanding_loan=100000,
                loan_repayment_history="Frequently delayed",
            )
        )

        self.assertEqual(low["score"], 0)
        self.assertEqual(low["category"], "Low")
        self.assertEqual(high["score"], 100)
        self.assertEqual(high["category"], "High")

    def test_medium_category_and_factor_order_are_farmer_specific(self):
        assessment = assess_farmer_risk(
            farmer_profile(
                outstanding_loan=80000,
                loan_repayment_history="Mostly on time",
            )
        )

        self.assertEqual(assessment["score"], 56.7)
        self.assertEqual(assessment["category"], "Medium")
        self.assertEqual(
            assessment["factors"][0]["name"],
            "Outstanding balance share",
        )
        self.assertEqual(len(assessment["factors"]), 2)
        self.assertIn("Only two available indicators", assessment["additional_factor_status"])

    def test_score_is_repeatable_and_unvalidated_inputs_are_not_claimed_as_models(self):
        profile = farmer_profile()
        first = assess_farmer_risk(profile)
        second = assess_farmer_risk(profile)

        self.assertEqual(first, second)
        self.assertIn("not a default probability", first["score_type"])
        self.assertIn("undocumented", first["excluded_indicators"]["financial_history_score"])
        self.assertIn("is configured", first["weather_warning"])

    def test_missing_invalid_and_unsupported_financial_inputs_raise(self):
        with self.assertRaisesRegex(ValueError, "Missing required risk inputs"):
            assess_farmer_risk(farmer_profile(outstanding_loan=None))
        with self.assertRaisesRegex(ValueError, "greater than zero"):
            assess_farmer_risk(farmer_profile(loan_amount=0))
        with self.assertRaisesRegex(ValueError, "non-negative"):
            assess_farmer_risk(farmer_profile(outstanding_loan=-1))
        with self.assertRaisesRegex(ValueError, "Unsupported repayment history"):
            assess_farmer_risk(farmer_profile(loan_repayment_history="Unknown"))

    def test_recommendations_match_recorded_financial_and_crop_health_factors(self):
        assessment = assess_farmer_risk(
            farmer_profile(
                outstanding_loan=80000,
                loan_repayment_history="1 delayed payment",
                crop_health_index=0.4,
            )
        )

        self.assertEqual(len(assessment["recommendations"]), 3)
        self.assertTrue(any("due dates" in text for text in assessment["recommendations"]))
        self.assertTrue(any("additional borrowing" in text for text in assessment["recommendations"]))
        self.assertTrue(any("field inspection" in text for text in assessment["recommendations"]))


class YieldPredictionTests(unittest.TestCase):
    def test_climate_scenario_compares_profile_with_user_entered_conditions(self):
        class LinearYieldModel:
            def predict(self, values):
                return (
                    values["Rainfall_mm"].to_numpy() / 100
                    + values["Temperature_C"].to_numpy()
                    + values["Soil_Moisture"].to_numpy() / 10
                    + values["Farm_Size_acres"].to_numpy()
                    + values["Crop_Health_Index"].to_numpy()
                )

        farmer = {
            "rainfall_mm": 800,
            "temperature_c": 25,
            "soil_moisture": 60,
            "farm_size_acres": 4,
            "crop_health_index": 0.7,
        }
        result = compare_yield_scenario(
            LinearYieldModel(),
            farmer,
            {
                "Rainfall_mm": 400,
                "Temperature_C": 35,
                "Soil_Moisture": 40,
                "Crop_Health_Index": 0.5,
            },
        )

        self.assertEqual(result["baseline_yield_tons"], 43.7)
        self.assertEqual(result["scenario_yield_tons"], 47.5)
        self.assertAlmostEqual(result["yield_change_tons"], 3.8)
        self.assertEqual(result["factors"][0]["name"], "Temperature")
        self.assertEqual(len(result["factors"]), 3)

    def test_climate_scenario_rejects_invalid_observations(self):
        class LinearYieldModel:
            def predict(self, values):
                return [1.0]

        farmer = {
            "rainfall_mm": 800,
            "temperature_c": 25,
            "soil_moisture": 60,
            "farm_size_acres": 4,
            "crop_health_index": 0.7,
        }
        with self.assertRaisesRegex(ValueError, "soil moisture"):
            compare_yield_scenario(
                LinearYieldModel(), farmer, {"Soil_Moisture": 110}
            )

    def test_crop_repayment_coverage_uses_supplied_same_period_values(self):
        result = calculate_crop_repayment_coverage(
            predicted_yield_tons=10,
            price_per_ton=2000,
            production_costs=5000,
            scheduled_repayment=10000,
        )
        self.assertEqual(result["gross_revenue"], 20000)
        self.assertEqual(result["net_crop_funds"], 15000)
        self.assertEqual(result["coverage_ratio"], 1.5)
        self.assertEqual(result["repayment_shortfall"], 0)

        shortfall = calculate_crop_repayment_coverage(2, 1000, 1500, 1000)
        self.assertEqual(shortfall["net_crop_funds"], 500)
        self.assertEqual(shortfall["repayment_shortfall"], 500)

    def test_crop_repayment_coverage_rejects_missing_or_invalid_values(self):
        with self.assertRaisesRegex(ValueError, "greater than zero"):
            calculate_crop_repayment_coverage(10, 0, 1000, 500)
        with self.assertRaisesRegex(ValueError, "non-negative"):
            calculate_crop_repayment_coverage(10, 1000, -1, 500)

    def test_yield_per_acre_and_invalid_area(self):
        self.assertEqual(calculate_yield_per_acre(12, 4), 3)
        for invalid_area in (0, -1, float("nan"), float("inf")):
            with self.subTest(area=invalid_area):
                with self.assertRaisesRegex(ValueError, "greater than zero"):
                    calculate_yield_per_acre(12, invalid_area)

    def test_prediction_uses_required_feature_schema_and_rejects_missing_columns(self):
        class StubModel:
            def predict(self, values):
                self.columns = list(values.columns)
                return [5.25]

        model = StubModel()
        sample = pd.DataFrame([{name: 1 for name in YIELD_FEATURES}])

        self.assertEqual(predict_total_yield(model, sample), 5.25)
        self.assertEqual(model.columns, YIELD_FEATURES)
        with self.assertRaisesRegex(ValueError, "Missing yield prediction features"):
            predict_total_yield(model, sample.drop(columns=[YIELD_FEATURES[0]]))

    def test_non_finite_model_output_is_rejected(self):
        class StubModel:
            def predict(self, values):
                return [math.nan]

        sample = pd.DataFrame([{name: 1 for name in YIELD_FEATURES}])
        with self.assertRaisesRegex(ValueError, "non-finite"):
            predict_total_yield(StubModel(), sample)


if __name__ == "__main__":
    unittest.main()
