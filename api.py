from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
import os

from database import engine, Base, SessionLocal, get_db
from models import FarmerModel
from services.ml_service import assess_farmer_risk
from services.db_service import DATA_FILE, fetch_dataset_farmers

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AgriShield AI Backend API",
    description="Farmer profiles and explicitly provisional financial risk indicators",
)


def find_farmer(farmer_id: str, db: Session):
    if DATA_FILE.is_file():
        farmer = next(
            (
                profile
                for profile in fetch_dataset_farmers()
                if profile["farmer_id"] == farmer_id
            ),
            None,
        )
        if farmer is not None:
            return farmer

    return db.query(FarmerModel).filter(FarmerModel.farmer_id == farmer_id).first()


def seed_database_if_empty():
    db = SessionLocal()
    try:
        count = db.query(FarmerModel).count()
        if count == 0 and os.path.exists("crop_data.csv"):
            df = pd.read_csv("crop_data.csv")
            for _, row in df.iterrows():
                farmer = FarmerModel(
                    farmer_id=str(row['Farmer_ID']),
                    farmer_name=str(row['Farmer_Name']),
                    loan_amount=float(row['Loan_Amount']),
                    outstanding_loan=float(row['Outstanding_Loan']),
                    loan_repayment_history=str(row['Loan_Repayment_History']),
                    financial_history_score=float(row['Financial_History_Score']),
                    crop_type=str(row['Crop_Type']),
                    farm_size_acres=float(row['Farm_Size_acres']),
                    irrigation_type=str(row['Irrigation_Type']),
                    soil_type=str(row['Soil_Type']),
                    historical_yield=float(row['Historical_Yield']),
                    previous_yield=float(row['Previous_Yield']),
                    rainfall_mm=float(row['Rainfall_mm']),
                    temperature_c=float(row['Temperature_C']),
                    soil_moisture=float(row['Soil_Moisture']),
                    crop_health_index=float(row['Crop_Health_Index']),
                    yield_tons=float(row['Yield_tons'])
                )
                db.add(farmer)
            db.commit()
            print(f"Database seeded with {len(df)} records from crop_data.csv.")
    finally:
        db.close()

seed_database_if_empty()

@app.get("/")
def read_root():
    return {"status": "online", "system": "AgriShield AI Backend API"}

@app.get("/api/farmers")
def get_farmers(db: Session = Depends(get_db)):
    if DATA_FILE.is_file():
        return fetch_dataset_farmers()
    farmers = db.query(FarmerModel).all()
    return farmers

@app.get("/api/farmers/{farmer_id}")
def get_farmer_by_id(farmer_id: str, db: Session = Depends(get_db)):
    farmer = find_farmer(farmer_id, db)
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer profile not found")
    return farmer


@app.get("/api/farmers/{farmer_id}/assessment")
def get_farmer_risk_assessment(farmer_id: str, db: Session = Depends(get_db)):
    farmer = find_farmer(farmer_id, db)
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer profile not found")

    field = farmer.get if isinstance(farmer, dict) else lambda name: getattr(farmer, name)
    try:
        assessment = assess_farmer_risk(
            {
                "loan_amount": field("loan_amount"),
                "outstanding_loan": field("outstanding_loan"),
                "loan_repayment_history": field("loan_repayment_history"),
                "crop_health_index": field("crop_health_index"),
            }
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {"farmer_id": field("farmer_id"), "assessment": assessment}
