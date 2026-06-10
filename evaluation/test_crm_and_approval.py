import os
import sys
import json
import csv
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Ensure search package can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import app, jobs_db
from utils.crm_exporter import export_to_crm, split_name

class TestCRMAndApproval(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.test_job_id = "test-job-123"
        self.test_result_path = f"outputs/job_{self.test_job_id}.json"
        
        # Mock data representing pipeline results
        self.mock_report = {
            "query": "Find SaaS companies",
            "prospects": [
                {
                    "company": "Acme Corp",
                    "website": "acme.com",
                    "qualification_score": 85,
                    "qualification_tier": "Hot",
                    "blocked_reason": None,
                    "buyer_fit": {"buyer_fit": "High", "competitor_flag": False},
                    "opportunity": {"urgency": "High"},
                    "contact": {
                        "contact_name": "John Doe",
                        "title": "CTO",
                        "linkedin_url": "https://linkedin.com/in/johndoe",
                        "apollo_id": "ap_111",
                        "verification_level": "apollo_verified"
                    },
                    "approved": None
                },
                {
                    "company": "Beta Inc",
                    "website": "beta.com",
                    "qualification_score": 40,
                    "qualification_tier": "Cold",
                    "blocked_reason": "COLD_PROSPECT",
                    "buyer_fit": {"buyer_fit": "Low", "competitor_flag": False},
                    "opportunity": None,
                    "contact": {
                        "contact_name": None,
                        "title": None,
                        "linkedin_url": None,
                        "apollo_id": None,
                        "verification_level": "not_found"
                    },
                    "approved": None
                }
            ]
        }
        
        # Ensure directories exist
        os.makedirs("outputs", exist_ok=True)
        os.makedirs("reports", exist_ok=True)
        
        # Write mock result file
        with open(self.test_result_path, "w") as f:
            json.dump(self.mock_report, f, indent=4)
            
        # Register job in db
        jobs_db[self.test_job_id] = {
            "job_id": self.test_job_id,
            "status": "completed",
            "results_path": self.test_result_path,
            "query": "Find SaaS companies"
        }

    def tearDown(self):
        # Cleanup mock files
        for fpath in [
            self.test_result_path,
            f"reports/job_{self.test_job_id}_contacts_found.csv",
            f"reports/job_{self.test_job_id}_approved_leads.csv",
            f"reports/job_{self.test_job_id}_hubspot_import.csv",
            f"reports/job_{self.test_job_id}_salesforce_import.csv"
        ]:
            if os.path.exists(fpath):
                os.remove(fpath)

    def test_split_name(self):
        """Verify utility splits full name to first and last name."""
        self.assertEqual(split_name("John Doe"), ("John", "Doe"))
        self.assertEqual(split_name("Alice"), ("Alice", ""))
        self.assertEqual(split_name(""), ("", ""))
        self.assertEqual(split_name(None), ("", ""))
        print("[Test] split_name utility: PASS")

    def test_crm_exporter(self):
        """Verify CSV files are created with correct columns and mappings."""
        # Setup one approved row
        prospects = list(self.mock_report["prospects"])
        prospects[0]["approved"] = True
        
        export_to_crm(prospects, self.test_job_id)
        
        # Check that job-specific files exist
        self.assertTrue(os.path.exists(f"reports/job_{self.test_job_id}_contacts_found.csv"))
        self.assertTrue(os.path.exists(f"reports/job_{self.test_job_id}_approved_leads.csv"))
        self.assertTrue(os.path.exists(f"reports/job_{self.test_job_id}_hubspot_import.csv"))
        self.assertTrue(os.path.exists(f"reports/job_{self.test_job_id}_salesforce_import.csv"))

        # Verify HubSpot headers and mapped data
        with open(f"reports/job_{self.test_job_id}_hubspot_import.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)
            row = next(reader)
            self.assertEqual(headers, ["Company Name", "First Name", "Last Name", "Job Title", "LinkedIn", "External ID", "Lead Score", "Lead Status"])
            self.assertEqual(row, ["Acme Corp", "John", "Doe", "CTO", "https://linkedin.com/in/johndoe", "ap_111", "85", "Hot"])

        # Verify Salesforce headers and mapped data
        with open(f"reports/job_{self.test_job_id}_salesforce_import.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)
            row = next(reader)
            self.assertEqual(headers, ["Account Name", "Contact Name", "Title", "LinkedIn", "External ID", "Lead Score", "Lead Status"])
            self.assertEqual(row, ["Acme Corp", "John Doe", "CTO", "https://linkedin.com/in/johndoe", "ap_111", "85", "Hot"])

        print("[Test] CRM Exporter Mappings: PASS")

    def test_get_review_contacts(self):
        """Verify API GET review endpoint returns contacts correctly."""
        response = self.client.get(f"/api/v1/jobs/{self.test_job_id}/review")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["job_id"], self.test_job_id)
        self.assertEqual(len(data["contacts"]), 2)
        
        # Verify first contact
        c1 = data["contacts"][0]
        self.assertEqual(c1["company"], "Acme Corp")
        self.assertEqual(c1["contact_name"], "John Doe")
        self.assertEqual(c1["title"], "CTO")
        self.assertEqual(c1["approved"], None)
        print("[Test] GET Review Contacts Endpoint: PASS")

    def test_submit_review_decisions(self):
        """Verify API POST review submissions updates file and triggers CRM Export."""
        submission_payload = {
            "decisions": [
                {
                    "company": "Acme Corp",
                    "approved": True,
                    "contact_name": "Johnathan Doe", # Edit name
                    "title": "Chief Technology Officer" # Edit title
                },
                {
                    "company": "Beta Inc",
                    "approved": False
                }
            ]
        }
        
        response = self.client.post(f"/api/v1/jobs/{self.test_job_id}/review", json=submission_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        
        # Verify result file is updated on disk
        with open(self.test_result_path, "r") as f:
            updated_report = json.load(f)
            
        p1 = updated_report["prospects"][0]
        self.assertEqual(p1["approved"], True)
        self.assertEqual(p1["contact"]["contact_name"], "Johnathan Doe")
        self.assertEqual(p1["contact"]["title"], "Chief Technology Officer")
        
        p2 = updated_report["prospects"][1]
        self.assertEqual(p2["approved"], False)
        print("[Test] POST Submit Review Decisions Endpoint: PASS")

    def test_get_job_dashboard(self):
        """Verify API GET dashboard endpoint calculates metrics correctly."""
        # Make one contact apollo_verified, another not_found
        response = self.client.get(f"/api/v1/jobs/{self.test_job_id}/dashboard")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data["job_id"], self.test_job_id)
        metrics = data["metrics"]
        self.assertEqual(metrics["prospects_found"], 2)
        self.assertEqual(metrics["qualified"], 1) # Hot is qualified, Cold is not
        self.assertEqual(metrics["high_fit"], 1) # High is high fit, Low is not
        self.assertEqual(metrics["apollo_verified_contacts"], 1) # John Doe is apollo_verified
        self.assertEqual(metrics["manual_review_required"], 1) # Beta Inc needs manual review
        print("[Test] GET Job Dashboard Endpoint: PASS")

if __name__ == "__main__":
    unittest.main()
