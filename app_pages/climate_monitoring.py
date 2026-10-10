import streamlit as st
import plotly.graph_objects as go
from ui.components import metric_card

st.title("Climate Monitoring")
st.write("Illustrative climate indicators for agricultural zones.")
st.warning(
    "The displayed conditions and alerts are demo values. No live weather provider, "
    "location-level observations, forecasts, or crop-season normals are configured."
)

col1, col2 = st.columns([1, 1])
with col1:
    location = st.selectbox("Location", ["Pune, Maharashtra", "Nashik, Maharashtra", "Nagpur, Maharashtra"])
with col2:
    crop = st.selectbox("Crop Type", ["Sugarcane", "Wheat", "Cotton"])

st.markdown("### Current Conditions (Demo)")
m1, m2, m3, m4 = st.columns(4)
with m1:
    metric_card("Rainfall (Last 7d)", "12 mm", "🌧️", "Below average", "-15%")
with m2:
    metric_card("Avg Temperature", "32 °C", "🌡️", "Above average", "+2°C")
with m3:
    metric_card("Soil Moisture", "45%", "💧", "Moderate", "-5%")
with m4:
    metric_card("Crop Condition", "Good", "🌱", "Based on NDVI")

st.markdown("### Live Warnings")
st.info("Unavailable: a verified location-specific weather feed is not configured.")
    
st.markdown("### Historical Climate Chart (Demo)")
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
historical_temp = [21, 23, 27, 31, 34, 30]
historical_rain = [2, 1, 5, 10, 15, 120]

fig = go.Figure()
fig.add_trace(go.Scatter(x=months, y=historical_temp, name="Avg Temp (°C)", line=dict(color="#F5B942", width=3)))
fig.add_trace(go.Bar(x=months, y=historical_rain, name="Rainfall (mm)", marker_color="rgba(16, 76, 58, 0.6)", yaxis="y2"))

fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(title="Temperature (°C)", gridcolor="rgba(0,0,0,0.05)"),
    yaxis2=dict(title="Rainfall (mm)", overlaying="y", side="right"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=0, r=0, t=30, b=0),
    height=400
)
st.plotly_chart(fig, use_container_width=True)

st.caption("Data source: fixed synthetic demo values. No observation or forecast timestamp is available.")
