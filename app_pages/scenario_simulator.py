import streamlit as st

from ui.climate_yield_assessment import render_climate_yield_assessment
from ui.farmer_profile import select_dataset_farmer
from ui.style import apply_theme

st.set_page_config(page_title="Climate Scenario Simulator", layout="wide")
apply_theme()

farmer = select_dataset_farmer("climate_scenario_profile")
st.title("Climate Scenario Simulator")
st.write(
    "Compare a farmer's recorded sample conditions with a user-entered "
    "climate scenario using the trained crop-yield model."
)
render_climate_yield_assessment(farmer, "system_climate_scenario")
