import importlib.util
import importlib
import unittest
from unittest.mock import patch


API_TEST_DEPENDENCIES = ("fastapi", "sqlalchemy", "httpx")


@unittest.skipUnless(
    all(importlib.util.find_spec(name) for name in API_TEST_DEPENDENCIES),
    "FastAPI, SQLAlchemy, and httpx are required for API response tests.",
)
class FarmerAssessmentAPITests(unittest.TestCase):
    def test_assessment_response_and_not_found_status(self):
        from fastapi.testclient import TestClient
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy.pool import StaticPool

        import database
        from database import Base, get_db
        from models import FarmerModel
        from services.db_service import fetch_dataset_farmers

        test_engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        test_session = sessionmaker(bind=test_engine)

        with patch.object(database, "engine", test_engine), patch.object(
            database, "SessionLocal", test_session
        ):
            api = importlib.import_module("api")

        db = test_session()
        db.add(
            FarmerModel(
                farmer_id="TEST-API-1",
                farmer_name="Test Farmer",
                loan_amount=100000,
                outstanding_loan=80000,
                loan_repayment_history="Mostly on time",
                financial_history_score=650,
                farm_size_acres=2,
                crop_health_index=0.7,
            )
        )
        db.add(
            FarmerModel(
                farmer_id="TEST-API-INVALID",
                farmer_name="Invalid Repayment History",
                loan_amount=100000,
                outstanding_loan=50000,
                loan_repayment_history="Unknown",
                financial_history_score=650,
                farm_size_acres=2,
                crop_health_index=0.7,
            )
        )
        db.commit()
        db.close()

        def override_get_db():
            session = test_session()
            try:
                yield session
            finally:
                session.close()

        api.app.dependency_overrides[get_db] = override_get_db
        try:
            with TestClient(api.app) as client:
                farmers_response = client.get("/api/farmers")
                response = client.get("/api/farmers/TEST-API-1/assessment")
                missing_response = client.get("/api/farmers/DOES-NOT-EXIST/assessment")
                invalid_response = client.get("/api/farmers/TEST-API-INVALID/assessment")
        finally:
            api.app.dependency_overrides.pop(get_db, None)
            test_engine.dispose()

        self.assertEqual(farmers_response.status_code, 200)
        self.assertEqual(farmers_response.json(), fetch_dataset_farmers())
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["farmer_id"], "TEST-API-1")
        self.assertEqual(payload["assessment"]["score"], 56.7)
        self.assertEqual(payload["assessment"]["category"], "Medium")
        self.assertEqual(len(payload["assessment"]["factors"]), 2)
        self.assertEqual(missing_response.status_code, 404)
        self.assertEqual(invalid_response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
