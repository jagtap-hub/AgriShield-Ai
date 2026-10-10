from collections.abc import Mapping
from functools import lru_cache
from math import isfinite
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "crop_data.csv"
MODEL_FILE = PROJECT_ROOT / "artifacts" / "yield_model.joblib"

YIELD_FEATURES = [
    "Rainfall_mm",
    "Temperature_C",
    "Soil_Moisture",
    "Farm_Size_acres",
    "Crop_Health_Index",
]

_REPAYMENT_RISK = {
    "always on time": 0.0,
    "mostly on time": 33.3333333333,
    "1 delayed payment": 66.6666666667,
    "frequently delayed": 100.0,
}


@lru_cache(maxsize=1)
def get_model_and_data():
    """Load the separately trained yield model and its current source data."""
    if not DATA_FILE.is_file():
        raise FileNotFoundError(f"Yield training data was not found: {DATA_FILE}")
    if not MODEL_FILE.is_file():
        raise FileNotFoundError(
            "The yield model has not been trained yet. Run "
            "'python train_yield_model.py' from the project folder."
        )

    df = pd.read_csv(DATA_FILE)
    artifact = joblib.load(MODEL_FILE)
    if artifact.get("feature_cols") != YIELD_FEATURES:
        raise ValueError("The saved yield model uses an unexpected feature schema.")

    return artifact["model"], df, YIELD_FEATURES.copy()


def predict_total_yield(model: Any, input_data: pd.DataFrame) -> float:
    """Predict total production in tons using the saved yield model."""
    missing = [feature for feature in YIELD_FEATURES if feature not in input_data]
    if missing:
        raise ValueError(f"Missing yield prediction features: {', '.join(missing)}")

    values = input_data.loc[:, YIELD_FEATURES].apply(pd.to_numeric, errors="coerce")
    prediction = float(model.predict(values)[0])
    if not isfinite(prediction):
        raise ValueError("Yield model returned a non-finite prediction.")
    return max(0.0, prediction)


def compare_yield_scenario(
    model: Any,
    farmer: Mapping[str, Any],
    scenario: Mapping[str, Any],
) -> dict[str, Any]:
    """Compare an entered weather scenario with the selected dataset conditions."""
    dataset_fields = {
        "Rainfall_mm": "rainfall_mm",
        "Temperature_C": "temperature_c",
        "Soil_Moisture": "soil_moisture",
        "Farm_Size_acres": "farm_size_acres",
        "Crop_Health_Index": "crop_health_index",
    }
    baseline = {}
    for feature, field in dataset_fields.items():
        try:
            value = float(farmer[field])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Missing or invalid farmer scenario input: {field}.") from exc
        if not isfinite(value):
            raise ValueError(f"Farmer scenario input {field} must be finite.")
        baseline[feature] = value

    scenario_values = baseline.copy()
    for feature in ("Rainfall_mm", "Temperature_C", "Soil_Moisture", "Crop_Health_Index"):
        if feature in scenario:
            try:
                value = float(scenario[feature])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Scenario input {feature} must be numeric.") from exc
            if not isfinite(value):
                raise ValueError(f"Scenario input {feature} must be finite.")
            scenario_values[feature] = value

    if scenario_values["Rainfall_mm"] < 0:
        raise ValueError("Scenario rainfall must be non-negative.")
    if not 0 <= scenario_values["Soil_Moisture"] <= 100:
        raise ValueError("Scenario soil moisture must be between 0 and 100.")
    if not 0 <= scenario_values["Crop_Health_Index"] <= 1:
        raise ValueError("Scenario crop health index must be between 0 and 1.")
    if baseline["Farm_Size_acres"] <= 0:
        raise ValueError("Farmer farm size must be greater than zero.")

    baseline_frame = pd.DataFrame([baseline], columns=YIELD_FEATURES)
    scenario_frame = pd.DataFrame([scenario_values], columns=YIELD_FEATURES)
    baseline_yield = predict_total_yield(model, baseline_frame)
    scenario_yield = predict_total_yield(model, scenario_frame)

    factors = []
    labels = {
        "Rainfall_mm": "Rainfall",
        "Temperature_C": "Temperature",
        "Soil_Moisture": "Soil moisture",
        "Crop_Health_Index": "Crop-health proxy",
    }
    for feature, label in labels.items():
        if baseline[feature] == scenario_values[feature]:
            continue
        isolated_values = baseline.copy()
        isolated_values[feature] = scenario_values[feature]
        isolated_yield = predict_total_yield(
            model,
            pd.DataFrame([isolated_values], columns=YIELD_FEATURES),
        )
        factors.append(
            {
                "name": label,
                "baseline_value": baseline[feature],
                "scenario_value": scenario_values[feature],
                "isolated_yield_change_tons": round(isolated_yield - baseline_yield, 3),
            }
        )
    factors.sort(
        key=lambda factor: abs(factor["isolated_yield_change_tons"]),
        reverse=True,
    )

    change_tons = scenario_yield - baseline_yield
    change_percent = (
        (change_tons / baseline_yield) * 100 if baseline_yield > 0 else None
    )
    return {
        "baseline_yield_tons": baseline_yield,
        "scenario_yield_tons": scenario_yield,
        "yield_change_tons": change_tons,
        "yield_change_percent": change_percent,
        "factors": factors[:3],
        "baseline_inputs": baseline,
        "scenario_inputs": scenario_values,
    }


