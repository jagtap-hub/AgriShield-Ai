import streamlit as st

from ui.farmer_profile import select_dataset_farmer
from ui.farmer_notifications import render_farmer_loan_notifications
from ui.style import apply_theme

st.set_page_config(page_title="Recommendations & Support", layout="wide")
apply_theme()

farmer = select_dataset_farmer("farmer_support_profile")
st.title("Recommendations & Support")
st.write(f"Field guidance for {farmer['farmer_name']}'s {farmer['crop_type']} profile.")
render_farmer_loan_notifications(str(farmer["farmer_id"]))

st.subheader("Farm conditions in the selected record")
columns = st.columns(4)
columns[0].metric("Crop", farmer["crop_type"])
columns[1].metric("Irrigation", farmer["irrigation_type"])
columns[2].metric("Soil moisture", f"{farmer['soil_moisture']:.2f}")
columns[3].metric(
    "Crop health index (0-1)", f"{farmer['crop_health_index']:.2f}"
)

st.markdown("### Practical next steps")
st.write(
    f"Use the recorded irrigation type ({farmer['irrigation_type']}) as a starting "
    "point for a field-level discussion. Ask a local agricultural extension service "
    "whether water-efficiency or drainage measures fit your crop and site."
)
st.write(
    f"The dataset records a crop-health index of {farmer['crop_health_index']:.2f}. "
    "This is not a diagnosis or a live measurement. Inspect current plants and ask "
    "a qualified local advisor to assess any visible stress before applying treatment."
)
st.write(
    "Check current local rules directly with the relevant authorities before relying "
    "on an insurance, subsidy, or relief program. Eligibility, coverage, and deadlines "
    "are not included in this dataset and are not guaranteed here."
)

st.info(
    "This profile comes from generated sample data. No live field report, weather "
    "feed, crop stage, program eligibility, or locally verified recommendation is connected."
)
