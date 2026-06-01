import json
from agents.icp_builder import ICPBuilderAgent
from agents.prospect_finder import ProspectFinderAgent
from agents.company_researcher import CompanyResearcherAgent
from agents.qualification_agent import QualificationAgent

class SalesCopilotWorkflow:
    def __init__(self):
        self.icp_builder = ICPBuilderAgent()
        self.prospect_finder = ProspectFinderAgent()
        self.researcher = CompanyResearcherAgent()
        self.qualifier = QualificationAgent()

    def run(self, query: str):
        print("\n=== STEP 1: ICP GENERATED ===")
        icp = self.icp_builder.build_icp(query)
        if icp.error:
            print(f"Error building ICP: {icp.error}")
            return None
        print(f"Target Industries: {icp.industries}")
        print(f"Market Type: {icp.market_type}")
        print(f"Keywords: {icp.keywords}")

        print("\n=== STEP 2: PROSPECTS FOUND ===")
        # Limiting to 5 for speed during testing, 
        # though the user recommended 10-20 overall
        prospect_list = self.prospect_finder.find_prospects(icp, limit=5)
        print(f"Discovered {len(prospect_list.prospects)} prospects matching the criteria.")

        final_report = {
            "query": query,
            "icp": icp.model_dump(),
            "prospects": []
        }

        for i, p in enumerate(prospect_list.prospects):
            print(f"\n--- STEP 3 & 4: RESEARCH & QUALIFICATION ({i+1}/{len(prospect_list.prospects)}) ---")
            print(f"Processing: {p.company} ({p.website})")
            
            research = self.researcher.research_company(p.company, p.website)
            print(f"Research Status: {research.status}")
            
            qualified = self.qualifier.qualify(icp, research)
            print(f"Result -> Score: {qualified.score}/100 | Tier: {qualified.tier}")
            print(f"Reasoning: {qualified.reasoning}")

            final_report["prospects"].append({
                "company": p.company,
                "website": p.website,
                "qualification_score": qualified.score,
                "qualification_tier": qualified.tier,
                "research": research.model_dump(),
                "qualification": qualified.model_dump()
            })

        print("\n=== STEP 5: FINAL REPORT GENERATED ===")
        return final_report