def calculate_crop_repayment_coverage(
    predicted_yield_tons: float,
    price_per_ton: float,
    production_costs: float,
    scheduled_repayment: float,
) -> dict[str, float]:
    """Estimate crop-funded repayment coverage from user-entered same-period values."""
    try:
        values = {
            "predicted yield": float(predicted_yield_tons),
            "market price": float(price_per_ton),
            "production costs": float(production_costs),
            "scheduled repayment": float(scheduled_repayment),
        }
    except (TypeError, ValueError) as exc:
        raise ValueError("Yield and financial inputs must be numeric.") from exc
    if any(not isfinite(value) for value in values.values()):
        raise ValueError("Yield and financial inputs must be finite.")
    if values["predicted yield"] < 0:
        raise ValueError("Predicted yield must be non-negative.")
    if values["market price"] <= 0:
        raise ValueError("Market price must be greater than zero.")
    if values["production costs"] < 0:
        raise ValueError("Production costs must be non-negative.")
    if values["scheduled repayment"] <= 0:
        raise ValueError("Scheduled repayment must be greater than zero.")

    gross_revenue = values["predicted yield"] * values["market price"]
    net_crop_funds = gross_revenue - values["production costs"]
    coverage_ratio = net_crop_funds / values["scheduled repayment"]
    return {
        "gross_revenue": gross_revenue,
        "net_crop_funds": net_crop_funds,
        "coverage_ratio": coverage_ratio,
        "repayment_shortfall": max(0.0, values["scheduled repayment"] - net_crop_funds),
    }


def get_yield_feature_importances(model: Any) -> list[float]:
    """Return global tree importances for yield prediction, not risk attribution."""
    try:
        return model.named_steps["regressor"].feature_importances_.tolist()
    except (AttributeError, KeyError) as exc:
        raise ValueError("Loaded yield model does not expose Random Forest importances.") from exc


def get_yield_model_metadata() -> dict[str, Any]:
    """Return holdout metrics and feature schema saved with the trained artifact."""
    get_model_and_data()
    artifact = joblib.load(MODEL_FILE)
    return {
        "target": artifact.get("target", "Yield_tons"),
        "feature_cols": artifact.get("feature_cols", YIELD_FEATURES.copy()),
        "metrics": artifact.get("metrics", {}),
        "training_rows": artifact.get("training_rows"),
        "trained_at_utc": artifact.get("trained_at_utc"),
        "dataset_note": artifact.get(
            "dataset_note",
            "Metrics reflect the supplied dataset only; bundled data is synthetic.",
        ),
    }


def calculate_yield_per_acre(predicted_total_yield: float, cultivated_area: float) -> float:
    """Convert total predicted tons to tons per acre, rejecting invalid area."""
    try:
        yield_value = float(predicted_total_yield)
        area = float(cultivated_area)
    except (TypeError, ValueError) as exc:
        raise ValueError("Yield and cultivated area must be numeric.") from exc

    if not isfinite(yield_value) or yield_value < 0:
        raise ValueError("Predicted total yield must be finite and non-negative.")
    if not isfinite(area) or area <= 0:
        raise ValueError("Cultivated area must be finite and greater than zero.")
    return yield_value / area


