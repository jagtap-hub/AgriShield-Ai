import unittest
import math
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import database
from services import credit_decision_service as decision_service


class CreditDecisionServiceTests(unittest.TestCase):
    def setUp(self):
        self.test_engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.test_session = sessionmaker(bind=self.test_engine)
        self.engine_patch = patch.object(database, "engine", self.test_engine)
        self.service_engine_patch = patch.object(
            decision_service, "engine", self.test_engine
        )
        self.session_factory_patch = patch.object(
            decision_service, "SessionLocal", self.test_session
        )
        self.engine_patch.start()
        self.service_engine_patch.start()
        self.session_factory_patch.start()

    def tearDown(self):
        self.session_factory_patch.stop()
        self.service_engine_patch.stop()
        self.engine_patch.stop()
        self.test_engine.dispose()

    def save(self, **overrides):
        values = {
            "application_id": "DEMO-FARM-1",
            "farmer_id": "FARM-1",
            "decision": "Approve",
            "proposed_amount": 80000,
            "requested_amount": 100000,
            "manager_identity": "Manager One",
            "rationale": "Reviewed the available sample evidence.",
        }
        values.update(overrides)
        return decision_service.save_credit_decision(**values)

    def test_saves_decision_and_tracks_status_transition(self):
        first = self.save()
        self.assertEqual(first["previous_status"], decision_service.PENDING_REVIEW)
        self.assertEqual(first["new_status"], "Approved")

        second = self.save(
            decision="Conditional approval",
            proposed_amount=70000,
            conditions="Confirm the repayment schedule.",
        )
        self.assertEqual(second["previous_status"], "Approved")
        self.assertEqual(second["new_status"], "Conditionally approved")

        history = decision_service.list_application_decisions("DEMO-FARM-1")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["decision"], "Conditional approval")
        self.assertTrue(history[0]["created_at"])

    def test_saves_farmer_notification_with_each_decision(self):
        approved = self.save()
        self.save(
            decision="Request additional verification",
            rationale="Please complete the missing verification.",
            requested_information="Submit updated land records.",
        )

        notifications = decision_service.list_farmer_notifications("FARM-1")
        self.assertEqual(len(notifications), 2)
        self.assertEqual(
            notifications[0]["status"], "Additional information requested"
        )
        self.assertIn("updated land records", notifications[0]["message"])
        self.assertEqual(notifications[1]["status"], "Approved")
        self.assertIn("does not confirm loan disbursement", notifications[1]["message"])
        self.assertEqual(notifications[1]["application_id"], approved["application_id"])
        self.assertEqual(
            decision_service.list_farmer_notifications("OTHER-FARMER"),
            [],
        )

    def test_rejection_and_verification_request_require_reason_and_details(self):
        with self.assertRaisesRegex(ValueError, "rationale is required"):
            self.save(decision="Reject", proposed_amount=0, rationale="")
        with self.assertRaisesRegex(ValueError, "rationale is required"):
            self.save(
                decision="Request additional verification",
                rationale=" ",
                requested_information="Provide updated land records.",
            )
        with self.assertRaisesRegex(ValueError, "Specify the additional"):
            self.save(
                decision="Request additional verification",
                rationale="Need more evidence.",
                requested_information="",
            )
        self.assertEqual(decision_service.list_application_decisions("DEMO-FARM-1"), [])

    def test_conditional_approval_requires_conditions(self):
        with self.assertRaisesRegex(ValueError, "conditions"):
            self.save(
                decision="Conditional approval",
                conditions="  ",
            )

    def test_rejects_invalid_amounts_and_identity(self):
        with self.assertRaisesRegex(ValueError, "Manager identity"):
            self.save(manager_identity=" ")
        with self.assertRaisesRegex(ValueError, "greater than zero"):
            self.save(proposed_amount=0)
        with self.assertRaisesRegex(ValueError, "cannot exceed"):
            self.save(proposed_amount=100001)
        with self.assertRaisesRegex(ValueError, "must have a proposed amount of zero"):
            self.save(decision="Reject", proposed_amount=1)
        with self.assertRaisesRegex(ValueError, "finite"):
            self.save(proposed_amount=math.nan)
        self.assertEqual(decision_service.list_application_decisions("DEMO-FARM-1"), [])


if __name__ == "__main__":
    unittest.main()
