import os
import time
import requests
from datetime import datetime
from search.providers.base_provider import SearchProvider

class ApolloProvider(SearchProvider):
    """
    Apollo Search Provider
    ======================
    Implements SearchProvider interface.
    Uses Apollo's /mixed_people/api_search endpoint to discover leads.
    """

    @property
    def name(self) -> str:
        return "apollo"

    def search(self, query: str, limit: int = 10) -> list[dict]:
        """
        Search using Apollo API.
        
        Args:
            query: The search term (mapped to q_keywords).
            limit: Maximum number of results to return.
            
        Returns:
            List of dicts with keys: company, website, source, confidence.
            Returns empty list [] on any failure.
        """
        api_key = os.getenv("APOLLO_API_KEY", "").strip()
        if not api_key:
            print("[ApolloProvider] ERROR: APOLLO_API_KEY is missing or empty in environment.")
            return []

        endpoint = "https://api.apollo.io/api/v1/mixed_people/api_search"
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }
        payload = {
            "q_keywords": query,
            "per_page": min(limit * 2, 100)  # Request slightly more for deduplication
        }

        try:
            # Execute search query (10s timeout)
            response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
            
            # Log Rate Limits
            self._log_rate_limits(response.headers)

            if response.status_code == 200:
                data = response.json()
                people = data.get("people", [])
                
                results = []
                seen_companies = set()
                
                for person in people:
                    org = person.get("organization") or {}
                    company_name = org.get("name")
                    if not company_name:
                        continue
                        
                    website = org.get("website") or org.get("primary_domain") or ""
                    
                    # Deduplicate by company name and website domain
                    dup_key = (company_name.lower().strip(), website.lower().strip())
                    if dup_key in seen_companies:
                        continue
                    seen_companies.add(dup_key)
                    
                    results.append({
                        "company": company_name,
                        "website": website,
                        "source": "Apollo",
                        "confidence": 95
                    })
                    
                    if len(results) >= limit:
                        break
                        
                return results

            elif response.status_code == 401:
                print("[ApolloProvider] ERROR 401: Unauthorized. Check API key.")
            elif response.status_code == 403:
                print("[ApolloProvider] ERROR 403: Forbidden. Scopes or plan issue.")
            elif response.status_code == 429:
                print("[ApolloProvider] ERROR 429: Rate limit exceeded.")
            else:
                print(f"[ApolloProvider] ERROR {response.status_code}: {response.text}")

        except requests.exceptions.Timeout:
            print("[ApolloProvider] ERROR: Request timed out.")
        except requests.exceptions.ConnectionError as e:
            print(f"[ApolloProvider] ERROR: Connection error. {e}")
        except Exception as e:
            print(f"[ApolloProvider] ERROR: Unexpected failure. {e}")

        return []

    def _log_rate_limits(self, headers: dict):
        """Helper to parse and log Apollo rate limit headers."""
        daily = headers.get("x-24-hour-requests-left", "N/A")
        hourly = headers.get("x-hourly-requests-left", "N/A")
        minute = headers.get("x-minute-requests-left", "N/A")

        os.makedirs("logs", exist_ok=True)
        log_path = "logs/apollo.log"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] Daily Remaining: {daily} | Hourly Remaining: {hourly} | Minute Remaining: {minute}\n"
        
        try:
            with open(log_path, "a") as f:
                f.write(log_line)
        except Exception as e:
            print(f"[ApolloProvider] Failed to write rate limit log: {e}")
