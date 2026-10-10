import streamlit as st

from services.ml_service import assess_farmer_risk
from ui.climate_yield_assessment import render_climate_yield_assessment
from ui.farmer_profile import select_dataset_farmer
from ui.style import apply_theme

st.set_page_config(page_title="Climate & Repayment Assessment", layout="wide")
apply_theme()

farmer = select_dataset_farmer("bank_risk_assessment_profile")
st.title("Climate & Repayment Assessment")
st.write(
    "Use an ML yield estimate and farmer-specific climate scenarios alongside "
    "available financial records."
)
st.warning(
    "The dataset contains generated sample rows, not verified borrower records. "
    "There are no real repayment outcomes, live weather forecasts, satellite feeds, "
    "or crop market and cost data. A validated repayment probability cannot be trained "
    "from this dataset."
)

st.subheader("Selected borrower and farm")
profile_columns = st.columns(4)
profile_columns[0].metric("Farmer", farmer["farmer_name"])
profile_columns[1].metric("Crop", farmer["crop_type"])
profile_columns[2].metric("Farm size", f"{farmer['farm_size_acres']:.2f} acres")
profile_columns[3].metric("Outstanding balance", f"₹{farmer['outstanding_loan']:,.0f}")

try:
    financial_indicator = assess_farmer_risk(farmer)
except ValueError as exc:
    st.info(f"Provisional financial indicator unavailable: {exc}")
else:
    st.subheader("Recorded financial history (provisional indicator)")
    financial_columns = st.columns(3)
    financial_columns[0].metric(
        "Indicator",
        f"{financial_indicator['score']:.1f} / 100",
        financial_indicator["category"],
    )
    financial_columns[1].metric(
        "Repayment history",
        farmer["loan_repayment_history"],
    )
    financial_columns[2].metric(
        "Outstanding / original loan",
        f"{farmer['outstanding_loan'] / farmer['loan_amount']:.1%}",
    )
    st.caption(
        "This transparent, unvalidated indicator uses repayment-history category "
        "and loan-balance share. It is not an ML classification or default probability."
    )

render_climate_yield_assessment(farmer, "bank_climate_risk_assessment")

st.subheader("What a validated climate-adjusted credit model needs")
st.write(
    "Real, time-stamped repayment outcomes linked to pre-decision borrower data, "
    "verified forecast and satellite observations, crop-season and location baselines, "
    "measured yields, crop prices and production costs, and scheduled repayments. "
    "Until those labels are available, the ML result above is a crop-yield estimate "
    "for decision support—not a credit-risk probability."
)
