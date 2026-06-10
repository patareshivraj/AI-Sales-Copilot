import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv

# Ensure search package can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.contact_discovery_agent import ContactDiscoveryAgent
from schemas.icp_schema import ICPProfile
from schemas.contact_schema import Contact

load_dotenv()

class TestApolloContactDiscovery(unittest.TestCase):

    def setUp(self):
        self.icp = ICPProfile(
            industries=["SaaS"],
            regions=["India"],
            decision_makers=["CTO", "CEO"],
            company_size="200-5000",
            keywords=["Cloud"]
        )
        self.agent = ContactDiscoveryAgent()

    @patch("requests.post")
    def test_1_contact_found(self, mock_post):
        """Test 1: Contact found and successfully verified via Apollo."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "people": [
                {
                    "id": "person_123",
                    "first_name": "Eran",
                    "last_name": "Manny",
                    "title": "CTO",
                    "linkedin_url": "https://linkedin.com/in/eran-manny",
                    "organization": {"name": "Apollo"}
                }
            ]
        }
        mock_post.return_value = mock_response

        # Execute contact discovery
        contact = self.agent.find_contact("Apollo", self.icp)
        
        self.assertIsInstance(contact, Contact)
        self.assertEqual(contact.contact_name, "Eran Manny")
        self.assertEqual(contact.title, "CTO")
        self.assertEqual(contact.verification_level, "apollo_verified")
        self.assertEqual(contact.source_type, "apollo")
        self.assertEqual(contact.apollo_id, "person_123")
        print("[Test 1] Apollo Contact Found: PASS")

    @patch("requests.post")
    @patch("agents.contact_discovery_agent.DDGS")
    def test_2_no_matching_role(self, mock_ddgs, mock_post):
        """Test 2: No matching role found on Apollo and DDG fallback returns not_found."""
        # Setup: Apollo returns empty people, DDG returns no results
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"people": []}
        mock_post.return_value = mock_response
        
        mock_ddg_instance = MagicMock()
        mock_ddg_instance.text.return_value = []
        mock_ddgs.return_value.__enter__.return_value = mock_ddg_instance

        contact = self.agent.find_contact("Unknown Company", self.icp)
        
        self.assertEqual(contact.verification_level, "not_found")
        print("[Test 2] No Matching Role Found -> not_found: PASS")

    @patch("requests.post")
    @patch("agents.contact_discovery_agent.DDGS")
    @patch("core.llm.LLMService.generate_structured")
    def test_3_apollo_failure_fallback_ddg(self, mock_llm_gen, mock_ddgs, mock_post):
        """Test 3: Apollo API exception successfully falls back to DDG without crashing."""
        # Setup: Apollo raises exception, DDG succeeds, LLM succeeds
        mock_post.side_effect = Exception("Connection Timeout")
        
        mock_ddg_instance = MagicMock()
        mock_ddg_instance.text.return_value = [
            {"title": "John Doe - CTO - Acme Corp", "href": "https://linkedin.com/in/johndoe", "body": "CTO at Acme"}
        ]
        mock_ddgs.return_value.__enter__.return_value = mock_ddg_instance

        mock_llm_gen.return_value = Contact(
            company="Acme Corp",
            contact_name="John Doe",
            title="CTO",
            linkedin_url="https://linkedin.com/in/johndoe",
            email=None,
            verification_level="verified",
            source_type="linkedin_search",
            contact_confidence=85
        )

        contact = self.agent.find_contact("Acme Corp", self.icp)
        
        self.assertIsInstance(contact, Contact)
        self.assertEqual(contact.contact_name, "John Doe")
        self.assertEqual(contact.verification_level, "verified")
        self.assertEqual(contact.source_type, "linkedin_search")
        print("[Test 3] Apollo Failure -> DDG Fallback: PASS")

    @patch("requests.post")
    @patch("agents.contact_discovery_agent.DDGS")
    @patch("core.llm.LLMService.generate_structured")
    def test_4_rate_limit_fallback(self, mock_llm_gen, mock_ddgs, mock_post):
        """Test 4: Apollo 429 Rate Limit hit falls back to DDG scraping."""
        # Setup: Apollo returns 429, DDG succeeds, LLM succeeds
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_post.return_value = mock_response
        
        mock_ddg_instance = MagicMock()
        mock_ddg_instance.text.return_value = [
            {"title": "Jane Doe - VP Engineering - Acme Corp", "href": "https://linkedin.com/in/janedoe", "body": "VP at Acme"}
        ]
        mock_ddgs.return_value.__enter__.return_value = mock_ddg_instance

        mock_llm_gen.return_value = Contact(
            company="Acme Corp",
            contact_name="Jane Doe",
            title="VP Engineering",
            linkedin_url="https://linkedin.com/in/janedoe",
            email=None,
            verification_level="verified",
            source_type="linkedin_search",
            contact_confidence=80
        )

        contact = self.agent.find_contact("Acme Corp", self.icp)
        
        self.assertIsInstance(contact, Contact)
        self.assertEqual(contact.contact_name, "Jane Doe")
        self.assertEqual(contact.verification_level, "verified")
        self.assertEqual(contact.source_type, "linkedin_search")
        print("[Test 4] Apollo Rate Limit -> DDG Fallback: PASS")

if __name__ == "__main__":
    unittest.main()
