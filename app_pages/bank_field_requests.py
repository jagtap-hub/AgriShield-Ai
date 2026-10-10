import pandas as pd
import streamlit as st

from services.db_service import fetch_dataset_farmers
from services.field_verification_service import (
    REVIEWED,
    SUBMITTED,
    create_field_request,
    list_field_requests,
    review_field_report,
)

st.title("Field Verification Requests")
st.write(
    "Send a verification request to a field officer and review the report they submit."
)

farmers = fetch_dataset_farmers()
farmer_by_id = {farmer["farmer_id"]: farmer for farmer in farmers}
if not farmer_by_id:
    st.error("No farmer profiles are available in crop_data.csv.")
    st.stop()

bank_user = st.session_state.get("bank_user") or {}
requested_by = bank_user.get("name", "Bank Credit Team")
branch = bank_user.get("branch", "Unspecified branch")

left, right = st.columns([1.1, 1])
with left:
    st.subheader("Create inspection request")
    with st.form("field_req_form"):
        farmer_id = st.selectbox(
            "Select borrower from dataset",
            options=list(farmer_by_id),
            format_func=lambda selected_id: (
                f"{selected_id} — {farmer_by_id[selected_id]['farmer_name']} "
                f"({farmer_by_id[selected_id]['crop_type']})"
            ),
        )
        assigned_officer = st.text_input("Assigned field officer's name")
        st.markdown("**Verification scope**")
        check_crop = st.checkbox("Crop condition and damage", value=True)
        check_soil = st.checkbox("Soil moisture and irrigation")
        check_land = st.checkbox("Land boundary and acreage")
        priority = st.selectbox("Priority", ["Normal", "Urgent", "Critical"])
        instructions = st.text_area("Instructions for the field officer")
        submitted = st.form_submit_button(
            "Dispatch field request", type="primary"
        )

    if submitted:
        scope = [
            label
            for enabled, label in (
                (check_crop, "Crop condition and damage"),
                (check_soil, "Soil moisture and irrigation"),
                (check_land, "Land boundary and acreage"),
            )
            if enabled
        ]
        try:
            new_request = create_field_request(
                farmer=farmer_by_id[farmer_id],
                assigned_officer=assigned_officer,
                requested_by=requested_by,
                branch=branch,
                scope=scope,
                priority=priority,
                instructions=instructions,
            )
        except ValueError as exc:
            st.error(str(exc))
        else:
            st.success(
                f"Request {new_request['task_id']} dispatched to "
                f"{new_request['assigned_officer']}."
            )
            st.rerun()

with right:
    st.subheader("Request tracker")
    requests = list_field_requests()
    if requests:
        tracker_rows = [
            {
                "Task": item["task_id"],
                "Farmer": item["farmer_name"],
                "Crop": item["crop_type"],
                "Assigned officer": item["assigned_officer"],
                "Priority": item["priority"],
                "Status": item["status"],
            }
            for item in requests
        ]
        st.dataframe(pd.DataFrame(tracker_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No field verification requests have been dispatched.")

st.markdown("---")
st.subheader("Submitted field reports")
submitted_reports = [item for item in requests if item["status"] in {SUBMITTED, REVIEWED}]
if not submitted_reports:
    st.info("No officer reports have been submitted yet.")
else:
    report_rows = [
        {
            "Task": item["task_id"],
            "Farmer": item["farmer_name"],
            "Officer": item["assigned_officer"],
            "Crop health": item["observed_crop_health"],
            "Verified damage (%)": item["verified_damage_percent"],
            "Observed factor": item["observed_factor"],
            "Officer notes": item["officer_notes"],
            "Status": item["status"],
            "Review notes": item["review_notes"] or "",
        }
        for item in submitted_reports
    ]
    st.dataframe(pd.DataFrame(report_rows), use_container_width=True, hide_index=True)

    needs_review = [item for item in submitted_reports if item["status"] == SUBMITTED]
    if needs_review:
        st.markdown("### Review a submitted report")
        with st.form("field_report_review_form"):
            task_id = st.selectbox(
                "Submitted report",
                options=[item["task_id"] for item in needs_review],
                format_func=lambda selected_task: next(
                    f"{item['task_id']} — {item['farmer_name']}"
                    for item in needs_review
                    if item["task_id"] == selected_task
                ),
            )
            review_notes = st.text_area("Bank review notes")
            review_submitted = st.form_submit_button("Mark report reviewed")

        if review_submitted:
            try:
                reviewed = review_field_report(
                    task_id=task_id,
                    reviewed_by=requested_by,
                    review_notes=review_notes,
                )
            except (LookupError, ValueError) as exc:
                st.error(str(exc))
            else:
                st.success(f"Report {reviewed['task_id']} marked as reviewed.")
                st.rerun()

st.caption(
    "Requests and reports are stored in the shared application database. "
    "Officer names are entered by users; identity authentication is not configured."
)
