from datetime import datetime
from uuid import uuid4

from database import Base, SessionLocal, engine
from models import FieldVerificationRequestModel


REQUESTED = "Requested"
SUBMITTED = "Submitted"
REVIEWED = "Reviewed"


def _ensure_storage() -> None:
    Base.metadata.create_all(bind=engine)


def _serialize_request(request: FieldVerificationRequestModel) -> dict:
    return {
        "task_id": request.task_id,
        "farmer_id": request.farmer_id,
        "farmer_name": request.farmer_name,
        "crop_type": request.crop_type,
        "assigned_officer": request.assigned_officer,
        "requested_by": request.requested_by,
        "branch": request.branch,
        "scope": request.scope,
        "priority": request.priority,
        "instructions": request.instructions,
        "status": request.status,
        "observed_crop_health": request.observed_crop_health,
        "verified_damage_percent": request.verified_damage_percent,
        "observed_factor": request.observed_factor,
        "officer_notes": request.officer_notes,
        "submitted_at": request.submitted_at,
        "reviewed_by": request.reviewed_by,
        "review_notes": request.review_notes,
        "reviewed_at": request.reviewed_at,
        "created_at": request.created_at,
    }


def list_field_requests() -> list[dict]:
    _ensure_storage()
    db = SessionLocal()
    try:
        requests = (
            db.query(FieldVerificationRequestModel)
            .order_by(FieldVerificationRequestModel.id.desc())
            .all()
        )
        return [_serialize_request(request) for request in requests]
    finally:
        db.close()


def create_field_request(
    farmer: dict,
    assigned_officer: str,
    requested_by: str,
    branch: str,
    scope: list[str],
    priority: str,
    instructions: str,
) -> dict:
    officer = assigned_officer.strip()
    if not officer:
        raise ValueError("An assigned field officer is required.")
    if not scope:
        raise ValueError("Select at least one verification requirement.")
    if priority not in {"Normal", "Urgent", "Critical"}:
        raise ValueError("Priority must be Normal, Urgent, or Critical.")

    _ensure_storage()
    with SessionLocal.begin() as db:
        request = FieldVerificationRequestModel(
            task_id=f"TSK-{uuid4().hex[:10].upper()}",
            farmer_id=str(farmer["farmer_id"]),
            farmer_name=str(farmer["farmer_name"]),
            crop_type=str(farmer["crop_type"]),
            assigned_officer=officer,
            requested_by=requested_by.strip() or "Bank Credit Team",
            branch=branch.strip() or "Unspecified branch",
            scope="; ".join(scope),
            priority=priority,
            instructions=instructions.strip(),
            status=REQUESTED,
        )
        db.add(request)
        db.flush()
        db.refresh(request)
        return _serialize_request(request)


def submit_field_report(
    task_id: str,
    officer_name: str,
    observed_crop_health: str,
    verified_damage_percent: int,
    observed_factor: str,
    officer_notes: str,
) -> dict:
    officer = officer_name.strip()
    if not officer:
        raise ValueError("Officer name is required to submit a report.")
    if not 0 <= verified_damage_percent <= 100:
        raise ValueError("Verified damage must be between 0 and 100 percent.")

    _ensure_storage()
    with SessionLocal.begin() as db:
        request = (
            db.query(FieldVerificationRequestModel)
            .filter(FieldVerificationRequestModel.task_id == task_id)
            .first()
        )
        if request is None:
            raise LookupError(f"Field request {task_id} was not found.")
        if request.assigned_officer.casefold() != officer.casefold():
            raise PermissionError("This request is assigned to a different officer.")
        if request.status != REQUESTED:
            raise ValueError(f"Cannot submit a report while status is {request.status}.")

        request.observed_crop_health = observed_crop_health
        request.verified_damage_percent = float(verified_damage_percent)
        request.observed_factor = observed_factor
        request.officer_notes = officer_notes.strip()
        request.submitted_at = datetime.now()
        request.status = SUBMITTED
        db.flush()
        db.refresh(request)
        return _serialize_request(request)


def review_field_report(task_id: str, reviewed_by: str, review_notes: str) -> dict:
    reviewer = reviewed_by.strip()
    if not reviewer:
        raise ValueError("Bank reviewer name is required.")

    _ensure_storage()
    with SessionLocal.begin() as db:
        request = (
            db.query(FieldVerificationRequestModel)
            .filter(FieldVerificationRequestModel.task_id == task_id)
            .first()
        )
        if request is None:
            raise LookupError(f"Field request {task_id} was not found.")
        if request.status != SUBMITTED:
            raise ValueError("Only submitted field reports can be reviewed.")

        request.reviewed_by = reviewer
        request.review_notes = review_notes.strip()
        request.reviewed_at = datetime.now()
        request.status = REVIEWED
        db.flush()
        db.refresh(request)
        return _serialize_request(request)
