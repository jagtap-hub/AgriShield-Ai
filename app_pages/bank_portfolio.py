import pandas as pd
import streamlit as st

from services.db_service import fetch_all_farmers

st.title("Farmer & Loan Portfolio")
st.write("Inspect farmer profiles and loan fields currently available in the configured data source.")

farmers = fetch_all_farmers()
if not farmers:
    st.info("No farmer records are available from the configured data source.")
    st.stop()

st.warning(
    "The bundled farmer records are generated sample data. Loan schedules, payment dates, "
    "field verification, insurance, and current weather feeds are not stored."
)

farmer_options = {
    f"{farmer['farmer_id']} - {farmer['farmer_name']}": farmer
    for farmer in farmers
}
selected_label = st.selectbox("Select Farmer", list(farmer_options))
farmer = farmer_options[selected_label]

st.markdown(f"### Borrower Profile: {farmer['farmer_name']} ({farmer['farmer_id']})")
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Original Loan Amount", f"₹{farmer['loan_amount']:,.0f}")
with m2:
    st.metric("Outstanding Balance", f"₹{farmer['outstanding_loan']:,.0f}")
with m3:
    st.metric("Financial History Score", farmer["financial_history_score"])
with m4:
    st.metric("Repayment History", farmer["loan_repayment_history"])

st.markdown("### Farm & Crop Fields")
st.dataframe(
    pd.DataFrame(
        [
            {"Field": "Crop type", "Value": farmer["crop_type"]},
            {"Field": "Farm size (acres)", "Value": farmer["farm_size_acres"]},
            {"Field": "Irrigation type", "Value": farmer["irrigation_type"]},
            {"Field": "Soil type", "Value": farmer["soil_type"]},
            {"Field": "Historical yield (dataset units)", "Value": farmer["historical_yield"]},
            {"Field": "Previous yield (dataset units)", "Value": farmer["previous_yield"]},
            {"Field": "Recorded yield (total tons)", "Value": farmer["yield_tons"]},
        ]
    ),
    use_container_width=True,
    hide_index=True,
)

st.markdown("### Climate Fields (sample data)")
st.dataframe(
    pd.DataFrame(
        [
            {"Field": "Rainfall (mm)", "Value": farmer["rainfall_mm"]},
            {"Field": "Temperature (°C)", "Value": farmer["temperature_c"]},
            {"Field": "Soil moisture", "Value": farmer["soil_moisture"]},
            {"Field": "Crop health index", "Value": farmer["crop_health_index"]},
        ]
    ),
    use_container_width=True,
    hide_index=True,
)
st.info(
    "Verified instalment schedule and repayment dates are unavailable. "
    "The repayment-history field is a generated sample category, not an observed payment ledger."
)
