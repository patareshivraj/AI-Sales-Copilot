import os
import sys
import unittest
from unittest.mock import patch
from dotenv import load_dotenv

# Ensure search package can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from search.providers.apollo_provider import ApolloProvider

load_dotenv()

class TestApolloProvider(unittest.TestCase):

    def setUp(self):
        self.provider = ApolloProvider()

    def test_provider_initialization(self):
        """Validate that the provider initializes and has the correct name."""
        self.assertEqual(self.provider.name, "apollo")
        print("[Test] Initialization: PASS")

    def test_query_execution_and_normalization(self):
        """Validate that a valid query runs and returns correctly normalized results."""
        api_key = os.getenv("APOLLO_API_KEY")
        if not api_key:
            self.skipTest("APOLLO_API_KEY is not set in environment; skipping live test.")

        print(f"[Test] Running live search query for 'Software Agency'...")
        results = self.provider.search("Software Agency", limit=3)
        
        self.assertIsInstance(results, list, "Search must return a list")
        print(f"[Test] Received {len(results)} results")
        
        for idx, item in enumerate(results):
            print(f"  Result #{idx+1}: {item}")
            # Validate keys
            self.assertIn("company", item, "Normalized result missing 'company'")
            self.assertIn("website", item, "Normalized result missing 'website'")
            self.assertIn("source", item, "Normalized result missing 'source'")
            self.assertIn("confidence", item, "Normalized result missing 'confidence'")
            
            # Validate types and specific values
            self.assertEqual(item["source"], "Apollo")
            self.assertEqual(item["confidence"], 95)
            self.assertIsInstance(item["company"], str)
            self.assertIsInstance(item["website"], str)

        print("[Test] Query execution and normalization: PASS")

    def test_missing_api_key_graceful_failure(self):
        """Validate that search returns [] and does not crash when API key is missing."""
        with patch.dict(os.environ, {"APOLLO_API_KEY": ""}):
            results = self.provider.search("Software Agency")
            self.assertEqual(results, [])
        print("[Test] Missing API key graceful failure: PASS")

    def test_error_handling_invalid_key(self):
        """Validate that search returns [] and does not crash when API key is invalid."""
        with patch.dict(os.environ, {"APOLLO_API_KEY": "invalid_api_key_value"}):
            results = self.provider.search("Software Agency")
            self.assertEqual(results, [])
        print("[Test] Invalid API key error handling: PASS")

    def test_rate_limit_logging(self):
        """Validate that log file is created in logs/apollo.log when logging rate limits."""
        # Clean up existing log to verify creation
        log_path = "logs/apollo.log"
        if os.path.exists(log_path):
            try:
                os.remove(log_path)
            except Exception:
                pass
                
        test_headers = {
            "x-24-hour-requests-left": "599",
            "x-hourly-requests-left": "199",
            "x-minute-requests-left": "49"
        }
        self.provider._log_rate_limits(test_headers)
        
        self.assertTrue(os.path.exists(log_path), "Rate limit logging failed to create log file")
        with open(log_path, "r") as f:
            content = f.read()
            self.assertIn("Daily Remaining: 599", content)
            self.assertIn("Hourly Remaining: 199", content)
            self.assertIn("Minute Remaining: 49", content)
            
        print("[Test] Rate limit logging: PASS")

if __name__ == "__main__":
    unittest.main()
