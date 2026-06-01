import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.contact_discovery_agent import ContactDiscoveryAgent
from schemas.icp_schema import ICPProfile

def run_tests():
    agent = ContactDiscoveryAgent()
    
    icp = ICPProfile(
        industries=["Information Technology"],
        company_size="1000+",
        decision_makers=["CTO", "Chief Technology Officer"],
        regions=["Global"],
        market_type="Global",
        keywords=[],
        reasoning=""
    )
    
    print("=======================================")
    print("CONTACT DISCOVERY AGENT - VALIDATION")
    print("=======================================\n")
    
    company = "Microsoft"
    print(f"Searching for Decision Makers at {company}...")
    result = agent.find_contact(company, icp)
    
    print("\nResult:")
    print(result.model_dump_json(indent=2))

if __name__ == "__main__":
    run_tests()
