import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
from datetime import datetime
from services.ml_service import (
    assess_farmer_risk,
    calculate_yield_per_acre,
    get_model_and_data,
    predict_total_yield,
)

st.title("Provisional Farmer Risk Indicator")
st.write(
    "Review available financial indicators and a separate crop-yield estimate. "
    "The financial score is not a trained default probability."
)

model, df, feature_cols = get_model_and_data()

# Create tabs for multi-step guided assessment
tabs = st.tabs(["1. Select Farmer", "2. Farm & Crop", "3. Climate", "4. Financials", "5. Review & Assess"])

with tabs[0]:
    st.markdown("### 1. Select Farmer")
    farmer_id = st.text_input("Farmer Reference ID", "FARM-1001")
    st.info("Manual demo assessment; this page does not load a verified farmer profile.")

with tabs[1]:
    st.markdown("### 2. Farm and Crop Information")
    farm_size = st.slider("Farm Size (acres)", 1.0, 50.0, 5.0)
    health_index = st.slider("Crop Health Index (NDVI Proxy)", 0.0, 1.0, 0.7)

with tabs[2]:
    st.markdown("### 3. Climate Conditions (Auto-filled)")
    st.write("These indicators are fetched from the Climate Intelligence module.")
    rain = st.slider("Rainfall (mm)", 100.0, 1500.0, 800.0)
    temp = st.slider("Temperature (°C)", 10.0, 45.0, 25.0)
    soil_moisture = st.slider("Soil Moisture (%)", 10.0, 100.0, 60.0)
    
with tabs[3]:
    st.markdown("### 4. Financial Information")
    loan_amount = st.number_input("Original Loan Amount (₹)", min_value=1.0, value=200000.0, step=10000.0)
    outstanding_loan = st.number_input("Outstanding Loan Balance (₹)", min_value=0.0, value=100000.0, step=5000.0)
    repayment_history = st.selectbox(
        "Recorded Repayment History",
        ["Always on time", "Mostly on time", "1 delayed payment", "Frequently delayed"],
    )

with tabs[4]:
    st.markdown("### 5. Review & Assess")
    st.write("Review the inputs from previous steps and generate the risk assessment.")
    st.warning(
        "Provisional financial indicator only—not a trained default probability. "
        "Weather sliders and yield estimates are not validated credit-risk signals."
    )
    
    col_a, col_b = st.columns([1, 2])
    with col_a:
        assess_btn = st.button("Run Risk Assessment", type="primary", use_container_width=True)
        st.caption("⚠️ Decision-support tool. Final lending decisions require human review.")
        
    if assess_btn:
        with st.spinner("Analyzing risk factors and running ML inference..."):
            time.sleep(1) # smooth UI
            user_data = pd.DataFrame({
                'Rainfall_mm': [rain],
                'Temperature_C': [temp],
                'Soil_Moisture': [soil_moisture],
                'Farm_Size_acres': [farm_size],
                'Crop_Health_Index': [health_index]
            })
            
            predicted_yield = predict_total_yield(model, user_data)
            yield_per_acre = calculate_yield_per_acre(predicted_yield, farm_size)
            assessment = assess_farmer_risk({
                "loan_amount": loan_amount,
                "outstanding_loan": outstanding_loan,
                "loan_repayment_history": repayment_history,
                "crop_health_index": health_index,
            })
            score = assessment["score"]
            category = assessment["category"]
            color = "#36D477" if category == "Low" else "#F5B942" if category == "Medium" else "#E45D5D"
            
            st.success("Assessment Complete!")
            
            c1, c2 = st.columns([1, 1.5])
            with c1:
                st.markdown(f"#### Risk Score")
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = score,
                    number = {'font': {'color': '#092B20', 'size': 36}},
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': category, 'font': {'size': 24, 'color': color}},
                    gauge = {
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                        'bar': {'color': color},
                        'steps': [
                            {'range': [0, 34], 'color': "rgba(54, 212, 119, 0.2)"},
                            {'range': [34, 67], 'color': "rgba(245, 185, 66, 0.2)"},
                            {'range': [67, 100], 'color': "rgba(228, 93, 93, 0.2)"}],
                    }
                ))
                fig.update_layout(height=280, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#15251C"))
                st.plotly_chart(fig, use_container_width=True)
                
            with c2:
                st.markdown("#### Assessment Details")
                st.write(f"**Reference ID:** `RES-{int(time.time())}`")
                st.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"**Predicted total production (sample-trained model):** {predicted_yield:.2f} tons")
                st.write(f"**Predicted production per acre:** {yield_per_acre:.2f} tons/acre")

                st.markdown("**Available score contributors**")
                for factor in assessment["factors"]:
                    st.markdown(
                        f"- **{factor['name']}** — {factor['observed_value']}. "
                        f"{factor['explanation']}"
                    )
                st.caption(assessment["additional_factor_status"])
                st.caption(assessment["method"])
                st.caption(
                    "Financial History Score is excluded because its meaning and scale are undocumented."
                )
                st.warning(assessment["weather_warning"])
                st.markdown("**Recommendations**")
                for recommendation in assessment["recommendations"]:
                    st.markdown(f"- {recommendation}")
                
                if category == "High":
                    st.error("High provisional indicator. Human review is required.")
                elif category == "Medium":
                    st.warning("Medium provisional indicator. Review the contributing factors.")
                else:
                    st.success("Low provisional indicator. This is not a lending recommendation.")
