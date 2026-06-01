import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.qualification_agent import QualificationAgent
from schemas.icp_schema import ICPProfile
from schemas.research_schema import CompanyResearch, Signal

def run_tests():
    agent = QualificationAgent()
    
    icp = ICPProfile(
        industries=["Information Technology", "Manufacturing"],
        company_size="1000+",
        decision_makers=["CTO"],
        regions=["Global"],
        market_type="Global",
        keywords=[],
        reasoning=""
    )
    
    # Hot Prospect
    research_hot = CompanyResearch(
        company="Persistent Systems",
        website="persistent.com",
        industry="Information Technology",
        summary="IT services and digital transformation",
        services=["Software Engineering", "Cloud", "AI Consulting"],
        pain_points=[],
        signals=[Signal(type="Hiring", confidence=90)],
        ai_readiness="Medium",
        research_confidence=85,
        status="Success"
    )
    
    # Cold Prospect
    research_cold = CompanyResearch(
        company="Bob's Bakery",
        website="bobsbakery.com",
        industry="Food & Beverage",
        summary="Local bakery",
        services=["Bread", "Cakes"],
        pain_points=[],
        signals=[],
        ai_readiness="Low",
        research_confidence=90,
        status="Success"
    )
    
    print("=========================================")
    print("QUALIFICATION AGENT - VALIDATION TESTS")
    print("=========================================\n")
    
    print("--- Testing Hot Prospect ---")
    result_hot = agent.qualify(icp, research_hot)
    print(result_hot.model_dump_json(indent=2))
    
    print("\n--- Testing Cold Prospect ---")
    result_cold = agent.qualify(icp, research_cold)
    print(result_cold.model_dump_json(indent=2))

if __name__ == "__main__":
    run_tests()
