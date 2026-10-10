import unittest
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import database
from database import Base
from services import field_verification_service as field_service


class FieldVerificationWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.test_engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.test_session = sessionmaker(bind=self.test_engine)
        self.engine_patch = patch.object(database, "engine", self.test_engine)
        self.session_patch = patch.object(
            field_service, "engine", self.test_engine
        )
        self.session_factory_patch = patch.object(
            field_service, "SessionLocal", self.test_session
        )
        self.engine_patch.start()
        self.session_patch.start()
        self.session_factory_patch.start()
        Base.metadata.create_all(bind=self.test_engine)

    def tearDown(self):
        self.session_factory_patch.stop()
        self.session_patch.stop()
        self.engine_patch.stop()
        self.test_engine.dispose()

    def test_bank_request_officer_report_and_bank_review_round_trip(self):
        request = field_service.create_field_request(
            farmer={
                "farmer_id": "FARM-TEST-1",
                "farmer_name": "Test Farmer",
                "crop_type": "Wheat",
            },
            assigned_officer="Officer Test",
            requested_by="Bank Reviewer",
            branch="Test Branch",
            scope=["Crop condition and damage"],
            priority="Urgent",
            instructions="Inspect the eastern plot.",
        )
        self.assertEqual(request["status"], field_service.REQUESTED)
        self.assertEqual(len(field_service.list_field_requests()), 1)

        with self.assertRaises(PermissionError):
            field_service.submit_field_report(
                request["task_id"],
                "Different Officer",
                "Good",
                0,
                "Normal growth",
                "",
            )

        report = field_service.submit_field_report(
            request["task_id"],
            "officer test",
            "Moderate stress",
            20,
            "Drought or heat stress",
            "Dry soil observed in the eastern plot.",
        )
        self.assertEqual(report["status"], field_service.SUBMITTED)
        self.assertEqual(report["verified_damage_percent"], 20.0)
        self.assertEqual(
            field_service.list_field_requests()[0]["officer_notes"],
            "Dry soil observed in the eastern plot.",
        )

        reviewed = field_service.review_field_report(
            request["task_id"], "Bank Reviewer", "Field report checked."
        )
        self.assertEqual(reviewed["status"], field_service.REVIEWED)
        self.assertEqual(reviewed["review_notes"], "Field report checked.")
        self.assertEqual(
            field_service.list_field_requests()[0]["reviewed_by"],
            "Bank Reviewer",
        )

        with self.assertRaises(ValueError):
            field_service.review_field_report(
                request["task_id"], "Bank Reviewer", ""
            )

    def test_rejects_requests_without_scope_or_a_valid_priority(self):
        farmer = {
            "farmer_id": "FARM-TEST-2",
            "farmer_name": "Another Farmer",
            "crop_type": "Rice",
        }
        with self.assertRaisesRegex(ValueError, "at least one"):
            field_service.create_field_request(
                farmer, "Officer Test", "Bank Reviewer", "Branch", [], "Normal", ""
            )
        with self.assertRaisesRegex(ValueError, "Priority"):
            field_service.create_field_request(
                farmer,
                "Officer Test",
                "Bank Reviewer",
                "Branch",
                ["Crop condition"],
                "ASAP",
                "",
            )
        self.assertEqual(field_service.list_field_requests(), [])

    def test_rejects_damage_outside_percentage_bounds(self):
        request = field_service.create_field_request(
            farmer={
                "farmer_id": "FARM-TEST-3",
                "farmer_name": "Bound Test",
                "crop_type": "Cotton",
            },
            assigned_officer="Officer Test",
            requested_by="Bank Reviewer",
            branch="Test Branch",
            scope=["Crop condition and damage"],
            priority="Normal",
            instructions="",
        )
        with self.assertRaisesRegex(ValueError, "between 0 and 100"):
            field_service.submit_field_report(
                request["task_id"],
                "Officer Test",
                "Good",
                101,
                "Normal growth",
                "",
            )


if __name__ == "__main__":
    unittest.main()
