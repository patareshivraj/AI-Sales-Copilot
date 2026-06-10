import os
import sys
import unittest
from dotenv import load_dotenv

# Ensure search package can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from search.apollo_icp_adapter import (
    translate_icp_to_apollo_payload, 
    parse_company_size, 
    map_headcount_to_apollo_ranges,
    INDUSTRY_MAPPING,
    LOCATION_MAPPING
)
from search.providers.apollo_company_provider import ApolloCompanyProvider
from schemas.icp_schema import ICPProfile

load_dotenv()

def safe_print(text: str):
    """Safely print text handling Windows console encoding issues."""
    try:
        print(text)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or 'utf-8'
        print(text.encode(encoding, errors='replace').decode(encoding))

class TestApolloICPAdapter(unittest.TestCase):

    def test_industry_mapping(self):
        """Validate industry mapping converts loose inputs to Apollo industry taxonomy."""
        icp_dict = {
            "industries": ["IT Services", "SaaS", "Hospital", "Unknown Industry"],
            "company_size": "200-5000",
            "regions": ["India"]
        }
        payload = translate_icp_to_apollo_payload(icp_dict)
        industries = payload.get("organization_industries", [])
        
        self.assertIn("information technology & services", industries)
        self.assertIn("computer software", industries)
        self.assertIn("hospital & health care", industries)
        self.assertIn("unknown industry", industries) # Fallback to raw lowercase if not in mapping table
        safe_print("[Test] Industry Mapping: PASS")

    def test_location_mapping(self):
        """Validate location mapping converts geographical terms and acronyms."""
        icp_dict = {
            "industries": ["tech"],
            "company_size": "200-5000",
            "regions": ["US", "in", "bengaluru", "Global"]
        }
        payload = translate_icp_to_apollo_payload(icp_dict)
        locations = payload.get("organization_locations", [])
        
        self.assertIn("United States", locations)
        self.assertIn("India", locations)
        self.assertIn("Bengaluru, Karnataka, India", locations)
        self.assertNotIn("Global", locations) # Global filtered out
        safe_print("[Test] Location Mapping: PASS")

    def test_employee_size_mapping(self):
        """Validate parse_company_size and mapping to Apollo ranges."""
        self.assertEqual(parse_company_size("200-5000 employees"), (200, 5000))
        self.assertEqual(parse_company_size("50+"), (50, None))
        
        self.assertEqual(
            map_headcount_to_apollo_ranges(200, 5000), 
            ["51,200", "201,500", "501,1000", "1001,5000"]
        )
        safe_print("[Test] Employee Size Mapping: PASS")

    def test_translate_icp_pydantic(self):
        """Validate translation of Pydantic ICPProfile."""
        icp_profile = ICPProfile(
            industries=["Hospital & Health Care"],
            company_size="10-50 employees",
            regions=["United States"],
            keywords=["Telehealth"]
        )
        payload = translate_icp_to_apollo_payload(icp_profile)
        
        self.assertEqual(payload.get("organization_industries"), ["hospital & health care"])
        self.assertEqual(payload.get("organization_locations"), ["United States"])
        self.assertEqual(payload.get("organization_num_employees_ranges"), ["1,10", "11,50"])
        self.assertEqual(payload.get("q_organization_keyword"), "Telehealth")
        safe_print("[Test] Pydantic ICP Translation: PASS")

    def test_live_structured_query(self):
        """Run live query with translated payload against Apollo API."""
        api_key = os.getenv("APOLLO_API_KEY")
        if not api_key:
            self.skipTest("APOLLO_API_KEY is not set in environment; skipping live test.")

        icp_dict = {
            "industries": ["healthcare"],
            "company_size": "200-5000",
            "regions": ["in"],
            "keywords": ["Apollo"]
        }
        
        payload = translate_icp_to_apollo_payload(icp_dict)
        safe_print(f"\n[Test] Translated payload: {payload}")
        
        provider = ApolloCompanyProvider()
        results = provider.search_structured(payload, limit=2)
        
        self.assertIsInstance(results, list)
        safe_print(f"[Test] Live results received: {len(results)}")
        
        for idx, org in enumerate(results):
            safe_print(f"  #{idx+1}: {org}")
            self.assertEqual(org["source"], "Apollo")
            
        safe_print("[Test] Live Structured Query: PASS")

if __name__ == "__main__":
    unittest.main()
