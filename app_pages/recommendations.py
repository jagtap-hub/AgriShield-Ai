import streamlit as st

st.title("Farm Advisory & Recommendations")
st.write("Practical next steps based on verified field observations.")

st.warning(
    "There is no live weather feed or verified farmer-specific field report connected. "
    "The options below are conditional guidance, not diagnoses or personalized alerts."
)

st.markdown("### If drought or water stress is confirmed")
st.write(
    "Check field soil moisture and local forecasts, then discuss feasible irrigation "
    "and water-conservation options with a local agricultural extension service."
)

st.markdown("### If excessive rainfall or waterlogging is confirmed")
st.write(
    "Inspect drainage and crop condition, and follow local crop-protection guidance "
    "for the crop and growth stage."
)

st.markdown("### If crop stress is observed")
st.write(
    "Inspect affected plants and seek local agronomic advice before applying treatments. "
    "A crop-health index is a screening signal, not a diagnosis."
)

st.markdown("### If repayment difficulty is anticipated")
st.write(
    "Review upcoming obligations against documented cash flow and contact the lender "
    "early to ask about applicable support or restructuring options."
)

st.caption(
    "Availability and eligibility for agricultural support programs vary. "
    "Confirm current rules with the relevant local authority; no benefit or financial "
    "outcome is guaranteed."
)
