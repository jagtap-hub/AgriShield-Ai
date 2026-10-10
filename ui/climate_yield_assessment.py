import math
from typing import Any

import pandas as pd
import streamlit as st

from services.ml_service import (
    calculate_crop_repayment_coverage,
    calculate_yield_per_acre,
    compare_yield_scenario,
    get_model_and_data,
    get_yield_feature_importances,
    get_yield_model_metadata,
)


def _show_model_details(model: Any, metadata: dict[str, Any]) -> None:
    metrics = metadata["metrics"]
    st.markdown("**Trained ML model**")
    st.write("Random Forest regression · Target: total crop production (`Yield_tons`).")
    if metrics:
        cols = st.columns(4)
        cols[0].metric("Test MAE", f"{metrics['mae']:.2f} tons")
        cols[1].metric("Test RMSE", f"{metrics['rmse']:.2f} tons")
        cols[2].metric("Test R²", f"{metrics['r2']:.3f}")
        cols[3].metric("Test rows", str(metrics["test_rows"]))
    st.caption(
        f"Model trained on {metadata.get('training_rows') or 'recorded'} training "
        "rows. Metrics measure fit to the supplied sample dataset only; they are "
        "not real-world or repayment-risk validation."
    )
    importance_values = get_yield_feature_importances(model)
    importance = pd.DataFrame(
        {"Feature": metadata["feature_cols"], "Yield model importance": importance_values}
    ).sort_values("Yield model importance", ascending=False)
    st.dataframe(importance, use_container_width=True, hide_index=True)


