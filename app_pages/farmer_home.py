import streamlit as st

from ui.farmer_profile import select_dataset_farmer
from ui.farmer_notifications import render_farmer_loan_notifications
from ui.style import apply_theme

st.set_page_config(page_title="Farmer Dashboard", layout="wide")
apply_theme()

farmer = select_dataset_farmer("farmer_home_profile")
st.title(f"Welcome, {farmer['farmer_name']}")
st.write("A summary of the selected farmer profile in the project dataset.")
render_farmer_loan_notifications(str(farmer["farmer_id"]))

left, right = st.columns(2)
with left:
    st.subheader("Farm profile")
    st.metric("Crop", farmer["crop_type"])
    st.metric("Farm size", f"{farmer['farm_size_acres']:.2f} acres")
    st.metric("Irrigation", farmer["irrigation_type"])
    st.metric("Soil type", farmer["soil_type"])
with right:
    st.subheader("Recorded sample indicators")
    st.metric("Crop health index (0-1)", f"{farmer['crop_health_index']:.2f}")
    st.metric("Historical yield", f"{farmer['historical_yield']:.2f} tons")
    st.metric("Previous yield", f"{farmer['previous_yield']:.2f} tons")
    st.metric("Dataset yield", f"{farmer['yield_tons']:.2f} tons")

st.info(
    "These are dataset records, not live farm telemetry. The dataset does not "
    "include a farmer location, growing season, crop prices, or income."
)
