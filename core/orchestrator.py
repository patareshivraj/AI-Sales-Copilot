import json
from agents.icp_builder import ICPBuilderAgent
from agents.prospect_finder import ProspectFinderAgent
from agents.company_researcher import CompanyResearcherAgent
from agents.qualification_agent import QualificationAgent
from agents.buyer_fit_agent import BuyerFitAgent
from agents.outreach_agent import OutreachAgent

class SalesCopilotWorkflow:
    def __init__(self):
        self.icp_builder = ICPBuilderAgent()
        self.prospect_finder = ProspectFinderAgent()
        self.researcher = CompanyResearcherAgent()
        self.qualifier = QualificationAgent()
        self.buyer_fit_agent = BuyerFitAgent()
        self.outreach_agent = OutreachAgent()

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
            print(f"Qualification -> Score: {qualified.score}/100 | Tier: {qualified.tier}")

            print("\n--- Phase 5.5: BUYER FIT EVALUATION ---")
            buyer_fit = self.buyer_fit_agent.evaluate(query, icp, research)
            print(f"Buyer Fit: {buyer_fit.buyer_fit} | Type: {buyer_fit.buyer_type}")
            print(f"Is Competitor: {buyer_fit.competitor_flag}")

            outreach_data = None
            if not buyer_fit.competitor_flag and buyer_fit.buyer_fit != "Low" and qualified.tier != "Cold":
                print("\n--- Phase 7: OUTREACH GENERATION ---")
                outreach = self.outreach_agent.draft_outreach(research, qualified)
                outreach_data = outreach.model_dump()
                print("Outreach drafted successfully.")
            else:
                print("\n--- Skipping Outreach (Low Fit/Competitor/Cold) ---")

            final_report["prospects"].append({
                "company": p.company,
                "website": p.website,
                "qualification_score": qualified.score,
                "qualification_tier": qualified.tier,
                "buyer_fit": buyer_fit.model_dump(),
                "research": research.model_dump(),
                "qualification": qualified.model_dump(),
                "outreach": outreach_data
            })

        print("\n=== STEP 5: FINAL REPORT GENERATED ===")
        return final_report
