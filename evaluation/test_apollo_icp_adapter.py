import os
import sys
import unittest
from dotenv import load_dotenv

# Ensure search package can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from search.apollo_icp_adapter import (
    translate_icp_to_apollo_payload, 
    parse_company_size, 
    map_headcount_to_apollo_ranges
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

    def test_parse_company_size(self):
        """Validate helper function parse_company_size."""
        self.assertEqual(parse_company_size("200-5000 employees"), (200, 5000))
        self.assertEqual(parse_company_size("50+"), (50, None))
        self.assertEqual(parse_company_size("10-50"), (10, 50))
        self.assertEqual(parse_company_size(""), (None, None))
        safe_print("[Test] parse_company_size: PASS")

    def test_map_headcount_to_apollo_ranges(self):
        """Validate helper function map_headcount_to_apollo_ranges."""
        self.assertEqual(map_headcount_to_apollo_ranges(200, 5000), ["51,200", "201,500", "501,1000", "1001,5000"])
        self.assertEqual(map_headcount_to_apollo_ranges(50, None), ["11,50", "51,200", "201,500", "501,1000", "1001,5000", "5001,10000", "10001,"])
        self.assertEqual(map_headcount_to_apollo_ranges(None, None), [])
        safe_print("[Test] map_headcount_to_apollo_ranges: PASS")

    def test_translate_icp_dict(self):
        """Validate translation of raw ICP dictionary to Apollo payload."""
        icp_dict = {
            "industries": ["Manufacturing"],
            "company_size": "200-5000",
            "regions": ["India", "Global"],
            "keywords": ["Automotive零件"]
        }
        payload = translate_icp_to_apollo_payload(icp_dict)
        
        self.assertEqual(payload.get("organization_industries"), ["Manufacturing"])
        self.assertEqual(payload.get("organization_locations"), ["India"]) # 'Global' filtered out
        self.assertEqual(payload.get("organization_num_employees_ranges"), ["51,200", "201,500", "501,1000", "1001,5000"])
        self.assertEqual(payload.get("q_organization_keyword"), "Automotive零件")
        
        safe_print("[Test] translate_icp_dict: PASS")

    def test_translate_icp_pydantic(self):
        """Validate translation of Pydantic ICPProfile to Apollo payload."""
        icp_profile = ICPProfile(
            industries=["Hospital & Health Care"],
            company_size="10-50 employees",
            regions=["United States"],
            keywords=["Telehealth"]
        )
        payload = translate_icp_to_apollo_payload(icp_profile)
        
        self.assertEqual(payload.get("organization_industries"), ["Hospital & Health Care"])
        self.assertEqual(payload.get("organization_locations"), ["United States"])
        self.assertEqual(payload.get("organization_num_employees_ranges"), ["1,10", "11,50"])
        self.assertEqual(payload.get("q_organization_keyword"), "Telehealth")
        
        safe_print("[Test] translate_icp_pydantic: PASS")

    def test_live_structured_query(self):
        """Run live structured query using adapter payload against Apollo API."""
        api_key = os.getenv("APOLLO_API_KEY")
        if not api_key:
            self.skipTest("APOLLO_API_KEY is not set in environment; skipping live test.")

        # Let's create an ICP targeted for India based Hospital & Health Care in 200-5000 range
        icp_dict = {
            "industries": ["hospital & health care"],
            "company_size": "200-5000",
            "regions": ["India"],
            "keywords": ["Apollo"]
        }
        
        payload = translate_icp_to_apollo_payload(icp_dict)
        safe_print(f"\n[Test] Translated payload: {payload}")
        
        provider = ApolloCompanyProvider()
        results = provider.search_structured(payload, limit=3)
        
        self.assertIsInstance(results, list)
        safe_print(f"[Test] Live results received: {len(results)}")
        
        for idx, org in enumerate(results):
            safe_print(f"  #{idx+1}: {org}")
            self.assertEqual(org["source"], "Apollo")
            self.assertIn("company", org)
            self.assertIn("website", org)
            self.assertIn("industry", org)
            self.assertIn("employee_count", org)
            self.assertIn("location", org)
            
        safe_print("[Test] Live structured query: PASS")

if __name__ == "__main__":
    unittest.main()
