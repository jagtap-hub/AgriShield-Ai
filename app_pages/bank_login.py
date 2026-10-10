import streamlit as st
from ui.components import hero_section, alert_card

st.title("Banker Portal Authentication")

hero_section(
    "AgriShield AI — Commercial Bank Portal", 
    "Secure role-based access for credit officers, risk analysts, and hackathon judges."
)

if "bank_user" not in st.session_state:
    st.session_state.bank_user = None

if st.session_state.bank_user:
    st.success(f"Logged in as **{st.session_state.bank_user['name']}** ({st.session_state.bank_user['role']})")
    st.info(f"**Branch:** {st.session_state.bank_user['branch']} | **Employee ID:** {st.session_state.bank_user['emp_id']}")
    if st.button("Logout / Change User", type="secondary"):
        st.session_state.bank_user = None
        st.rerun()
else:
    # Judge Quick Login Banner
    st.markdown("""
    <div class="premium-card" style="background-color: #E8F7EE; border-left: 6px solid #36D477; padding: 18px; border-radius: 12px; margin-bottom: 25px;">
        <h4 style="margin: 0; color: #092B20;">⚖️ Hackathon Judge Quick Demo Mode</h4>
        <p style="margin: 5px 0 10px 0; color: #15251C; font-size: 0.95rem;">
            Presenting to judges? Click below for instant one-click login with full Senior Credit Officer & Judge permissions.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_j1, col_j2 = st.columns([1, 2])
    with col_j1:
        if st.button("🏆 One-Click Login as Judge / Examiner", type="primary", use_container_width=True):
            st.session_state.bank_user = {
                "emp_id": "JUDGE-2026",
                "name": "Lead Credit Judge",
                "email": "judge@agrishield.ai",
                "branch": "Pune Central Branch",
                "role": "Chief Risk Examiner"
            }
            st.success("Authenticated as Judge!")
            st.rerun()

    st.markdown("---")

    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.markdown("### 🔒 Employee Login")
        emp_id = st.text_input("Bank Employee ID", "EMP-80429")
        email = st.text_input("Work Email", "j.doe@agribank.com")
        password = st.text_input("Password", "••••••••", type="password")
        
        branch = st.selectbox("Assigned Branch", ["Pune Central Branch", "Nashik Main Branch", "Nagpur East Branch", "Satara Rural Branch"])
        role = st.selectbox("Role Permission", ["Senior Credit Officer", "Branch Manager", "Agri-Risk Analyst"])
        
        if st.button("Authenticate & Access Dashboard", type="secondary", use_container_width=True):
            st.session_state.bank_user = {
                "emp_id": emp_id,
                "name": "Jane Doe",
                "email": email,
                "branch": branch,
                "role": role
            }
            st.success("Authentication successful!")
            st.rerun()
            
    with c2:
        st.markdown("### 🛡️ Judge Demo Credentials")
        st.write("**Employee ID:** `JUDGE-2026`")
        st.write("**Email:** `judge@agrishield.ai`")
        st.write("**Password:** `judge123`")
        st.write("**Role:** `Chief Risk Examiner`")
        st.write("**FastAPI Server:** `http://127.0.0.1:8000`")
        st.write("**Swagger Docs:** `http://127.0.0.1:8000/docs`")
        
        alert_card("Role Scoped Data", "You will view loan data and farmer profiles registered under your assigned branch.", "info", "🔒")
        alert_card("Audit Logging", "Audit logging is not configured; demo decisions and score overrides are not recorded.", "amber", "📜")
