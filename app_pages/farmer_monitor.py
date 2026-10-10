import streamlit as st

from ui.farmer_profile import select_dataset_farmer
from ui.style import apply_theme

st.set_page_config(page_title="Farm & Climate Monitor", layout="wide")
apply_theme()

farmer = select_dataset_farmer("farmer_monitor_profile")
st.title("My Farm & Climate Monitor")
st.write(
    f"Farm and environmental indicators recorded for {farmer['farmer_name']}."
)

st.subheader("Farm profile")
profile_columns = st.columns(4)
profile_columns[0].metric("Crop", farmer["crop_type"])
profile_columns[1].metric("Farm size", f"{farmer['farm_size_acres']:.2f} acres")
profile_columns[2].metric("Irrigation", farmer["irrigation_type"])
profile_columns[3].metric("Soil type", farmer["soil_type"])

st.subheader("Recorded sample indicators")
indicator_columns = st.columns(4)
indicator_columns[0].metric("Rainfall", f"{farmer['rainfall_mm']:.1f} mm")
indicator_columns[1].metric("Temperature", f"{farmer['temperature_c']:.1f} °C")
indicator_columns[2].metric("Soil moisture", f"{farmer['soil_moisture']:.2f}")
indicator_columns[3].metric(
    "Crop health index (0-1)", f"{farmer['crop_health_index']:.2f}"
)

st.info(
    "These are single-row synthetic dataset values, not live measurements. "
    "The dataset has no dates, location, growing season, or weather baseline, "
    "so it cannot support a trend chart or location-specific warning."
)
