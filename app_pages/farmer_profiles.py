import streamlit as st
import pandas as pd
from services.db_service import fetch_all_farmers

st.title("Farmer Profiles Directory")
st.write("Manage farmer records, view profiles dynamically loaded from the database.")

farmers = fetch_all_farmers()
df = pd.DataFrame(farmers)

# Search and Filters
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    search_term = st.text_input("🔍 Search farmers by name or ID...")
with col2:
    crop_filter = st.selectbox("Crop Type", ["All"] + list(df['crop_type'].unique()) if 'crop_type' in df else ["All"])
with col3:
    irrigation_filter = st.selectbox("Irrigation Type", ["All"] + list(df['irrigation_type'].unique()) if 'irrigation_type' in df else ["All"])

# Apply filters
filtered_df = df.copy()
if search_term:
    filtered_df = filtered_df[
        filtered_df['farmer_name'].str.contains(search_term, case=False, na=False) |
        filtered_df['farmer_id'].str.contains(search_term, case=False, na=False)
    ]
if crop_filter != "All":
    filtered_df = filtered_df[filtered_df['crop_type'] == crop_filter]
if irrigation_filter != "All":
    filtered_df = filtered_df[filtered_df['irrigation_type'] == irrigation_filter]

st.markdown(f"### Database Farmer Directory ({len(filtered_df)} records)")

display_cols = ['farmer_id', 'farmer_name', 'crop_type', 'farm_size_acres', 'irrigation_type', 'soil_type', 'loan_amount', 'outstanding_loan', 'financial_history_score']
st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)
