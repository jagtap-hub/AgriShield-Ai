from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func
from database import Base

class FarmerModel(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(String(50), unique=True, index=True)
    farmer_name = Column(String(100))
    loan_amount = Column(Float)
    outstanding_loan = Column(Float)
    loan_repayment_history = Column(String(100))
    financial_history_score = Column(Float)
    crop_type = Column(String(50))
    farm_size_acres = Column(Float)
    irrigation_type = Column(String(50))
    soil_type = Column(String(50))
    historical_yield = Column(Float)
    previous_yield = Column(Float)
    rainfall_mm = Column(Float)
    temperature_c = Column(Float)
    soil_moisture = Column(Float)
    crop_health_index = Column(Float)
    yield_tons = Column(Float)


class FieldVerificationRequestModel(Base):
    __tablename__ = "field_verification_requests"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(40), unique=True, index=True, nullable=False)
    farmer_id = Column(String(50), nullable=False, index=True)
    farmer_name = Column(String(100), nullable=False)
    crop_type = Column(String(50), nullable=False)
    assigned_officer = Column(String(100), nullable=False, index=True)
    requested_by = Column(String(100), nullable=False)
    branch = Column(String(100), nullable=False)
    scope = Column(Text, nullable=False)
    priority = Column(String(30), nullable=False)
    instructions = Column(Text, nullable=False, default="")
    status = Column(String(20), nullable=False, default="Requested", index=True)
    observed_crop_health = Column(String(30))
    verified_damage_percent = Column(Float)
    observed_factor = Column(String(100))
    officer_notes = Column(Text)
    submitted_at = Column(DateTime)
    reviewed_by = Column(String(100))
    review_notes = Column(Text)
    reviewed_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class CreditDecisionModel(Base):
    __tablename__ = "credit_decisions"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(String(60), nullable=False, index=True)
    farmer_id = Column(String(50), nullable=False, index=True)
    decision = Column(String(50), nullable=False)
    proposed_amount = Column(Float, nullable=False)
    manager_identity = Column(String(120), nullable=False)
    rationale = Column(Text, nullable=False)
    conditions = Column(Text)
    requested_information = Column(Text)
    previous_status = Column(String(50), nullable=False)
    new_status = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class FarmerNotificationModel(Base):
    __tablename__ = "farmer_notifications"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(String(50), nullable=False, index=True)
    application_id = Column(String(60), nullable=False, index=True)
    title = Column(String(120), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
