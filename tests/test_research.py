import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.company_researcher import CompanyResearcherAgent

def run_tests():
    agent = CompanyResearcherAgent()
    
    test_cases = [
        {"company": "Persistent Systems", "website": "https://en.wikipedia.org/wiki/Persistent_Systems"},
        {"company": "Invalid Company XYZ", "website": "thisisnotarealwebsite1234567.com"}
    ]
    
    print("===========================================")
    print("COMPANY RESEARCHER AGENT - VALIDATION TESTS")
    print("===========================================\n")
    
    for tc in test_cases:
        print(f"--- Testing: {tc['company']} ({tc['website']}) ---")
        result = agent.research_company(tc['company'], tc['website'])
        print(result.model_dump_json(indent=2))
        print("\n" + "-"*40 + "\n")

if __name__ == "__main__":
    run_tests()
