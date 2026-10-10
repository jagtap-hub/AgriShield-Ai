import streamlit as st

def apply_theme():
    st.markdown("""
    <style>
        /* Main background */
        .stApp {
            background-color: #F7F8F2;
            color: #15251C;
        }
        
        /* Sidebar customization — sidebar scrolls naturally; NO fixed elements
           (a fixed-positioned footer used to overlay and hide the last fields) */
        [data-testid="stSidebar"] {
            background-color: #092B20 !important;
            padding-bottom: 16px !important;
        }
        [data-testid="stSidebar"] * {
            color: #E8F7EE !important;
        }
        [data-testid="stSidebar"] [data-testid="stSidebarNav"] {
            background-color: #092B20 !important;
        }
        [data-testid="stSidebar"] svg {
            fill: #E8F7EE !important;
        }
        
        /* Hide default sidebar header if possible or recolor it */
        [data-testid="stSidebarNav"] {
            background-color: #092B20 !important;
        }

        /* Active Sidebar Item */
        [data-testid="stSidebarNavLink"] {
            display: flex !important;
            align-items: center !important;
            min-height: 34px;
            padding: 4px 10px !important;
            color: #E8F7EE !important;
            background-color: transparent !important;
            border-radius: 8px;
            margin: 2px 10px !important;
            transition: all 0.2s ease;
        }
        [data-testid="stSidebarNavLink"] *,
        [data-testid="stSidebarNavLink"] span,
        [data-testid="stSidebarNavLink"] p {
            color: #E8F7EE !important;
            -webkit-text-fill-color: #E8F7EE !important;
        }
        [data-testid="stSidebarNavLink"]:hover {
            background-color: rgba(54, 212, 119, 0.1) !important;
        }
        [data-testid="stSidebarNavLink"][aria-current="page"],
        [data-testid="stSidebarNavLink"] [aria-current="page"] {
            background-color: #B8F36B !important;
        }
        [data-testid="stSidebarNavLink"][aria-current="page"] *,
        [data-testid="stSidebarNavLink"][aria-current="page"] span,
        [data-testid="stSidebarNavLink"][aria-current="page"] p,
        [data-testid="stSidebarNavLink"] [aria-current="page"],
        [data-testid="stSidebarNavLink"] [aria-current="page"] * {
            color: #092B20 !important;
            -webkit-text-fill-color: #092B20 !important;
            font-weight: 600 !important;
        }
        [data-testid="stSidebarNavLink"][aria-current="page"] svg,
        [data-testid="stSidebarNavLink"] [aria-current="page"] svg {
            fill: #092B20 !important;
        }
        
        /* Fix Form Input & Slider Labels Contrast */
        .stApp label, 
        .stApp [data-testid="stWidgetLabel"], 
        .stApp [data-testid="stWidgetLabel"] *, 
        .stApp [data-testid="stMarkdownContainer"] p,
        .stSlider label, 
        .stTextInput label, 
        .stSelectbox label, 
        .stNumberInput label, 
        .stRadio label {
            color: #092B20 !important;
            font-weight: 600 !important;
        }
        
        /* Slider thumb & value text */
        [data-testid="stThumbValue"], [data-testid="stSliderTickBar"] {
            color: #092B20 !important;
        }
        
        /* Buttons */
        .stButton>button {
            background-color: #36D477;
            color: #092B20 !important;
            font-weight: 600;
            border-radius: 12px;
            border: none;
            padding: 10px 24px;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #B8F36B;
            color: #092B20 !important;
            box-shadow: 0 4px 12px rgba(184, 243, 107, 0.4);
            border-color: #B8F36B;
        }
        
        /* Secondary Buttons */
        button[kind="secondary"] {
            background-color: #FFFFFF !important;
            color: #104C3A !important;
            border: 1px solid #104C3A !important;
        }
        button[kind="secondary"]:hover {
            background-color: #E8F7EE !important;
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: #092B20 !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        /* Cards */
        .premium-card {
            background-color: #FFFFFF;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.04);
            border: 1px solid rgba(16, 76, 58, 0.08);
            margin-bottom: 20px;
            height: 100%;
        }
        
        .metric-value {
            font-size: 2.2rem;
            font-weight: 700;
            color: #092B20;
            margin: 5px 0;
        }
        
        .metric-label {
            color: #728076;
            font-size: 0.9rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Alerts */
        .alert-card {
            padding: 16px;
            border-radius: 12px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        .alert-red { border-left: 6px solid #E45D5D; background-color: #FEF2F2; }
        .alert-amber { border-left: 6px solid #F5B942; background-color: #FFFBEB; }
        .alert-green { border-left: 6px solid #36D477; background-color: #F0FDF4; }
        
        /* Form inputs */
        .stTextInput>div>div>input,
        .stNumberInput>div>div>input,
        .stTextArea textarea,
        [data-testid="stTextInputRootElement"],
        [data-testid="stNumberInputRootElement"],
        [data-testid="stSelectbox"] [role="group"],
        .stSelectbox [data-baseweb="select"] > div {
            background-color: #FFFFFF !important;
            border-radius: 8px;
            border: 1px solid #A8B7AE !important;
            color: #092B20 !important;
            -webkit-text-fill-color: #092B20 !important;
        }
        [data-testid="stTextInputField"],
        [data-testid="stNumberInputField"],
        [data-testid="stSelectbox"] input[role="combobox"],
        [data-testid="stTextArea"] textarea {
            background-color: transparent !important;
            color: #092B20 !important;
            -webkit-text-fill-color: #092B20 !important;
        }
        .stTextInput>div>div>input::placeholder,
        .stNumberInput>div>div>input::placeholder,
        .stTextArea textarea::placeholder {
            color: #52645A !important;
            -webkit-text-fill-color: #52645A !important;
            opacity: 1 !important;
        }
        .stTextInput input:focus,
        .stNumberInput input:focus,
        .stTextArea textarea:focus,
        .stSelectbox [data-baseweb="select"] > div:focus-within {
            border-color: #104C3A !important;
            box-shadow: 0 0 0 2px rgba(54, 212, 119, 0.25) !important;
        }
        [data-testid="stTextInputRootElement"]:focus-within,
        [data-testid="stNumberInputRootElement"]:focus-within,
        [data-testid="stSelectbox"] [role="group"]:focus-within {
            border-color: #104C3A !important;
            box-shadow: 0 0 0 2px rgba(54, 212, 119, 0.25) !important;
        }
        [role="listbox"] {
            background-color: #FFFFFF !important;
            color: #092B20 !important;
        }
        [role="option"] {
            color: #092B20 !important;
        }
        [role="option"]:hover,
        [role="option"][aria-selected="true"] {
            background-color: #E8F7EE !important;
            color: #092B20 !important;
        }
        
        /* Buttons INSIDE the dark sidebar: light theme button is invisible on
           dark green, so give them their own dark-portal styling */
        [data-testid="stSidebar"] [data-testid="stButton"] button {
            background-color: #B8F36B !important;
            color: #092B20 !important;
            -webkit-text-fill-color: #092B20 !important;
            border: 1px solid #B8F36B !important;
            font-weight: 600;
            border-radius: 12px;
            padding: 10px 24px;
        }
        [data-testid="stSidebar"] [data-testid="stButton"] button *,
        [data-testid="stSidebar"] [data-testid="stButton"] button p,
        [data-testid="stSidebar"] [data-testid="stButton"] button span {
            color: #092B20 !important;
            -webkit-text-fill-color: #092B20 !important;
        }
        [data-testid="stSidebar"] [data-testid="stButton"] button:hover {
            background-color: #D8F7A7 !important;
            border-color: #D8F7A7 !important;
        }
        [data-testid="stSidebar"] [data-testid="stButton"] button:focus-visible {
            outline: 3px solid #FFFFFF !important;
            outline-offset: 2px !important;
        }

        /* Text fields / selects inside the sidebar: white bg + dark text so
           they are always readable */
        [data-testid="stSidebar"] .stTextInput>div>div>input,
        [data-testid="stSidebar"] .stSelectbox>div>div>div,
        [data-testid="stSidebar"] .stNumberInput>div>div>input {
            background-color: #FFFFFF !important;
            color: #092B20 !important;
            -webkit-text-fill-color: #092B20 !important;
            border: 1px solid #36D477 !important;
            border-radius: 8px;
        }
        [data-testid="stSidebar"] .stTextInput>div>div>input::placeholder,
        [data-testid="stSidebar"] .stSelectbox [data-testid="stSelectboxValue"] {
            color: #092B20 !important;
            opacity: 0.85 !important;
        }

        /* Dataframes */
        [data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("""
    <div style="text-align: center; margin-bottom: 6px; padding: 8px 0 4px 0;">
        <h2 style="color: #B8F36B !important; margin: 0 0 3px 0; font-weight: 800;">🛡️ AgriShield AI</h2>
        <p style="color: #E8F7EE; font-size: 0.85em; opacity: 0.8; margin: 0; font-weight: 500; letter-spacing: 1px;">CLIMATE INTELLIGENCE</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar footer (in-flow, never fixed — a fixed footer covers sidebar fields)
    st.sidebar.markdown("""
    <div style="margin-top: 8px; margin-bottom: 4px; padding: 12px; background-color: rgba(54,212,119,0.06); border: 1px solid rgba(54,212,119,0.15); border-radius: 12px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="width: 32px; height: 32px; border-radius: 50%; background-color: #36D477; display: flex; align-items: center; justify-content: center; color: #092B20; font-weight: bold; flex-shrink: 0;">JD</div>
            <div style="line-height: 1.2; min-width: 0;">
                <div style="font-size: 14px; font-weight: 600; color: #fff; white-space: nowrap; overflow: visible;">Demo Profile</div>
                <div style="font-size: 11px; color: rgba(255,255,255,0.7); display: flex; align-items: center; gap: 4px; white-space: nowrap;">
                    <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background-color: #36D477;"></span> Systems Online
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
