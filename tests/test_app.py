import os
import tempfile
import unittest

from app import create_app
from config import Config
from models import db, EmergencyAlert, EmergencyContact, IncidentReport, Notification, User


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    NOTIFICATION_SIMULATION_MODE = True


class WomensSafetyTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        TestConfig.SQLALCHEMY_DATABASE_URI = f"sqlite:///{self.db_path}"
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def _register_and_login(self, email="ananya@example.com", password="Password@123"):
        self.client.post(
            "/register",
            data={
                "full_name": "Ananya Verma",
                "email": email,
                "phone": "+919876543210",
                "password": password,
                "confirm_password": password,
            },
            follow_redirects=True,
        )
        return self.client.post(
            "/login",
            data={"email": email, "password": password},
            follow_redirects=True,
        )

    def test_registration_password_hashing_and_login(self):
        resp = self._register_and_login()
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Welcome, Ananya Verma", resp.data)

        with self.app.app_context():
            user = User.query.filter_by(email="ananya@example.com").first()
            self.assertIsNotNone(user)
            self.assertNotEqual(user.password_hash, "Password@123")
            self.assertTrue(user.check_password("Password@123"))

    def test_contacts_crud_and_sos_simulation(self):
        self._register_and_login()

        # Add emergency contact
        resp = self.client.post(
            "/contacts/add",
            data={
                "name": "Meera Verma",
                "phone": "+919811112222",
                "email": "meera@example.com",
                "relationship": "Parent",
            },
            follow_redirects=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Meera Verma", resp.data)

        with self.app.app_context():
            contact = EmergencyContact.query.filter_by(name="Meera Verma").first()
            self.assertIsNotNone(contact)
            contact_id = contact.id

        # Trigger SOS with simulated notification
        sos_resp = self.client.post(
            "/api/sos",
            json={
                "latitude": 28.6139,
                "longitude": 77.2090,
                "accuracy": 15.0,
                "location_status": "captured",
                "message": "Need help near Connaught Place",
                "contact_ids": [contact_id],
            },
        )
        self.assertEqual(sos_resp.status_code, 201)
        payload = sos_resp.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["notifications"][0]["status"], "simulated")

        with self.app.app_context():
            self.assertEqual(EmergencyAlert.query.count(), 1)
            notif = Notification.query.first()
            self.assertEqual(notif.status, "simulated")
            self.assertEqual(notif.mode, "simulation")

    def test_services_api_and_incident_reporting(self):
        self._register_and_login()

        svc_resp = self.client.get("/api/services?type=police&lat=28.63&lng=77.21")
        self.assertEqual(svc_resp.status_code, 200)
        services = svc_resp.get_json()["services"]
        self.assertGreater(len(services), 0)
        self.assertIsNotNone(services[0]["distance_km"])

        inc_resp = self.client.post(
            "/incidents",
            data={
                "category": "Unsafe / Poorly Lit Area",
                "incident_date": "2026-11-18",
                "location_text": "Metro Gate 3",
                "description": "Streetlights were completely out near the pedestrian exit.",
            },
            follow_redirects=True,
        )
        self.assertEqual(inc_resp.status_code, 200)
        self.assertIn(b"Metro Gate 3", inc_resp.data)

        with self.app.app_context():
            self.assertEqual(IncidentReport.query.count(), 1)

    def test_admin_rbac_enforcement(self):
        # Regular user cannot access admin dashboard
        self._register_and_login()
        forbidden = self.client.get("/admin/dashboard")
        self.assertEqual(forbidden.status_code, 403)

        # Logout and sign in as admin
        self.client.post("/logout")
        admin_resp = self.client.post(
            "/admin/login",
            data={
                "email": Config.ADMIN_EMAIL,
                "password": Config.ADMIN_PASSWORD,
            },
            follow_redirects=True,
        )
        self.assertEqual(admin_resp.status_code, 200)
        self.assertIn(b"Administrator Dashboard", admin_resp.data)

    def test_safety_info_public_page(self):
        resp = self.client.get("/safety-info")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"112", resp.data)
        self.assertIn(b"1091", resp.data)


if __name__ == "__main__":
    unittest.main()
