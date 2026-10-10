import pandas as pd
import requests
from pathlib import Path
from database import SessionLocal
from models import FarmerModel

API_URL = "http://127.0.0.1:8000"
DATA_FILE = Path(__file__).resolve().parents[1] / "crop_data.csv"

DATASET_TO_PROFILE = {
    "Farmer_ID": "farmer_id",
    "Farmer_Name": "farmer_name",
    "Loan_Amount": "loan_amount",
    "Outstanding_Loan": "outstanding_loan",
    "Loan_Repayment_History": "loan_repayment_history",
    "Financial_History_Score": "financial_history_score",
    "Crop_Type": "crop_type",
    "Farm_Size_acres": "farm_size_acres",
    "Irrigation_Type": "irrigation_type",
    "Soil_Type": "soil_type",
    "Historical_Yield": "historical_yield",
    "Previous_Yield": "previous_yield",
    "Rainfall_mm": "rainfall_mm",
    "Temperature_C": "temperature_c",
    "Soil_Moisture": "soil_moisture",
    "Crop_Health_Index": "crop_health_index",
    "Yield_tons": "yield_tons",
}


def fetch_dataset_farmers():
    """Load farmer profiles from the project's CSV dataset."""
    if not DATA_FILE.is_file():
        raise FileNotFoundError(f"Farmer dataset was not found: {DATA_FILE}")

    df = pd.read_csv(DATA_FILE)
    missing_columns = [column for column in DATASET_TO_PROFILE if column not in df]
    if missing_columns:
        raise ValueError(
            f"Farmer dataset is missing required columns: {', '.join(missing_columns)}"
        )

    return (
        df.rename(columns=DATASET_TO_PROFILE)
        .loc[:, list(DATASET_TO_PROFILE.values())]
        .to_dict(orient="records")
    )

def fetch_all_farmers():
    # The CSV dataset is the source of truth for the bundled farmer profiles.
    if DATA_FILE.is_file():
        return fetch_dataset_farmers()

    # Try FastAPI backend first, fallback to direct DB query
    try:
        res = requests.get(f"{API_URL}/api/farmers", timeout=2)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    
    # DB Fallback
    db = SessionLocal()
    try:
        farmers = db.query(FarmerModel).all()
        return [
            {
                "farmer_id": f.farmer_id,
                "farmer_name": f.farmer_name,
                "loan_amount": f.loan_amount,
                "outstanding_loan": f.outstanding_loan,
                "loan_repayment_history": f.loan_repayment_history,
                "financial_history_score": f.financial_history_score,
                "crop_type": f.crop_type,
                "farm_size_acres": f.farm_size_acres,
                "irrigation_type": f.irrigation_type,
                "soil_type": f.soil_type,
                "historical_yield": f.historical_yield,
                "previous_yield": f.previous_yield,
                "rainfall_mm": f.rainfall_mm,
                "temperature_c": f.temperature_c,
                "soil_moisture": f.soil_moisture,
                "crop_health_index": f.crop_health_index,
                "yield_tons": f.yield_tons
            } for f in farmers
        ]
    finally:
        db.close()

def fetch_farmer_by_id(farmer_id: str):
    if DATA_FILE.is_file():
        profile = next(
            (
                farmer
                for farmer in fetch_dataset_farmers()
                if farmer["farmer_id"] == farmer_id
            ),
            None,
        )
        if profile is not None:
            return profile

    # Try FastAPI backend first, fallback to direct DB query
    try:
        res = requests.get(f"{API_URL}/api/farmers/{farmer_id}", timeout=2)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass

    db = SessionLocal()
    try:
        f = db.query(FarmerModel).filter(FarmerModel.farmer_id == farmer_id).first()
        if f:
            return {
                "farmer_id": f.farmer_id,
                "farmer_name": f.farmer_name,
                "loan_amount": f.loan_amount,
                "outstanding_loan": f.outstanding_loan,
                "loan_repayment_history": f.loan_repayment_history,
                "financial_history_score": f.financial_history_score,
                "crop_type": f.crop_type,
                "farm_size_acres": f.farm_size_acres,
                "irrigation_type": f.irrigation_type,
                "soil_type": f.soil_type,
                "historical_yield": f.historical_yield,
                "previous_yield": f.previous_yield,
                "rainfall_mm": f.rainfall_mm,
                "temperature_c": f.temperature_c,
                "soil_moisture": f.soil_moisture,
                "crop_health_index": f.crop_health_index,
                "yield_tons": f.yield_tons
            }
        return None
    finally:
        db.close()
