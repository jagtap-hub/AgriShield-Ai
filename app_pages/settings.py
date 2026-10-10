import streamlit as st

st.title("System Settings")
st.write("Configure application preferences and data connections.")

tabs = st.tabs(["Profile", "Data Sources", "Model Information", "Data Import", "Privacy & Security", "Application Preferences"])

with tabs[0]:
    st.markdown("### User Profile")
    st.text_input("Name", "Jane Doe")
    st.text_input("Email", "jane.doe@agrishield.ai")
    st.text_input("Role", "Credit Risk Manager", disabled=True)
    st.button("Update Profile", type="primary")

with tabs[1]:
    st.markdown("### Data Sources & APIs")
    st.write("Configure external integrations for climate and market data.")
    
    st.markdown("#### Weather API")
    c1, c2 = st.columns([3, 1])
    with c1:
        st.text_input("API Endpoint", "https://api.weather.com/v3/...", disabled=True)
    with c2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.write("🟢 Connected")
        
    st.markdown("#### Market Prices API")
    c3, c4 = st.columns([3, 1])
    with c3:
        st.text_input("API Key", "************************")
    with c4:
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("Test Connection", type="secondary")

with tabs[2]:
    st.markdown("### Model Information")
    st.write("**Credit Risk Model Version:** v2.4 (Production)")
    st.write("**Model Type:** Random Forest Classifier (Scikit-learn)")
    st.write("**Dataset:** Synthetic Farm Financial & Climate Data (due to lack of public repayment labels)")
    st.write("**Features Used:** Rainfall Deviation, Temperature Anomaly, Soil Moisture, Expected Yield Change, Market Price Change, Farmer Income, Existing Loan, Repayment History Score, Location, Crop Type, Irrigation Availability.")
    
    st.info("**Disclaimer:** The predictions are illustrative and based on a synthetic dataset designed for demonstration. Real-world deployment requires a model trained on actual historical bank repayment labels.")
    
    st.button("Request Model Retraining", type="secondary")

with tabs[3]:
    st.markdown("### Data Import")
    st.write("Upload offline farmer records or historical portfolio data.")
    st.file_uploader("Upload CSV or Excel File", type=["csv", "xlsx"])
    st.button("Start Import", type="primary")

with tabs[4]:
    st.markdown("### Privacy & Security")
    st.write("Manage data retention and access controls.")
    st.checkbox("Anonymize PII in exports", value=True)
    st.checkbox("Require 2FA for high-risk assessments", value=False)
    st.button("Save Security Settings", type="primary")

with tabs[5]:
    st.markdown("### Application Preferences")
    st.selectbox("Default Region", ["Pune", "Nashik", "Nagpur"])
    st.selectbox("Theme", ["System Default", "Light", "Dark"])
    st.selectbox("Language", ["English", "Hindi", "Marathi"])
    st.button("Save Preferences", type="primary")
