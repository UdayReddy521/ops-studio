"""API release checks with real SQLite persistence and a deterministic clock."""
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient

from app import create_app


NOW = datetime(2026, 11, 23, 9, 0, tzinfo=timezone.utc)
OVERDUE = {"id": "L101", "owner": "Priya", "due_at": "2026-11-23T14:00:00+05:30"}
FUTURE = {"id": "L102", "owner": "Ravi", "due_at": "2026-11-23T15:00:00+05:30"}


class LeadFollowupReleaseChecks(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.database = Path(directory.name) / "followup.sqlite3"
        self.client = self.open_client()

    def open_client(self):
        client = TestClient(create_app(self.database, clock=lambda: NOW))
        self.addCleanup(client.close)
        return client

    def submit(self, enquiry):
        response = self.client.post("/enquiries", json=enquiry)
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def reminders_sent(self, client):
        response = client.post("/reminders/run")
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()["delivered_to_test_inbox"]

    def test_new_enquiry_is_recorded(self):
        recorded = self.submit(OVERDUE)
        reopened = self.open_client()
        response = reopened.get("/enquiries/L101")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), recorded)
        self.assertEqual(recorded["due_at"], "2026-11-23T08:30:00.000000+00:00")
        self.assertEqual(reopened.post("/enquiries", json=OVERDUE).status_code, 409)

    def test_only_overdue_enquiry_gets_a_reminder(self):
        self.submit(OVERDUE)
        self.submit(FUTURE)
        self.assertEqual(self.reminders_sent(self.client), 1)
        response = self.client.get("/reminders")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{
            "enquiry_id": "L101", "owner": "Priya",
            "delivered_at": "2026-11-23T09:00:00.000000+00:00",
        }])

    def test_retries_and_a_restart_do_not_duplicate_reminders(self):
        self.submit(OVERDUE)
        second_worker = self.open_client()
        with ThreadPoolExecutor(max_workers=2) as workers:
            counts = list(workers.map(self.reminders_sent, [self.client, second_worker]))
        self.assertEqual(sorted(counts), [0, 1])
        restarted = self.open_client()
        self.assertEqual(self.reminders_sent(restarted), 0)
        self.assertEqual(len(restarted.get("/reminders").json()), 1)


if __name__ == "__main__":
    unittest.main()
