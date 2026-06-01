import json
from agents.icp_builder import ICPBuilderAgent
from agents.prospect_finder import ProspectFinderAgent
from agents.company_researcher import CompanyResearcherAgent
from agents.qualification_agent import QualificationAgent
from agents.buyer_fit_agent import BuyerFitAgent
from agents.contact_discovery_agent import ContactDiscoveryAgent
from agents.outreach_agent import OutreachAgent
from agents.sequencer_agent import SequencerAgent
from agents.opportunity_agent import OpportunityAgent

class SalesCopilotWorkflow:
    def __init__(self):
        self.icp_builder = ICPBuilderAgent()
        self.prospect_finder = ProspectFinderAgent()
        self.researcher = CompanyResearcherAgent()
        self.qualifier = QualificationAgent()
        self.buyer_fit_agent = BuyerFitAgent()
        self.contact_agent = ContactDiscoveryAgent()
        self.outreach_agent = OutreachAgent()
        self.sequencer_agent = SequencerAgent()
        self.opportunity_agent = OpportunityAgent()

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

            # Opportunity Intelligence runs for all researched prospects
            opportunity_data = None
            if research.status == "Success":
                print("\n--- Phase 12: OPPORTUNITY INTELLIGENCE ---")
                opportunity = self.opportunity_agent.analyze(research, qualified)
                opportunity_data = opportunity.model_dump()
                print(f"Urgency: {opportunity.urgency}")
                print(f"Why Now: {opportunity.why_now}")

            # Blocked Reason tracking
            outreach_data = None
            sequence_data = None
            contact_data = None
            blocked_reason = None
            
            if research.status != "Success":
                blocked_reason = "INSUFFICIENT_RESEARCH"
                print(f"\n--- Blocked: {blocked_reason} ---")
            elif qualified.tier == "Cold":
                blocked_reason = "COLD_PROSPECT"
                print(f"\n--- Blocked: {blocked_reason} ---")
            elif buyer_fit.competitor_flag:
                blocked_reason = "COMPETITOR"
                print(f"\n--- Blocked: {blocked_reason} ---")
            elif not buyer_fit.outreach_allowed:
                blocked_reason = "LOW_BUYER_FIT"
                print(f"\n--- Blocked: {blocked_reason} ---")
            else:
                # Passed all gates, attempt contact discovery
                print("\n--- Phase 6: CONTACT DISCOVERY ---")
                contact = self.contact_agent.find_contact(p.company, icp)
                contact_data = contact.model_dump()
                
                if contact.contact_name:
                    print(f"Found Decision Maker: {contact.contact_name} ({contact.title}) [Confidence: {contact.contact_confidence}%]")
                    
                    print("\n--- Phase 7: OUTREACH GENERATION ---")
                    outreach = self.outreach_agent.draft_outreach(research, qualified)
                    outreach_data = outreach.model_dump()
                    print("Outreach drafted successfully.")
                    
                    print("\n--- Phase 8: FOLLOW-UP SEQUENCER ---")
                    sequence = self.sequencer_agent.generate_sequence(research, outreach)
                    sequence_data = sequence.model_dump()
                    print("5-Step Sequence generated successfully.")
                else:
                    blocked_reason = "NO_VERIFIED_CONTACT"
                    print("No verified decision maker found. Manual Review Required.")

            final_report["prospects"].append({
                "company": p.company,
                "website": p.website,
                "qualification_score": qualified.score,
                "qualification_tier": qualified.tier,
                "blocked_reason": blocked_reason,
                "buyer_fit": buyer_fit.model_dump(),
                "research": research.model_dump(),
                "qualification": qualified.model_dump(),
                "opportunity": opportunity_data,
                "contact": contact_data,
                "outreach": outreach_data,
                "sequence": sequence_data
            })

        print("\n=== STEP 5: FINAL REPORT GENERATED ===")
        return final_report
