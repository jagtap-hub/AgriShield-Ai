import streamlit as st

# ---------------------------------------------------------------------------
# GUIDED WORKFLOW COMPONENTS — make the app flow easy to follow for any user
# ---------------------------------------------------------------------------

ROLE_META = {
    "farmer": {"icon": "👨‍🌾", "label": "Farmer Portal", "tagline": "Farm → Climate scenario → Yield estimate → Support"},
    "officer": {"icon": "🚜", "label": "Field Officer Portal", "tagline": "Task → Inspect → Report → Done"},
    "bank": {"icon": "🏦", "label": "Banker Portal", "tagline": "Login → Portfolio → ML yield scenario → Field check → Human review"},
}


def role_selector():
    """Landing-page role chooser: pick a portal, the sidebar nav updates instantly."""
    if "user_role" not in st.session_state:
        st.session_state.user_role = None
    st.markdown("### 👋 Welcome! Who are you using this app as?")
    st.caption("Pick one below — the sidebar menu will change to show only your tools.")
    c1, c2, c3 = st.columns(3)
    roles = [
        ("farmer", "👨‍🌾 I am a Farmer", "View my farm profile, explore a crop-yield scenario and find support."),
        ("officer", "🚜 I am a Field Officer", "Inspect farmer plots on the ground and submit verification reports."),
        ("bank", "🏦 I am a Banker", "Review ML crop-yield scenarios, request field checks and assess repayment evidence."),
    ]
    clicked = None
    for (role, label, desc), col in zip(roles, [c1, c2, c3]):
        with col:
            selected = st.session_state.user_role == role
            border = "6px solid #B8F36B" if selected else "1px solid rgba(16,76,58,0.15)"
            st.markdown(f"""
            <div class="premium-card" style="border: {border}; min-height: 200px;">
                <h4 style="margin: 0 0 8px 0;">{label}</h4>
                <p style="font-size: 0.9rem; color: #728076;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open this portal" if not selected else "✓ Current portal",
                         key=f"role_{role}", use_container_width=True,
                         type="primary" if selected else "secondary"):
                clicked = role
    if clicked:
        st.session_state.user_role = clicked
        st.rerun()
    return st.session_state.user_role


def workflow_tracker(steps, current_step=0):
    """Horizontal step tracker: shows where the user is in the overall workflow."""
    cols = st.columns(len(steps))
    for i, col in enumerate(cols):
        with col:
            done = i < current_step
            active = i == current_step
            color = "#36D477" if done else ("#092B20" if active else "#728076")
            bg = "#B8F36B" if done else ("#E8F7EE" if active else "#FFFFFF")
            ring = f"3px solid {color}" if active else "1px solid rgba(16,76,58,0.12)"
            st.markdown(f"""
            <div style="text-align:center; padding: 10px 6px; border-radius: 12px; background:{bg};">
                <div style="width:34px; height:34px; margin: 0 auto 6px auto; border-radius:50%;
                     border:{ring}; background:{bg}; display:flex; align-items:center; justify-content:center;
                     font-weight:700; color:{color};">{'✓' if done else i+1}</div>
                <div style="font-size:0.8rem; font-weight:600; color:{color};">{steps[i]}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


def next_step_banner(text, button_label, page_path):
    """'What happens next?' card with a one-click jump to the next workflow page."""
    st.markdown(f"""
    <div class="premium-card" style="background:#E8F7EE; border-left:6px solid #36D477;">
        <h4 style="margin:0;">➡️ What happens next?</h4>
        <p style="margin:4px 0 0 0;">{text}</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button(button_label, key=f"next_{page_path}", type="primary", use_container_width=True):
        st.switch_page(page_path)


def portal_header(role, steps, current_step):
    """Consistent workflow header for every portal page."""
    meta = ROLE_META[role]
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom: 10px;">
        <div style="font-size:2rem;">{meta['icon']}</div>
        <div>
            <div style="font-weight:700; font-size:1.1rem;">{meta['label']} · Step {current_step + 1} of {len(steps)}</div>
            <div style="color:#728076; font-size:0.85rem;">{meta['tagline']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    workflow_tracker(steps, current_step)


def metric_card(title, value, icon, description="", trend=None):
    trend_html = ""
    if trend:
        color = "#36D477" if trend.startswith("+") else "#E45D5D"
        trend_html = f"<div style='color: {color}; font-size: 0.85rem; font-weight: 600; margin-top: 5px;'>{trend} vs last month</div>"
        
    st.markdown(f"""
    <div class="premium-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div class="metric-label">{title}</div>
            <div style="background-color: #E8F7EE; padding: 8px; border-radius: 8px; font-size: 1.2rem;">{icon}</div>
        </div>
        <div class="metric-value">{value}</div>
        <div style="color: #728076; font-size: 0.85rem;">{description}</div>
        {trend_html}
    </div>
    """, unsafe_allow_html=True)

def hero_section(title, subtitle):
    st.markdown(f"""
    <div class="hero-section">
        <div style="position: absolute; right: -20px; top: -50px; opacity: 0.1; font-size: 200px;">🌿</div>
        <div style="position: absolute; right: 150px; bottom: -40px; opacity: 0.05; font-size: 150px;">🛡️</div>
        <h1 class="hero-title">{title}</h1>
        <p class="hero-subtitle">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def alert_card(title, message, severity="info", icon="ℹ️"):
    color_class = "alert-amber"
    if severity == "high" or severity == "error":
        color_class = "alert-red"
    elif severity == "success":
        color_class = "alert-green"
        
    st.markdown(f"""
    <div class="alert-card {color_class}">
        <div style="font-size: 1.5rem;">{icon}</div>
        <div>
            <div style="font-weight: 700; color: #15251C; margin-bottom: 2px;">{title}</div>
            <div style="font-size: 0.9rem; color: #404040;">{message}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
