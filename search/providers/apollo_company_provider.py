import os
import requests
from datetime import datetime
from search.providers.base_provider import SearchProvider

class ApolloCompanyProvider(SearchProvider):
    """
    Apollo Company Search Provider
    ==============================
    Implements SearchProvider interface.
    Uses Apollo's /organizations/search endpoint to discover companies.
    """

    @property
    def name(self) -> str:
        return "apollo_company"

    def search(self, query: str, limit: int = 10) -> list[dict]:
        """
        Search using Apollo Organizations Search API (legacy text search).
        
        Args:
            query: The search term (mapped to q_organization_name).
            limit: Maximum number of results to return.
            
        Returns:
            List of dicts with keys: company, website, industry, employee_count, location, source.
            Returns empty list [] on any failure.
        """
        payload = {
            "q_organization_name": query
        }
        return self.search_structured(payload, limit)

    def search_structured(self, payload: dict, limit: int = 10) -> list[dict]:
        """
        Search using structured filters (e.g. from apollo_icp_adapter).
        
        Args:
            payload: Apollo API request payload body dictionary containing filters.
            limit: Maximum number of results to return.
            
        Returns:
            List of dicts with keys: company, website, industry, employee_count, location, source.
            Returns empty list [] on any failure.
        """
        api_key = os.getenv("APOLLO_API_KEY", "").strip()
        if not api_key:
            print("[ApolloCompanyProvider] ERROR: APOLLO_API_KEY is missing or empty in environment.")
            return []

        endpoint = "https://api.apollo.io/api/v1/organizations/search"
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }
        
        # Ensure per_page is set correctly
        payload_copy = dict(payload)
        payload_copy["per_page"] = min(limit, 100)

        try:
            # Execute request with 10s timeout
            response = requests.post(endpoint, json=payload_copy, headers=headers, timeout=10)
            
            # Log Rate Limits
            self._log_rate_limits(response.headers)

            if response.status_code == 200:
                data = response.json()
                organizations = data.get("organizations", [])
                
                results = []
                for org in organizations:
                    company_name = org.get("name")
                    if not company_name:
                        continue
                        
                    website = org.get("website_url") or org.get("primary_domain") or ""
                    industry = org.get("industry") or ""
                    employee_count = str(org.get("estimated_num_employees") or "")
                    
                    location_parts = [org.get(k) for k in ["city", "state", "country"] if org.get(k)]
                    location = ", ".join(location_parts) if location_parts else ""

                    results.append({
                        "company": company_name,
                        "website": website,
                        "industry": industry,
                        "employee_count": employee_count,
                        "location": location,
                        "source": "Apollo"
                    })
                    
                    if len(results) >= limit:
                        break
                        
                return results

            elif response.status_code == 401:
                print("[ApolloCompanyProvider] ERROR 401: Unauthorized. Check API key.")
            elif response.status_code == 403:
                print("[ApolloCompanyProvider] ERROR 403: Forbidden. Plan or permission issue.")
            elif response.status_code == 429:
                print("[ApolloCompanyProvider] ERROR 429: Rate limit exceeded.")
            else:
                print(f"[ApolloCompanyProvider] ERROR {response.status_code}: {response.text}")

        except requests.exceptions.Timeout:
            print("[ApolloCompanyProvider] ERROR: Request timed out.")
        except requests.exceptions.ConnectionError as e:
            print(f"[ApolloCompanyProvider] ERROR: Connection error. {e}")
        except Exception as e:
            print(f"[ApolloCompanyProvider] ERROR: Unexpected failure. {e}")

        return []

    def _log_rate_limits(self, headers: dict):
        """Helper to parse and log Apollo rate limit headers."""
        daily = headers.get("x-24-hour-requests-left", "N/A")
        hourly = headers.get("x-hourly-requests-left", "N/A")
        minute = headers.get("x-minute-requests-left", "N/A")

        os.makedirs("logs", exist_ok=True)
        log_path = "logs/apollo.log"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [Company Search] Daily Remaining: {daily} | Hourly Remaining: {hourly} | Minute Remaining: {minute}\n"
        
        try:
            with open(log_path, "a") as f:
                f.write(log_line)
        except Exception as e:
            print(f"[ApolloCompanyProvider] Failed to write rate limit log: {e}")
