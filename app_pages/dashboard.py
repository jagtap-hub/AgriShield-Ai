import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
from ui.components import metric_card, hero_section
from services.ml_service import get_model_and_data, get_yield_feature_importances

st.title("Overview")

hero_section(
    "Good morning, welcome to AgriShield", 
    "Climate intelligence for stronger farms and smarter lending."
)

col1, col2 = st.columns([1, 1])
with col1:
    st.markdown(f"**Date:** {datetime.now().strftime('%B %d, %Y')}")
with col2:
    st.selectbox("Select Location Context", ["All Regions", "Pune District", "Nashik District", "Nagpur District"])

st.markdown("<br>", unsafe_allow_html=True)
col_a, col_b = st.columns(2)
with col_a:
    st.button("Assess Farmer Risk", type="primary", use_container_width=True)
with col_b:
    st.button("Explore Climate", type="secondary", use_container_width=True)

st.markdown("### Key Metrics")
m1, m2, m3, m4 = st.columns(4)

with m1:
    metric_card("Farmers Monitored", "Unavailable", "👨‍🌾", "No monitoring feed is connected")
with m2:
    metric_card("Farms Assessed", "Unavailable", "🛡️", "Assessment history is not stored")
with m3:
    metric_card("Needs Review", "Unavailable", "⚠️", "No portfolio review queue is connected")
with m4:
    metric_card("Live Weather Alerts", "Unavailable", "🔔", "No weather provider configured")

st.markdown("---")

c1, c2 = st.columns([2, 1])

with c1:
    st.markdown("### Climate Trends (Demo Data)")
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    temp = [22, 24, 28, 32, 35, 30]
    rain = [5, 2, 10, 5, 20, 150]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=temp, name="Avg Temp (°C)", line=dict(color="#E45D5D", width=3)))
    fig.add_trace(go.Bar(x=months, y=rain, name="Rainfall (mm)", marker_color="rgba(54, 212, 119, 0.5)", yaxis="y2"))
    
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(title="Temperature (°C)", gridcolor="rgba(0,0,0,0.05)"),
        yaxis2=dict(title="Rainfall (mm)", overlaying="y", side="right"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.markdown("### Risk Distribution")
    st.info(
        "Unavailable: assessments are not persisted, so no portfolio distribution "
        "can be calculated from current records."
    )

st.markdown("### Global Yield-Model Feature Importance")
model, df, feature_cols = get_model_and_data()
importance = get_yield_feature_importances(model)
feat_imp_df = pd.DataFrame({'Feature': feature_cols, 'Importance': importance}).sort_values('Importance', ascending=True)

fig_bar = px.bar(feat_imp_df, x='Importance', y='Feature', orientation='h', 
             color_discrete_sequence=['#104C3A'])
fig_bar.update_layout(
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(gridcolor="rgba(0,0,0,0.05)"),
    margin=dict(l=0, r=0, t=10, b=0),
    height=300
)
st.plotly_chart(fig_bar, use_container_width=True)
st.caption(
    "These aggregate importances describe yield prediction only. They are not "
    "farmer-specific risk explanations or causal effects."
)

st.markdown("### Latest Intelligence")
st.info(
    "Live, location-specific weather and market feeds are not configured. "
    "No current forecast or early warning is available."
)
