import streamlit as st

from services.credit_decision_service import (
    PENDING_REVIEW,
    list_application_decisions,
    list_farmer_notifications,
)


def render_farmer_loan_notifications(farmer_id: str) -> None:
    """Show persisted loan updates for the currently selected farmer profile."""
    application_id = f"DEMO-{farmer_id}"
    decisions = list_application_decisions(application_id)
    notifications = list_farmer_notifications(farmer_id)
    current_status = decisions[0]["new_status"] if decisions else PENDING_REVIEW

    st.subheader("Loan application status")
    if current_status == PENDING_REVIEW:
        st.info(
            f"Application {application_id} is pending bank manager review."
        )
    elif current_status == "Rejected":
        st.error(f"Application {application_id} status: {current_status}.")
    elif current_status == "Additional information requested":
        st.warning(f"Application {application_id} status: {current_status}.")
    else:
        st.success(f"Application {application_id} status: {current_status}.")

    st.caption(
        "Updates appear here after a manager records a decision. Notifications are "
        "stored in this prototype database and are not SMS, email, or push messages."
    )
    st.markdown("### Loan notifications")
    if not notifications:
        st.caption("No manager decision notifications yet.")
        return

    for notification in notifications:
        st.markdown(f"**{notification['title']}**")
        st.write(notification["message"])
        timestamp = notification["created_at"]
        if timestamp:
            st.caption(f"Recorded: {timestamp:%Y-%m-%d %H:%M UTC}")
        st.markdown("---")
