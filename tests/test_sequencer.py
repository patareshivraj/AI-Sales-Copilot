import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.sequencer_agent import SequencerAgent
from schemas.research_schema import CompanyResearch, Signal
from schemas.outreach_schema import Outreach

def run_tests():
    agent = SequencerAgent()
    
    research = CompanyResearch(
        company="GlobalTech Logistics",
        website="globaltech.example.com",
        industry="Logistics & Supply Chain",
        summary="A global logistics and supply chain provider looking to modernize.",
        services=["Freight Forwarding", "Warehousing", "Supply Chain Management"],
        pain_points=["High operational costs", "Inefficient routing", "Data silos"],
        signals=[Signal(type="Hiring Data Engineers", confidence=90)],
        ai_readiness="Medium",
        research_confidence=85,
        status="Success"
    )
    
    outreach = Outreach(
        subject="Accelerating GlobalTech's Routing Efficiency with AI",
        cold_email="Hi John,\n\nI noticed GlobalTech is actively expanding its Data Engineering team to tackle routing inefficiencies. We recently helped a similar logistics provider reduce freight costs by 15% using predictive AI models. Would you be open to a brief chat about how we can support your modernization efforts?\n\nBest,\nSales Rep",
        linkedin_message="Hi John, saw you're hiring Data Engineers to optimize routing at GlobalTech. We specialize in predictive AI for logistics. Let's connect!",
        personalization_reason="Used the hiring signal and the specific pain point regarding inefficient routing."
    )
    
    print("=======================================")
    print("FOLLOW-UP SEQUENCER - VALIDATION TESTS")
    print("=======================================\n")
    
    print("Generating 5-step sequence for GlobalTech Logistics...\n")
    result = agent.generate_sequence(research, outreach)
    
    print(result.model_dump_json(indent=2))

if __name__ == "__main__":
    run_tests()
