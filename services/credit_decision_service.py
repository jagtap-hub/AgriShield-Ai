from datetime import datetime, timezone
from math import isfinite

from database import Base, SessionLocal, engine
from models import CreditDecisionModel, FarmerNotificationModel

PENDING_REVIEW = "Pending review"

DECISION_STATUSES = {
    "Approve": "Approved",
    "Conditional approval": "Conditionally approved",
    "Request additional verification": "Additional information requested",
    "Reject": "Rejected",
}


def _serialize_decision(record: CreditDecisionModel) -> dict:
    return {
        "application_id": record.application_id,
        "farmer_id": record.farmer_id,
        "decision": record.decision,
        "proposed_amount": record.proposed_amount,
        "manager_identity": record.manager_identity,
        "rationale": record.rationale,
        "conditions": record.conditions,
        "requested_information": record.requested_information,
        "previous_status": record.previous_status,
        "new_status": record.new_status,
        "created_at": record.created_at,
    }


def _serialize_notification(record: FarmerNotificationModel) -> dict:
    return {
        "farmer_id": record.farmer_id,
        "application_id": record.application_id,
        "title": record.title,
        "message": record.message,
        "status": record.status,
        "created_at": record.created_at,
    }


def list_application_decisions(application_id: str) -> list[dict]:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        records = (
            db.query(CreditDecisionModel)
            .filter(CreditDecisionModel.application_id == application_id)
            .order_by(CreditDecisionModel.id.desc())
            .all()
        )
        return [_serialize_decision(record) for record in records]


def list_farmer_notifications(farmer_id: str, limit: int = 20) -> list[dict]:
    if not farmer_id.strip():
        raise ValueError("Farmer ID is required to load notifications.")
    if limit < 1:
        raise ValueError("Notification limit must be positive.")

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        records = (
            db.query(FarmerNotificationModel)
            .filter(FarmerNotificationModel.farmer_id == farmer_id)
            .order_by(FarmerNotificationModel.id.desc())
            .limit(limit)
            .all()
        )
        return [_serialize_notification(record) for record in records]


def save_credit_decision(
    *,
    application_id: str,
    farmer_id: str,
    decision: str,
    proposed_amount: float,
    requested_amount: float,
    manager_identity: str,
    rationale: str,
    conditions: str = "",
    requested_information: str = "",
) -> dict:
    if decision not in DECISION_STATUSES:
        raise ValueError("Select a valid credit decision.")
    manager = manager_identity.strip()
    if not manager:
        raise ValueError("Manager identity is required.")
    rationale_text = rationale.strip()
    if decision in {"Reject", "Request additional verification"} and not rationale_text:
        raise ValueError(
            "A rationale is required to reject or request additional verification."
        )
    if decision == "Conditional approval" and not conditions.strip():
        raise ValueError("Enter the conditions for a conditional approval.")
    if decision == "Request additional verification" and not requested_information.strip():
        raise ValueError("Specify the additional information or verification required.")

    try:
        amount = float(proposed_amount)
        maximum = float(requested_amount)
    except (TypeError, ValueError) as exc:
        raise ValueError("Proposed and requested loan amounts must be numeric.") from exc
    if not isfinite(amount) or not isfinite(maximum):
        raise ValueError("Loan amounts must be finite numbers.")
    if amount < 0 or maximum <= 0:
        raise ValueError("Loan amounts must be non-negative and requested amount positive.")
    if decision != "Reject" and amount <= 0:
        raise ValueError("Proposed amount must be greater than zero.")
    if amount > maximum:
        raise ValueError("Proposed amount cannot exceed the requested loan amount.")
    if decision == "Reject" and amount != 0:
        raise ValueError("A rejected application must have a proposed amount of zero.")

    Base.metadata.create_all(bind=engine)
    with SessionLocal.begin() as db:
        latest = (
            db.query(CreditDecisionModel)
            .filter(CreditDecisionModel.application_id == application_id)
            .order_by(CreditDecisionModel.id.desc())
            .first()
        )
        previous_status = latest.new_status if latest else PENDING_REVIEW
        record = CreditDecisionModel(
            application_id=application_id,
            farmer_id=farmer_id,
            decision=decision,
            proposed_amount=amount,
            manager_identity=manager,
            rationale=rationale_text,
            conditions=conditions.strip() or None,
            requested_information=requested_information.strip() or None,
            previous_status=previous_status,
            new_status=DECISION_STATUSES[decision],
            created_at=datetime.now(timezone.utc),
        )
        db.add(record)
        db.flush()
        db.refresh(record)

        amount_text = f"Rs {amount:,.0f}"
        if decision == "Approve":
            message = (
                f"Your application {application_id} has been approved for "
                f"{amount_text}. This prototype status does not confirm loan "
                "disbursement."
            )
        elif decision == "Conditional approval":
            message = (
                f"Your application {application_id} has been conditionally approved "
                f"for {amount_text}. Conditions: {conditions.strip()}"
            )
        elif decision == "Request additional verification":
            message = (
                f"Your application {application_id} is awaiting additional "
                f"verification. Please provide: {requested_information.strip()}"
            )
        else:
            message = (
                f"Your application {application_id} has been rejected. "
                "Please contact your bank representative for next steps."
            )

        db.add(
            FarmerNotificationModel(
                farmer_id=farmer_id,
                application_id=application_id,
                title=f"Loan application {record.new_status}",
                message=message,
                status=record.new_status,
                created_at=record.created_at,
            )
        )
        db.flush()
        return _serialize_decision(record)
