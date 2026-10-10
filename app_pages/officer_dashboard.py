import pandas as pd
import streamlit as st

from services.field_verification_service import (
    REQUESTED,
    REVIEWED,
    SUBMITTED,
    list_field_requests,
)

st.title("Field Officer Dashboard")
st.write("View bank-assigned inspections and track reports submitted to the bank.")

requests = list_field_requests()
pending = [item for item in requests if item["status"] == REQUESTED]
submitted = [item for item in requests if item["status"] == SUBMITTED]
reviewed = [item for item in requests if item["status"] == REVIEWED]

columns = st.columns(3)
columns[0].metric("Assigned requests", len(pending))
columns[1].metric("Reports awaiting bank review", len(submitted))
columns[2].metric("Reviewed reports", len(reviewed))

st.markdown("---")
st.subheader("Field verification requests")
if not requests:
    st.info("There are no bank requests yet. New assignments will appear here.")
else:
    rows = [
        {
            "Task": item["task_id"],
            "Farmer": item["farmer_name"],
            "Farmer ID": item["farmer_id"],
            "Crop": item["crop_type"],
            "Assigned officer": item["assigned_officer"],
            "Priority": item["priority"],
            "Scope": item["scope"],
            "Instructions": item["instructions"],
            "Status": item["status"],
        }
        for item in requests
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.info(
    "This shared demo portal does not authenticate field-officer identities. "
    "Reports are associated with the officer name entered by the banker."
)
