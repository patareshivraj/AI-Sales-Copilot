import os
import sys
import unittest
from unittest.mock import patch
from dotenv import load_dotenv

# Ensure search package can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from search.search_manager import SearchManager
from schemas.icp_schema import ICPProfile

load_dotenv()

class TestApolloProspectDiscovery(unittest.TestCase):

    def setUp(self):
        self.icp = ICPProfile(
            industries=["Manufacturing"],
            regions=["India"],
            company_size="200-5000",
            keywords=["Automotive"]
        )
        self.search_manager = SearchManager()

    @patch("search.providers.apollo_company_provider.ApolloCompanyProvider.search_structured")
    @patch("search.search_manager.SearchCache.get")
    @patch("search.search_manager.SearchCache.get_stale")
    def test_1_apollo_success(self, mock_cache_get_stale, mock_cache_get, mock_apollo_search):
        """Test 1: Apollo structured search success returns Apollo results."""
        # Setup: Cache miss, Apollo success
        mock_cache_get.return_value = None
        mock_cache_get_stale.return_value = None
        mock_apollo_search.return_value = [
            {
                "company": "Apollo Test Company",
                "website": "apollo-test.com",
                "industry": "manufacturing",
                "employee_count": "500",
                "location": "Mumbai, India",
                "source": "Apollo"
            }
        ]

        results = self.search_manager.search_prospects(self.icp, limit=5)
        
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["company"], "Apollo Test Company")
        self.assertEqual(results[0]["source"], "Apollo")
        print("[Test 1] Apollo Success Case: PASS")

    @patch("search.providers.apollo_company_provider.ApolloCompanyProvider.search_structured")
    @patch("search.providers.duckduckgo_provider.DuckDuckGoProvider.search")
    @patch("search.search_manager.SearchCache.get")
    @patch("search.search_manager.SearchCache.get_stale")
    def test_2_apollo_fail_ddg_success(self, mock_cache_get_stale, mock_cache_get, mock_ddg_search, mock_apollo_search):
        """Test 2: Apollo fail falls back to DuckDuckGo."""
        # Setup: Cache miss, Apollo fails (exception), DDG succeeds
        mock_cache_get.return_value = None
        mock_cache_get_stale.return_value = None
        mock_apollo_search.side_effect = Exception("Apollo API timeout")
        mock_ddg_search.return_value = [
            {
                "title": "DDG Test Company Profile",
                "href": "ddg-test.com",
                "body": "Manufacturer based in Pune, India."
            }
        ]

        results = self.search_manager.search_prospects(self.icp, limit=5)
        
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["href"], "ddg-test.com")
        self.assertNotIn("source", results[0]) # Raw DDG search items do not have source key
        print("[Test 2] Apollo Fail -> DDG Fallback: PASS")

    @patch("search.providers.apollo_company_provider.ApolloCompanyProvider.search_structured")
    @patch("search.providers.duckduckgo_provider.DuckDuckGoProvider.search")
    @patch("search.search_manager.SearchCache.get")
    @patch("search.search_manager.SearchCache.get_stale")
    def test_3_apollo_ddg_fail_cache_success(self, mock_cache_get_stale, mock_cache_get, mock_ddg_search, mock_apollo_search):
        """Test 3: Apollo + DDG fail falls back to cached results."""
        # Setup: Cache miss (fresh), Apollo fails, DDG fails, Cache Stale succeeds
        mock_cache_get.return_value = None
        mock_apollo_search.side_effect = Exception("Apollo Connection Error")
        mock_ddg_search.side_effect = Exception("DDG Rate Limited")
        mock_cache_get_stale.return_value = [
            {
                "title": "Cached Company Profile",
                "href": "cached-test.com",
                "body": "Cached Manufacturer info"
            }
        ]

        results = self.search_manager.search_prospects(self.icp, limit=5)
        
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["href"], "cached-test.com")
        print("[Test 3] Apollo + DDG Fail -> Cache Recovery Fallback: PASS")

    @patch("search.providers.apollo_company_provider.ApolloCompanyProvider.search_structured")
    @patch("search.providers.duckduckgo_provider.DuckDuckGoProvider.search")
    @patch("search.search_manager.SearchCache.get")
    @patch("search.search_manager.SearchCache.get_stale")
    def test_4_total_failure(self, mock_cache_get_stale, mock_cache_get, mock_ddg_search, mock_apollo_search):
        """Test 4: Total failure returns empty list [] without crashing."""
        # Setup: Cache miss, Apollo fails, DDG fails, Cache Stale fails
        mock_cache_get.return_value = None
        mock_apollo_search.side_effect = Exception("Apollo Dead")
        mock_ddg_search.side_effect = Exception("DDG Dead")
        mock_cache_get_stale.return_value = None

        results = self.search_manager.search_prospects(self.icp, limit=5)
        
        self.assertEqual(results, [])
        print("[Test 4] Total Failure -> [] Safety: PASS")

if __name__ == "__main__":
    unittest.main()
