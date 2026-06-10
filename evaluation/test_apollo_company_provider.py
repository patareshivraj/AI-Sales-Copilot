import os
import sys
import unittest
from dotenv import load_dotenv

# Ensure search package can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from search.providers.apollo_company_provider import ApolloCompanyProvider

load_dotenv()

def safe_print(text: str):
    """Safely print text handling Windows console encoding issues."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback to replacing unencodable characters for the current stdout encoding
        encoding = sys.stdout.encoding or 'utf-8'
        print(text.encode(encoding, errors='replace').decode(encoding))

class TestApolloCompanyProvider(unittest.TestCase):

    def setUp(self):
        self.provider = ApolloCompanyProvider()

    def test_provider_initialization(self):
        """Validate that the provider initializes and has correct name."""
        self.assertEqual(self.provider.name, "apollo_company")
        safe_print("[Test] Initialization: PASS")

    def test_live_queries(self):
        """Run live queries against Apollo and validate normalization."""
        api_key = os.getenv("APOLLO_API_KEY")
        if not api_key:
            self.skipTest("APOLLO_API_KEY is not set in environment; skipping live test.")

        queries = [
            "AI consulting companies",
            "Software agencies",
            "Manufacturing companies India"
        ]

        for query in queries:
            safe_print(f"\n[Test] Running live search query for: '{query}'...")
            results = self.provider.search(query, limit=3)
            
            self.assertIsInstance(results, list, "Search results must be a list")
            safe_print(f"[Test] Received {len(results)} results:")
            
            for idx, item in enumerate(results):
                safe_print(f"  #{idx+1}: {item}")
                
                # Assertions for output schema contract
                self.assertIn("company", item, "Missing 'company' key")
                self.assertIn("website", item, "Missing 'website' key")
                self.assertIn("industry", item, "Missing 'industry' key")
                self.assertIn("employee_count", item, "Missing 'employee_count' key")
                self.assertIn("location", item, "Missing 'location' key")
                self.assertIn("source", item, "Missing 'source' key")
                
                self.assertEqual(item["source"], "Apollo")
                self.assertIsInstance(item["company"], str)
                self.assertIsInstance(item["website"], str)
                self.assertIsInstance(item["industry"], str)
                self.assertIsInstance(item["employee_count"], str)
                self.assertIsInstance(item["location"], str)

        safe_print("\n[Test] Live queries execution and normalization: PASS")

if __name__ == "__main__":
    unittest.main()
