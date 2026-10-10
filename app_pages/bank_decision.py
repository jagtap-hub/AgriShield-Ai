import html

import pandas as pd
import streamlit as st

from services.credit_decision_service import (
    DECISION_STATUSES,
    PENDING_REVIEW,
    list_application_decisions,
    save_credit_decision,
)
from services.db_service import fetch_dataset_farmers
from services.field_verification_service import list_field_requests
from services.ml_service import (
    assess_farmer_risk,
    calculate_yield_per_acre,
    get_model_and_data,
    get_yield_model_metadata,
    predict_total_yield,
)

st.set_page_config(page_title="Bank Manager Review", layout="wide")
st.markdown(
    """
    <style>
    .review-eyebrow {color:#9A7418;font-size:.78rem;font-weight:800;letter-spacing:.14em}
    .review-title {color:#103D2D;font-size:2.1rem;font-weight:800;margin:.2rem 0}
    .review-subtitle {color:#52665A;margin-bottom:1.2rem}
    .review-card {background:#fff;border:1px solid #DCE8DE;border-radius:14px;padding:18px 20px;height:100%}
    .review-label {color:#637367;font-size:.76rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase}
    .review-value {color:#143B2B;font-size:1.12rem;font-weight:750;margin-top:5px;overflow-wrap:anywhere}
    .review-small {color:#5B6A60;font-size:.83rem;margin-top:5px}
    .status-badge {display:inline-block;background:#FFF2CF;color:#73520A;border-radius:20px;padding:5px 11px;font-size:.8rem;font-weight:750}
    [data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input {
      background:#FFFFFF !important;color:#17251D !important;border:1px solid #9EB5A4 !important
    }
    [data-testid="stSelectbox"] [role="combobox"] {background:#FFFFFF !important;color:#17251D !important}
    [data-testid="stNumberInput"] input {background:#FFFFFF !important;color:#17251D !important}
    [data-testid="stForm"] {background:#F7FAF5;border:1px solid #DCE8DE;border-radius:14px;padding:18px}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="review-eyebrow">AGRISHIELD AI · BANKING WORKFLOW</div>', unsafe_allow_html=True)
st.markdown('<div class="review-title">Bank Manager Review</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="review-subtitle">Review application evidence, assess model outputs and record a reasoned decision.</div>',
    unsafe_allow_html=True,
)

farmers = fetch_dataset_farmers()
farmer_by_id = {str(farmer["farmer_id"]): farmer for farmer in farmers}
if not farmer_by_id:
    st.error("No applicant profiles are available in crop_data.csv.")
    st.stop()

application_id_by_farmer = {
    farmer_id: f"DEMO-{farmer_id}" for farmer_id in farmer_by_id
}
farmer_id_by_application = {
    application_id: farmer_id
    for farmer_id, application_id in application_id_by_farmer.items()
}
application_options = list(farmer_id_by_application)
selection = st.selectbox(
    "Select application to review",
    options=application_options,
    format_func=lambda application_id: (
        f"{application_id} — "
        f"{farmer_by_id[farmer_id_by_application[application_id]]['farmer_name']} "
        f"({farmer_by_id[farmer_id_by_application[application_id]]['crop_type']})"
    ),
    key="credit_decision_application",
)
farmer_id = farmer_id_by_application[selection]
farmer = farmer_by_id[farmer_id]
application_decisions = list_application_decisions(selection)
latest_decision = application_decisions[0] if application_decisions else None
application_status = latest_decision["new_status"] if latest_decision else PENDING_REVIEW

status_html = html.escape(application_status)
card_columns = st.columns([1, 1.25, 1, 1, 1.25, 1])
card_values = (
    ("Application ID", selection, "Generated demo reference"),
    ("Farmer name", farmer["farmer_name"], farmer_id),
    ("District", "Not provided", "No location field in dataset"),
    ("Crop", farmer["crop_type"], f"{farmer['farm_size_acres']:.1f} acres"),
    ("Requested loan", f"₹{farmer['loan_amount']:,.0f}", "From sample dataset"),
)
for column, (label, value, detail) in zip(card_columns, card_values):
    column.markdown(
        f'<div class="review-card"><div class="review-label">{html.escape(label)}</div>'
        f'<div class="review-value">{html.escape(str(value))}</div>'
        f'<div class="review-small">{html.escape(str(detail))}</div></div>',
        unsafe_allow_html=True,
    )
card_columns[5].markdown(
    f'<div class="review-card"><div class="review-label">Application status</div>'
    f'<div style="margin-top:12px"><span class="status-badge">{status_html}</span></div>'
    '<div class="review-small">Prototype decision history</div></div>',
    unsafe_allow_html=True,
)

st.warning(
    "This profile and application reference come from generated sample data. "
    "They are not a real loan application; the page is a prototype and does not "
    "authorize or guarantee lending."
)

with st.expander("Review checklist", expanded=True):
    checks = st.columns(5)
    check_items = (
        ("Farmer and loan details", "Loaded from sample CSV"),
        ("AI yield assessment", "Trained yield model"),
        ("Credit-risk evidence", "Unvalidated demo indicator"),
        ("Field verification", "See report below"),
        ("Supporting documents", "No document records"),
    )
    for column, (label, detail) in zip(checks, check_items):
        column.markdown(f"**{label}**")
        column.caption(detail)

st.markdown("## AI assessment results")
yield_prediction = None
try:
    model, _, feature_columns = get_model_and_data()
    model_metadata = get_yield_model_metadata()
    model_input = pd.DataFrame(
        [
            {
                "Rainfall_mm": farmer["rainfall_mm"],
                "Temperature_C": farmer["temperature_c"],
                "Soil_Moisture": farmer["soil_moisture"],
                "Farm_Size_acres": farmer["farm_size_acres"],
                "Crop_Health_Index": farmer["crop_health_index"],
            }
        ],
        columns=feature_columns,
    )
    yield_prediction = predict_total_yield(model, model_input)
except (FileNotFoundError, ValueError) as exc:
    st.error(f"Trained crop-yield prediction unavailable: {exc}")
    model_metadata = {"metrics": {}}

try:
    risk_assessment = assess_farmer_risk(farmer)
except ValueError as exc:
    risk_assessment = None
    st.error(f"Demo credit-risk indicator unavailable: {exc}")

ai_columns = st.columns(4)
if yield_prediction is not None:
    ai_columns[0].metric("Predicted crop yield", f"{yield_prediction:.2f} tons")
    try:
        per_acre = calculate_yield_per_acre(
            yield_prediction, farmer["farm_size_acres"]
        )
    except (TypeError, ValueError) as exc:
        ai_columns[1].warning(f"Yield per acre unavailable: {exc}")
    else:
        ai_columns[1].metric("Yield per acre", f"{per_acre:.2f} tons/acre")
else:
    ai_columns[0].metric("Predicted crop yield", "Unavailable")
    ai_columns[1].metric("Yield per acre", "Unavailable")

if risk_assessment:
    ai_columns[2].metric(
        "Credit-risk score",
        f"{risk_assessment['score']:.1f} / 100",
    )
    ai_columns[3].metric(
        "Risk category",
        risk_assessment["category"],
        help="Unvalidated demo indicator; not a model-derived default probability.",
    )
else:
    ai_columns[2].metric("Credit-risk score", "Unavailable")
    ai_columns[3].metric("Risk category", "Unavailable")

if yield_prediction is not None and model_metadata.get("metrics"):
    metrics = model_metadata["metrics"]
    st.caption(
        "Yield is a trained Random Forest prediction. Current synthetic-data holdout "
        f"metrics: MAE {metrics['mae']:.2f} tons, RMSE {metrics['rmse']:.2f} tons, "
        f"R² {metrics['r2']:.3f} ({metrics['test_rows']} test rows). "
        "These are not field-validated performance results."
    )
st.caption(
    "The credit-risk score is a provisional rule applied to generated repayment "
    "history and outstanding balance; no default classifier is trained because "
    "the dataset has no verified repayment outcome labels."
)

financial_columns = st.columns(3)
financial_columns[0].metric("Original loan", f"₹{farmer['loan_amount']:,.0f}")
financial_columns[1].metric(
    "Outstanding balance", f"₹{farmer['outstanding_loan']:,.0f}"
)
financial_columns[2].metric(
    "Recorded repayment history", str(farmer["loan_repayment_history"])
)

if risk_assessment:
    st.markdown("### Risk factors")
    for factor in risk_assessment["factors"]:
        st.markdown(
            f"- **{factor['name']}** — {factor['observed_value']}. "
            f"{factor['explanation']}"
        )
    st.caption(risk_assessment["additional_factor_status"])
    st.caption(
        "Weather and yield are not included in the credit indicator. There are no "
        "verified crop-season weather baselines, crop prices, costs, repayment "
        "capacity, or actual credit outcomes."
    )

st.markdown("## Field officer verification")
field_reports = [
    report
    for report in list_field_requests()
    if report["farmer_id"] == farmer_id
]
if not field_reports:
    st.info("Farm inspection status: No field verification request is linked to this sample profile.")
else:
    report_options = [report["task_id"] for report in field_reports]
    selected_task = st.selectbox(
        "Inspection report",
        options=report_options,
        format_func=lambda task_id: next(
            f"{task_id} — {report['status']}"
            for report in field_reports
            if report["task_id"] == task_id
        ),
    )
    report = next(item for item in field_reports if item["task_id"] == selected_task)
    report_columns = st.columns(4)
    report_columns[0].metric("Inspection status", report["status"])
    report_columns[1].metric(
        "Officer", report["assigned_officer"] or "Not assigned"
    )
    report_columns[2].metric(
        "Observed crop condition",
        report["observed_crop_health"] or "Not reported",
    )
    damage = report["verified_damage_percent"]
    report_columns[3].metric(
        "Verified damage", f"{damage:.0f}%" if damage is not None else "Not reported"
    )
    st.markdown(f"**Observed factor:** {report['observed_factor'] or 'Not reported'}")
    st.markdown(f"**Verification scope:** {report['scope']}")
    st.markdown(f"**Officer remarks:** {report['officer_notes'] or 'No remarks submitted.'}")
    st.markdown("**Document verification:** Not recorded in the current officer report workflow.")
    st.markdown("**Uploaded photos:** No photo attachment is recorded for this inspection.")
    if report["review_notes"]:
        st.markdown(f"**Previous bank report review:** {report['review_notes']}")

st.markdown("## Supporting documents")
st.info(
    "No application-document upload or verification records are connected to this "
    "dataset. Confirm original documents through your approved process."
)

st.markdown("## Final decision")
bank_user = st.session_state.get("bank_user") or {}
default_manager = str(bank_user.get("name", "")).strip()
manager_identity = st.text_input(
    "Manager / officer identity",
    value=default_manager,
    help="Recorded in the decision audit trail. This prototype does not authenticate identities.",
)
decision_options = list(DECISION_STATUSES)
decision = st.selectbox("Decision", options=decision_options, key="credit_decision_choice")

with st.form("credit_decision_form"):
    if decision == "Reject":
        proposed_amount = 0.0
        st.caption("Rejected application: proposed approved amount is recorded as ₹0.")
    else:
        proposed_amount = st.number_input(
            "Proposed loan amount (₹)",
            min_value=1.0,
            max_value=float(farmer["loan_amount"]),
            value=float(farmer["loan_amount"]),
            step=1000.0,
            help="Must be positive and cannot exceed the requested amount.",
        )

    rationale_required = decision in {
        "Reject",
        "Request additional verification",
    }
    rationale = st.text_area(
        "Decision rationale / manager notes"
        + (" (required)" if rationale_required else ""),
        placeholder="Explain the evidence and reasoning for this decision.",
    )
    conditions = ""
    requested_information = ""
    if decision == "Conditional approval":
        conditions = st.text_area(
            "Approval conditions (required)",
            placeholder="Specify conditions the applicant must satisfy.",
        )
    elif decision == "Request additional verification":
        requested_information = st.text_area(
            "Additional information or verification required (required)",
            placeholder="For example, a field visit, missing document, or updated farm evidence.",
        )

    submitted = st.form_submit_button(
        "Save decision to audit history",
        type="primary",
        width="stretch",
    )

if submitted:
    try:
        saved_decision = save_credit_decision(
            application_id=selection,
            farmer_id=farmer_id,
            decision=decision,
            proposed_amount=proposed_amount,
            requested_amount=float(farmer["loan_amount"]),
            manager_identity=manager_identity,
            rationale=rationale,
            conditions=conditions,
            requested_information=requested_information,
        )
    except ValueError as exc:
        st.error(str(exc))
    else:
        st.success(
            f"Decision saved for {selection}. Status: {saved_decision['new_status']}."
        )
        st.rerun()

if application_decisions:
    st.markdown("## Decision audit history")
    audit_rows = [
        {
            "Timestamp": record["created_at"],
            "Application": record["application_id"],
            "Manager": record["manager_identity"],
            "Decision": record["decision"],
            "Amount (₹)": record["proposed_amount"],
            "Previous status": record["previous_status"],
            "New status": record["new_status"],
            "Rationale": record["rationale"],
        }
        for record in application_decisions
    ]
    st.dataframe(audit_rows, width="stretch", hide_index=True)

st.caption(
    "Prototype decisions are stored in the configured application database for "
    "demonstration and audit review. They do not approve, reject, or authorize a real loan."
)
