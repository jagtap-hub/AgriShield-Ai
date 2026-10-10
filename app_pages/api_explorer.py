import streamlit as st
import requests
import pandas as pd
from ui.components import metric_card, alert_card
from services.db_service import fetch_all_farmers

st.title("⚡ FastAPI Backend & Database Inspector")
st.write("Live API metrics, Swagger interactive documentation, and database record inspector for judge presentations.")

API_URL = "http://127.0.0.1:8000"

# Check API health
try:
    res = requests.get(f"{API_URL}/", timeout=2)
    if res.status_code == 200:
        api_online = True
        status_msg = "🟢 FastAPI Server Online & Listening at http://127.0.0.1:8000"
    else:
        api_online = False
        status_msg = "🔴 API responding with error"
except Exception:
    api_online = False
    status_msg = "🟡 API running in Direct DB Fallback Mode"

st.info(status_msg)

m1, m2, m3 = st.columns(3)
with m1:
    metric_card("Backend Framework", "FastAPI v0.143", "⚡", "Uvicorn ASGI Server")
with m2:
    metric_card("Database Engine", "SQLite / MySQL", "🗄️", "SQLAlchemy ORM")
with m3:
    farmers_all = fetch_all_farmers()
    metric_card("Database Records", f"{len(farmers_all)} Farmers", "📊", "Seeded from CSV")

st.markdown("---")

st.markdown("### 🌐 Live Swagger & REST Endpoints")
st.markdown("""
<div class="premium-card" style="background-color: #FFFFFF; padding: 20px; border-radius: 12px; border: 1px solid rgba(16, 76, 58, 0.1);">
    <h4 style="margin-top:0;">📖 Interactive API Documentation (For Judges)</h4>
    <p>You can view and test the live FastAPI REST endpoints directly in your browser:</p>
    <ul>
        <li><strong>Swagger UI (Interactive Docs):</strong> <a href="http://127.0.0.1:8000/docs" target="_blank">http://127.0.0.1:8000/docs</a></li>
        <li><strong>ReDoc UI:</strong> <a href="http://127.0.0.1:8000/redoc" target="_blank">http://127.0.0.1:8000/redoc</a></li>
        <li><strong>OpenAPI JSON Schema:</strong> <a href="http://127.0.0.1:8000/openapi.json" target="_blank">http://127.0.0.1:8000/openapi.json</a></li>
        <li><strong>Farmers Endpoint:</strong> <a href="http://127.0.0.1:8000/api/farmers" target="_blank">http://127.0.0.1:8000/api/farmers</a></li>
        <li><strong>Single Farmer Endpoint:</strong> <a href="http://127.0.0.1:8000/api/farmers/FARM-1001" target="_blank">http://127.0.0.1:8000/api/farmers/FARM-1001</a></li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("### 🔍 Live API JSON Response Inspector")

c1, c2 = st.columns(2)
with c1:
    selected_fid = st.selectbox("Select Farmer ID to fetch from FastAPI", [f"FARM-{1001 + i}" for i in range(10)])
    if st.button("GET /api/farmers/{id}", type="primary"):
        try:
            r = requests.get(f"{API_URL}/api/farmers/{selected_fid}", timeout=2)
            if r.status_code == 200:
                st.json(r.json())
            else:
                st.error(f"Error {r.status_code}: {r.text}")
        except Exception as e:
            st.error(f"Could not connect to FastAPI server: {str(e)}")

with c2:
    st.markdown("#### 🗄️ Database Record Preview (First 5 Rows)")
    df = pd.DataFrame(farmers_all[:5])
    st.dataframe(df[['farmer_id', 'farmer_name', 'loan_amount', 'crop_type', 'financial_history_score']], use_container_width=True, hide_index=True)
