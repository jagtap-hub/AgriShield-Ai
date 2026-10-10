import streamlit as st

from services.field_verification_service import (
    REQUESTED,
    list_field_requests,
    submit_field_report,
)

st.title("Field Officer Verification")
st.write("Inspect the assigned case and send a report back to the requesting bank.")

requests = [item for item in list_field_requests() if item["status"] == REQUESTED]
if not requests:
    st.info("No requests are waiting for a field report.")
    st.caption("New bank assignments appear here as soon as they are dispatched.")
    st.stop()

officers = sorted({item["assigned_officer"] for item in requests}, key=str.casefold)
officer_name = st.selectbox("Field officer", options=officers)
assigned_requests = [
    item
    for item in requests
    if item["assigned_officer"].casefold() == officer_name.casefold()
]

task_id = st.selectbox(
    "Assigned inspection task",
    options=[item["task_id"] for item in assigned_requests],
    format_func=lambda selected_task: next(
        f"{item['task_id']} — {item['farmer_name']} ({item['crop_type']})"
        for item in assigned_requests
        if item["task_id"] == selected_task
    ),
)
selected_request = next(item for item in assigned_requests if item["task_id"] == task_id)

with st.container(border=True):
    st.markdown(f"**Requested by:** {selected_request['requested_by']}")
    st.markdown(f"**Branch:** {selected_request['branch']}")
    st.markdown(f"**Priority:** {selected_request['priority']}")
    st.markdown(f"**Scope:** {selected_request['scope']}")
    st.markdown(f"**Instructions:** {selected_request['instructions'] or 'None provided'}")

with st.form("officer_verification_form"):
    first, second = st.columns(2)
    with first:
        observed_health = st.selectbox(
            "Observed crop health",
            ["Excellent", "Good", "Moderate stress", "Severe stress"],
        )
        verified_damage = st.slider("Verified crop damage (%)", 0, 100, 0)
    with second:
        observed_factor = st.selectbox(
            "Primary factor observed",
            [
                "Normal growth",
                "Drought or heat stress",
                "Excess rainfall or waterlogging",
                "Pest or disease",
                "Other field condition",
            ],
        )
    officer_notes = st.text_area("Field observations and notes")
    submitted = st.form_submit_button("Submit report to bank", type="primary")

if submitted:
    try:
        report = submit_field_report(
            task_id=task_id,
            officer_name=officer_name,
            observed_crop_health=observed_health,
            verified_damage_percent=verified_damage,
            observed_factor=observed_factor,
            officer_notes=officer_notes,
        )
    except (LookupError, PermissionError, ValueError) as exc:
        st.error(str(exc))
    else:
        st.success(
            f"Report for {report['task_id']} submitted to the bank for review."
        )
        st.rerun()

st.caption(
    "The report is saved in the shared application database and becomes visible "
    "on the bank's Field Verification Requests page."
)
