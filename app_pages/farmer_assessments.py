import streamlit as st

from services.ml_service import assess_farmer_risk
from ui.farmer_profile import select_dataset_farmer
from ui.style import apply_theme

st.set_page_config(page_title="Assessments & Alerts", layout="wide")
apply_theme()

farmer = select_dataset_farmer("farmer_assessments_profile")
st.title("My Assessment & Alerts")

try:
    assessment = assess_farmer_risk(farmer)
except ValueError as exc:
    st.error(f"Assessment unavailable for this profile: {exc}")
else:
    st.subheader("Provisional financial indicator")
    st.metric(
        "Risk indicator",
        f"{assessment['score']:.1f} / 100",
        assessment["category"],
    )
    st.caption(
        "This is an unvalidated decision-support indicator, not a default probability "
        "or credit decision. It equally averages repayment-history category and "
        "outstanding balance as a share of original loan."
    )
    st.dataframe(
        [
            {
                "Factor": factor["name"],
                "Observed value": factor["observed_value"],
                "Score contribution": factor["impact_points"],
            }
            for factor in assessment["factors"]
        ],
        use_container_width=True,
        hide_index=True,
    )

st.markdown("---")
st.subheader("Weather notifications")
st.info(
    "Unavailable: no live weather observations or forecast provider is connected. "
    "Stored weather values are synthetic sample data, not alerts."
)
st.caption("Assessment history is not stored; this result is calculated for the selected profile.")
