from schemas.icp_schema import ICPProfile
from schemas.research_schema import CompanyResearch
from schemas.buyer_fit_schema import BuyerFit
from core.llm import LLMService

BUYER_FIT_PROMPT = """You are an expert Go-To-Market Strategist evaluating a company's fit.

We offer: {our_offering}
Target ICP: {icp_industries}

Company Researched: {company}
Industry: {industry}
Services Offered: {services}
Summary: {summary}

Your Job:
Determine if this company is a Potential Customer, a Competitor, or a Partner.
If they sell the exact same services as us (e.g. they are an IT consultancy selling AI Transformation), they are a Competitor. Competitors have Low buyer fit.

Evaluate the buyer fit now.
"""

class BuyerFitAgent:
    def __init__(self):
        self.llm = LLMService(temperature=0.1)

    def evaluate(self, our_offering: str, icp: ICPProfile, research: CompanyResearch) -> BuyerFit:
        if not research.summary and not research.services:
            return BuyerFit(
                buyer_fit="Low",
                buyer_type="Unknown",
                competitor_flag=False,
                partner_flag=False,
                reasoning="Insufficient research data."
            )
            
        prompt = BUYER_FIT_PROMPT.format(
            our_offering=our_offering,
            icp_industries=", ".join(icp.industries),
            company=research.company,
            industry=research.industry,
            services=", ".join(research.services),
            summary=research.summary
        )
        
        try:
            response = self.llm.generate_structured(prompt, BuyerFit)
            if isinstance(response, BuyerFit):
                # Post-process the block logic
                if response.competitor_flag:
                    response.outreach_allowed = False
                    response.disqualification_reason = "Company provides overlapping services (Competitor)."
                elif response.buyer_fit == "Low":
                    response.outreach_allowed = False
                    response.disqualification_reason = "Low buyer fit determined by ICP match."
                else:
                    response.outreach_allowed = True
                    response.disqualification_reason = ""
                    
                return response
        except Exception as e:
            return BuyerFit(
                buyer_fit="Low",
                buyer_type="Unknown",
                competitor_flag=False,
                partner_flag=False,
                reasoning=f"LLM Error: {e}"
            )
        
        return BuyerFit(
            buyer_fit="Low",
            buyer_type="Unknown",
            competitor_flag=False,
            partner_flag=False,
            reasoning="Failed to parse response."
        )
