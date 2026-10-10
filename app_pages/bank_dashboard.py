import streamlit as st
import pandas as pd
from ui.components import metric_card
from services.db_service import fetch_all_farmers
from services.ml_service import assess_farmer_risk

st.title("Banking Dashboard")
user = st.session_state.get("bank_user")
if user:
    st.write(f"Branch Overview — **{user.get('branch', 'Unspecified branch')}** | Officer: **{user.get('name', 'Signed-in user')}**")
else:
    st.write("Portfolio overview — no signed-in officer or branch context is available.")

farmer_profiles = fetch_all_farmers()
assessment_rows = []
assessed_categories = []
for profile in farmer_profiles:
    try:
        assessment = assess_farmer_risk(profile)
    except ValueError as exc:
        assessment = None
        assessment_error = str(exc)
    else:
        assessment_error = ""
        assessed_categories.append(assessment["category"])
    assessment_rows.append(
        {
            "Farmer ID": profile.get("farmer_id", "Unavailable"),
            "Farmer Name": profile.get("farmer_name", "Unavailable"),
            "Loan Amount": profile.get("loan_amount"),
            "Provisional Score": assessment["score"] if assessment else None,
            "Category": assessment["category"] if assessment else "Not scored",
            "Status": "Available indicators" if assessment else assessment_error,
        }
    )

st.markdown("### Key Portfolio Indicators")
m1, m2, m3, m4 = st.columns(4)
with m1:
    metric_card("Farmer Profiles", str(len(farmer_profiles)), "👨‍🌾", "Loaded from configured data source")
with m2:
    metric_card("Saved Assessments", "Unavailable", "⏳", "Assessment history is not stored")
with m3:
    metric_card("High Provisional Indicators", str(assessed_categories.count("High")), "⚠️", "Human review required")
with m4:
    metric_card("Field Audits", "Unavailable", "📡", "No field-audit source is connected")

st.markdown("---")

c1, c2 = st.columns([2, 1])

with c1:
    st.markdown("### Farmer Profiles & Provisional Indicators")
    st.caption(
        "Scores are calculated from available repayment-history and balance-share fields. "
        "They are not validated default probabilities; source records may be synthetic."
    )
    st.dataframe(pd.DataFrame(assessment_rows), use_container_width=True, hide_index=True)

with c2:
    st.markdown("### ⚡ Quick Officer Actions")
    st.button("🛡️ Perform AI Risk Assessment", type="primary", use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("📡 Dispatch Field Inspection", type="secondary", use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("📝 Log Credit Decision", type="secondary", use_container_width=True)

st.markdown("---")
st.markdown("### 🔔 Branch Weather Warnings")
st.info("Unavailable: no verified, location-specific weather source is configured.")