def render_climate_yield_assessment(
    farmer: dict[str, Any],
    key_prefix: str,
) -> dict[str, Any] | None:
    """Render a farmer-specific ML yield scenario and optional repayment coverage."""
    profile_key = f"{key_prefix}_{farmer['farmer_id']}"
    try:
        model, _, _ = get_model_and_data()
        metadata = get_yield_model_metadata()
    except (FileNotFoundError, ValueError) as exc:
        st.error(f"The trained yield model is unavailable: {exc}")
        return None

    st.subheader("AI/ML crop and climate scenario")
    st.caption(
        "Select a farmer, then adjust the climate inputs to see how the trained "
        "yield model responds. The saved weather values are generated sample data; "
        "scenario inputs are not forecasts."
    )

    with st.form(f"{profile_key}_climate_scenario"):
        first, second = st.columns(2)
        with first:
            rainfall = st.slider(
                "Scenario rainfall (mm)",
                0.0,
                3000.0,
                float(farmer["rainfall_mm"]),
                step=10.0,
                key=f"{profile_key}_rainfall",
            )
            temperature = st.slider(
                "Scenario temperature (°C)",
                -10.0,
                60.0,
                float(farmer["temperature_c"]),
                step=0.5,
                key=f"{profile_key}_temperature",
            )
        with second:
            soil_moisture = st.slider(
                "Scenario soil moisture (%)",
                0.0,
                100.0,
                float(farmer["soil_moisture"]),
                step=1.0,
                key=f"{profile_key}_soil_moisture",
            )
            crop_health = st.slider(
                "Crop-health proxy (0-1)",
                0.0,
                1.0,
                float(farmer["crop_health_index"]),
                step=0.01,
                key=f"{profile_key}_crop_health",
            )
        run_scenario = st.form_submit_button(
            "Estimate climate-adjusted crop yield", type="primary"
        )

    finance_inputs: tuple[float, float, float] | None = None
    with st.expander("Optional: estimate crop-funded repayment coverage"):
        st.caption(
            "Enter values for the same crop and repayment period. The dataset does "
            "not contain current market prices, production costs, or scheduled installments."
        )
        include_financial_estimate = st.checkbox(
            "I have values for this period",
            key=f"{profile_key}_include_finance",
        )
        if include_financial_estimate:
            price_col, cost_col, repayment_col = st.columns(3)
            price = price_col.number_input(
                "Crop price (₹ per ton)",
                min_value=0.0,
                value=0.0,
                step=100.0,
                key=f"{profile_key}_crop_price",
            )
            costs = cost_col.number_input(
                "Crop production costs (₹)",
                min_value=0.0,
                value=0.0,
                step=1000.0,
                key=f"{profile_key}_crop_costs",
            )
            repayment = repayment_col.number_input(
                "Scheduled repayment (₹)",
                min_value=0.0,
                value=0.0,
                step=1000.0,
                key=f"{profile_key}_scheduled_repayment",
            )
            finance_inputs = (price, costs, repayment)

    result_key = f"{profile_key}_last_climate_result"
    if run_scenario:
        try:
            scenario_result = compare_yield_scenario(
                model,
                farmer,
                {
                    "Rainfall_mm": rainfall,
                    "Temperature_C": temperature,
                    "Soil_Moisture": soil_moisture,
                    "Crop_Health_Index": crop_health,
                },
            )
            scenario_result["farmer_id"] = farmer["farmer_id"]
        except (KeyError, TypeError, ValueError) as exc:
            st.error(f"Could not estimate this scenario: {exc}")
        else:
            st.session_state[result_key] = scenario_result

    scenario_result = st.session_state.get(result_key)
    if scenario_result and scenario_result["farmer_id"] == farmer["farmer_id"]:
        baseline_yield = scenario_result["baseline_yield_tons"]
        scenario_yield = scenario_result["scenario_yield_tons"]
        yield_change = scenario_result["yield_change_tons"]
        percent_change = scenario_result["yield_change_percent"]

        st.markdown("### Model estimate")
        metric_cols = st.columns(4)
        metric_cols[0].metric("Selected-record yield estimate", f"{baseline_yield:.2f} tons")
        metric_cols[1].metric("Entered-scenario yield estimate", f"{scenario_yield:.2f} tons")
        percent_label = (
            f"{percent_change:+.1f}% vs record"
            if percent_change is not None
            else "Baseline prediction is zero"
        )
        metric_cols[2].metric(
            "Scenario yield change",
            f"{yield_change:+.2f} tons",
            delta=percent_label,
        )
        try:
            scenario_yield_per_acre = calculate_yield_per_acre(
                scenario_yield, farmer["farm_size_acres"]
            )
            metric_cols[3].metric(
                "Scenario yield per acre",
                f"{scenario_yield_per_acre:.2f} tons/acre",
            )
        except (TypeError, ValueError) as exc:
            st.warning(f"Yield per acre unavailable: {exc}")

        if scenario_result["factors"]:
            st.markdown("**Largest model sensitivities in this scenario**")
            sensitivity_rows = [
                {
                    "Input": factor["name"],
                    "Selected-record value": factor["baseline_value"],
                    "Scenario value": factor["scenario_value"],
                    "Isolated yield change (tons)": factor["isolated_yield_change_tons"],
                }
                for factor in scenario_result["factors"]
            ]
            st.dataframe(
                sensitivity_rows,
                use_container_width=True,
                hide_index=True,
            )
            st.caption(
                "These are one-input-at-a-time model sensitivities, not causal effects. "
                "The model has no crop-specific, location-specific, or seasonal calibration."
            )
        else:
            st.info("Scenario inputs match the selected record; no input changed.")

        if finance_inputs is not None:
            price, costs, repayment = finance_inputs
            if price <= 0 or repayment <= 0:
                st.info(
                    "Enter a positive crop price and scheduled repayment to estimate "
                    "repayment coverage. Use actual figures for the same period."
                )
            else:
                try:
                    baseline_coverage = calculate_crop_repayment_coverage(
                        baseline_yield, price, costs, repayment
                    )
                    scenario_coverage = calculate_crop_repayment_coverage(
                        scenario_yield, price, costs, repayment
                    )
                except ValueError as exc:
                    st.error(f"Repayment coverage unavailable: {exc}")
                else:
                    st.markdown("### Estimated crop-funded repayment capacity")
                    capacity_cols = st.columns(3)
                    capacity_cols[0].metric(
                        "Scenario gross crop revenue",
                        f"₹{scenario_coverage['gross_revenue']:,.0f}",
                    )
                    capacity_cols[1].metric(
                        "Scenario funds after crop costs",
                        f"₹{scenario_coverage['net_crop_funds']:,.0f}",
                    )
                    capacity_cols[2].metric(
                        "Funds / scheduled repayment",
                        f"{scenario_coverage['coverage_ratio']:.2f}x",
                    )
                    if scenario_coverage["repayment_shortfall"] > 0:
                        st.warning(
                            "Under the entered scenario, crop funds are below the "
                            "entered repayment by "
                            f"₹{scenario_coverage['repayment_shortfall']:,.0f}. "
                            "This is not a default probability or a lending decision."
                        )
                    else:
                        st.info(
                            "Under the entered scenario, estimated crop funds cover "
                            "the entered repayment. This does not assess household "
                            "costs, other income, or overall ability to repay."
                        )
                    if not math.isclose(
                        baseline_coverage["net_crop_funds"],
                        scenario_coverage["net_crop_funds"],
                    ):
                        st.caption(
                            "Scenario crop funds change by "
                            f"₹{scenario_coverage['net_crop_funds'] - baseline_coverage['net_crop_funds']:,.0f} "
                            "relative to the selected-record inputs."
                        )

    with st.expander("About model training and evaluation"):
        _show_model_details(model, metadata)
        st.caption(metadata["dataset_note"])

    return scenario_result if scenario_result and scenario_result["farmer_id"] == farmer["farmer_id"] else None
