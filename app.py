import streamlit as st
from ui.style import apply_theme
from ui.components import role_selector

# --- UI Configuration (Must be first) ---
st.set_page_config(page_title="AgriShield AI", page_icon="🛡️", layout="wide")

apply_theme()

# ---------------------------------------------------------------------------
# GUIDED WORKFLOW: the user picks a portal once, then the sidebar only shows
# the pages that belong to that portal — no clutter, no confusion.
# ---------------------------------------------------------------------------

ALL_PAGES = {
    "farmer": {
        "👨‍🌾 FARMER PORTAL": [
            st.Page("app_pages/farmer_home.py", title="1 · Home Dashboard", icon="🏠"),
            st.Page("app_pages/farmer_monitor.py", title="2 · My Farm & Climate", icon="⛅"),
            st.Page("app_pages/farmer_outlook.py", title="3 · Crop Yield Outlook", icon="📈"),
            st.Page("app_pages/farmer_support.py", title="4 · Recommendations & Support", icon="💡"),
            st.Page("app_pages/farmer_assessments.py", title="5 · Assessments & Alerts", icon="🔔"),
            st.Page("app_pages/farmer_schemes.py", title="6 · Government Schemes", icon="🌾"),
        ]
    },
    "officer": {
        "🚜 FIELD OFFICER PORTAL": [
            st.Page("app_pages/officer_dashboard.py", title="1 · Officer Dashboard", icon="🗺️"),
            st.Page("app_pages/officer_verification.py", title="2 · Verification Tasks", icon="✅"),
        ]
    },
    "bank": {
        "🏦 BANKER PORTAL": [
            st.Page("app_pages/bank_login.py", title="1 · Banker Login & Judge Demo", icon="🔑"),
            st.Page("app_pages/bank_dashboard.py", title="2 · Banking Dashboard", icon="📊"),
            st.Page("app_pages/bank_portfolio.py", title="3 · Farmer & Loan Portfolio", icon="💼"),
            st.Page("app_pages/bank_risk_assessment.py", title="4 · Climate & Repayment Assessment", icon="🛡️"),
            st.Page("app_pages/bank_field_requests.py", title="5 · Field Verification Requests", icon="📡"),
            st.Page("app_pages/bank_decision.py", title="6 · Review & Decision Tracking", icon="📝"),
            st.Page("app_pages/bank_reports.py", title="7 · Branch Reports & Alerts", icon="📁"),
        ]
    },
    "system": {
        "⚙️ SYSTEM": [
            st.Page("app_pages/api_explorer.py", title="FastAPI & DB Explorer", icon="⚡"),
            st.Page("app_pages/settings.py", title="Settings", icon="⚙️"),
        ]
    },
}

role = st.session_state.get("user_role")

if role:
    if st.sidebar.button("🔄 Switch Portal", use_container_width=True):
        st.session_state.user_role = None
        st.rerun()
    if st.sidebar.button("⚙️ System Tools", use_container_width=True):
        st.session_state.user_role = "system"
        st.rerun()
    nav = st.navigation(ALL_PAGES[role])
    nav.run()
else:
    # Landing page — role chooser decides which portal the sidebar shows.
    st.markdown("""
    <div class="hero-section">
        <div style="position: absolute; right: -20px; top: -50px; opacity: 0.1; font-size: 200px;">🌿</div>
        <h1 class="hero-title">🛡️ AgriShield AI</h1>
        <p class="hero-subtitle">One workflow, three portals: farmers explore crop-yield scenarios, officers verify field conditions, and bankers review climate and repayment evidence.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("#### 🧭 The full workflow in one glance")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="premium-card"><h4 style="margin:0;">👨‍🌾 Farmer</h4><p style="font-size:0.9rem;">🏠 Home → ⛅ Farm & Climate → 📈 ML Crop Yield Scenarios → 💡 Support → 🔔 Assessments</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="premium-card"><h4 style="margin:0;">🚜 Field Officer</h4><p style="font-size:0.9rem;">🗺️ Dashboard → ✅ Verification Tasks<br/><b>Result:</b> ground truth report for each farmer plot.</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="premium-card"><h4 style="margin:0;">🏦 Banker</h4><p style="font-size:0.9rem;">🔑 Login → 📊 Dashboard → 💼 Portfolio → 🛡️ ML Yield & Repayment Review → 📡 Field Requests → 📝 Decision → 📁 Reports<br/><b>Result:</b> model-assisted review with field evidence and human decision-making.</p></div>', unsafe_allow_html=True)
    st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)
    role_selector()