def assess_farmer_risk(farmer: Mapping[str, Any]) -> dict[str, Any]:
    """Return an explicitly provisional, deterministic financial indicator score.

    The two available inputs are equally averaged for transparency. These are
    design assumptions, not weights learned or validated against default data.
    """
    required = ("loan_amount", "outstanding_loan", "loan_repayment_history")
    missing = [
        name
        for name in required
        if farmer.get(name) is None or str(farmer.get(name)).strip() == ""
    ]
    if missing:
        raise ValueError(f"Missing required risk inputs: {', '.join(missing)}")

    try:
        loan_amount = float(farmer["loan_amount"])
        outstanding_loan = float(farmer["outstanding_loan"])
    except (TypeError, ValueError) as exc:
        raise ValueError("Loan amount and outstanding balance must be numeric.") from exc

    if not isfinite(loan_amount) or loan_amount <= 0:
        raise ValueError("Loan amount must be finite and greater than zero.")
    if not isfinite(outstanding_loan) or outstanding_loan < 0:
        raise ValueError("Outstanding balance must be finite and non-negative.")

    repayment_label = str(farmer["loan_repayment_history"]).strip()
    repayment_risk = _REPAYMENT_RISK.get(repayment_label.casefold())
    if repayment_risk is None:
        supported = ", ".join(_REPAYMENT_RISK)
        raise ValueError(
            f"Unsupported repayment history {repayment_label!r}; "
            f"expected one of: {supported}."
        )

    raw_exposure_percent = outstanding_loan / loan_amount * 100.0
    exposure_risk = min(raw_exposure_percent, 100.0)
    score = round((repayment_risk + exposure_risk) / 2.0, 1)
    if score < 34:
        category = "Low"
    elif score < 67:
        category = "Medium"
    else:
        category = "High"

    factors = [
        {
            "name": "Repayment history",
            "observed_value": repayment_label,
            "comparison": (
                "Ordered provisional scale: always on time (0), mostly on time "
                "(33.3), one delayed payment (66.7), frequently delayed (100)."
            ),
            "component_score": round(repayment_risk, 1),
            "impact_points": round(repayment_risk / 2.0, 1),
            "explanation": (
                f"This history maps to {repayment_risk:.1f}/100 on the disclosed "
                "provisional scale and contributes half of that amount to the score."
            ),
        },
        {
            "name": "Outstanding balance share",
            "observed_value": f"{raw_exposure_percent:.1f}% of original loan",
            "comparison": (
                "Calculated as outstanding balance / original loan amount; "
                "the component is capped at 100. This is exposure, not repayment capacity."
            ),
            "component_score": round(exposure_risk, 1),
            "impact_points": round(exposure_risk / 2.0, 1),
            "explanation": (
                f"The balance share contributes {exposure_risk / 2.0:.1f} points "
                "under the provisional equal-weight formula."
            ),
        },
    ]
    factors.sort(key=lambda factor: factor["impact_points"], reverse=True)

    recommendations = []
    if repayment_risk >= _REPAYMENT_RISK["1 delayed payment"]:
        recommendations.append(
            "Review upcoming due dates and contact the lender early to discuss "
            "available repayment support if a payment may be missed."
        )
    if raw_exposure_percent >= 70:
        recommendations.append(
            "Review the outstanding balance alongside actual instalments and "
            "cash flow before taking on additional borrowing."
        )
    if not recommendations:
        recommendations.append(
            "Keep repayment records current and review instalment timing against "
            "seasonal farm cash flow."
        )

    crop_health = farmer.get("crop_health_index")
    if crop_health is not None:
        try:
            crop_health_value = float(crop_health)
        except (TypeError, ValueError):
            crop_health_value = float("nan")
        if isfinite(crop_health_value) and crop_health_value < 0.55:
            recommendations.append(
                "The recorded crop-health proxy is low; verify it with a current "
                "field inspection or calibrated imagery and seek local agronomic advice."
            )

    return {
        "score": score,
        "category": category,
        "score_type": "provisional financial indicator; not a default probability",
        "method": (
            "Arithmetic mean of the ordinal repayment-history score and outstanding "
            "balance share, with equal 50% contributions. This unvalidated formula is "
            "for decision support only."
        ),
        "category_thresholds": {"low": "0-33.9", "medium": "34-66.9", "high": "67-100"},
        "factors": factors,
        "additional_factor_status": (
            "Only two available indicators are scored. The third contributing factor "
            "cannot be estimated reliably from this dataset."
        ),
        "excluded_indicators": {
            "financial_history_score": (
                "Not scored because its definition, direction, and scale are undocumented."
            ),
            "yield_and_weather": (
                "Not scored as credit risk: no verified crop-season/location baseline, "
                "crop revenue or costs, repayment capacity, or actual repayment labels."
            ),
        },
        "weather_warning": (
            "Unavailable: no live, location-specific weather provider is configured. "
            "Stored weather values are sample/synthetic data, not current observations or forecasts."
        ),
        "recommendations": recommendations,
    }
