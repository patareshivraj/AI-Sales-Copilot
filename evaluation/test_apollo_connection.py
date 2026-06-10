import os
import sys
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_apollo_auth():
    # 1. Check if the API key exists
    api_key = os.getenv("APOLLO_API_KEY")
    api_key_present = "PASS" if api_key else "FAIL"

    endpoint = "https://api.apollo.io/api/v1/mixed_people/api_search"
    headers = {
        "Authorization": f"Bearer {api_key}" if api_key else "",
        "Content-Type": "application/json",
        "Cache-Control": "no-cache"
    }
    payload = {
        "q_organization_name": "Apollo",
        "per_page": 1
    }

    status_code = "N/A"
    auth_passed = "FAIL"
    response_body_preview = ""
    response_headers = {}
    apollo_reachable = "FAIL"
    exact_response = "None"

    if api_key:
        try:
            # Test authentication against Apollo with 10 seconds timeout
            response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
            status_code = response.status_code
            apollo_reachable = "PASS"
            response_headers = dict(response.headers)
            
            try:
                resp_json = response.json()
                exact_response = json.dumps(resp_json, indent=2)
                response_body_preview = exact_response[:500]
                if len(exact_response) > 500:
                    response_body_preview += "\n..."
            except Exception:
                exact_response = response.text
                response_body_preview = exact_response[:500]
                if len(exact_response) > 500:
                    response_body_preview += "\n..."

            if response.status_code in [200, 201]:
                auth_passed = "PASS"
            else:
                auth_passed = "FAIL"
                
        except requests.exceptions.Timeout:
            response_body_preview = "Request Timed Out"
        except requests.exceptions.ConnectionError as e:
            response_body_preview = f"Connection Error: {e}"
        except Exception as e:
            response_body_preview = f"Unexpected Error: {e}"
    else:
        response_body_preview = "No API Key loaded. Please check your .env file."

    # Print the exact requested output format
    print("=================================")
    print("APOLLO AUTH TEST")
    print("=================================")
    print(f"API Key Present: {api_key_present}")
    print(f"Endpoint Tested: {endpoint}")
    print(f"Status Code: {status_code}")
    print(f"Authentication: {auth_passed}")
    print("\nResponse Preview:")
    print(response_body_preview)

    print("\n" + "="*40)
    print("DETAILED QUESTIONS SUMMARY")
    print("="*40)
    print(f"1. Is the API key loaded? {'Yes' if api_key else 'No'}")
    print(f"2. Is Apollo reachable? {apollo_reachable}")
    print(f"3. Is authentication successful? {auth_passed}")
    print(f"4. Which endpoint works? {endpoint if auth_passed == 'PASS' else 'None'}")
    print(f"5. What exact response Apollo returns?\n{exact_response}")

    print("\nResponse Headers:")
    for k, v in response_headers.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    test_apollo_auth()
