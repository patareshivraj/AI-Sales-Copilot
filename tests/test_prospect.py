import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.prospect_finder import ProspectFinderAgent
from schemas.icp_schema import ICPProfile

def run_tests():
    agent = ProspectFinderAgent()
    
    # Mock ICP for DataTech Labs
    icp = ICPProfile(
        industries=["Manufacturing"],
        company_size="1000-5000",
        decision_makers=["CTO", "CIO"],
        regions=["India"],
        market_type="India",
        keywords=["digital transformation", "ai consulting"],
        reasoning="Test reasoning"
    )
    
    print("====================================")
    print("PROSPECT FINDER AGENT - TEST")
    print("====================================\n")
    
    print(f"Searching for keywords: {icp.keywords} in {icp.market_type}...")
    results = agent.find_prospects(icp)
    
    print(f"\nFound {len(results.prospects)} prospects:\n")
    print(results.model_dump_json(indent=2))

if __name__ == "__main__":
    run_tests()
