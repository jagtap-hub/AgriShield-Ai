import streamlit as st

from ui.climate_yield_assessment import render_climate_yield_assessment
from ui.farmer_profile import select_dataset_farmer
from ui.style import apply_theme

st.set_page_config(page_title="Crop Yield Outlook", layout="wide")
apply_theme()

farmer = select_dataset_farmer("farmer_outlook_profile")
st.title("Crop Yield & Climate Outlook")
st.write(
    f"Explore crop production for {farmer['farmer_name']}'s "
    f"{farmer['crop_type']} farm."
)

farm_columns = st.columns(4)
farm_columns[0].metric("Crop", farmer["crop_type"])
farm_columns[1].metric("Farm size", f"{farmer['farm_size_acres']:.2f} acres")
farm_columns[2].metric("Irrigation", farmer["irrigation_type"])
farm_columns[3].metric(
    "Recorded crop-health proxy",
    f"{farmer['crop_health_index']:.2f} / 1",
)

render_climate_yield_assessment(farmer, "farmer_yield_outlook")
