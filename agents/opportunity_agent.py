from schemas.research_schema import CompanyResearch
from schemas.qualification_schema import Qualification
from schemas.opportunity_schema import OpportunityIntelligence
from core.llm import LLMService

OPPORTUNITY_PROMPT = """You are a Sales Strategist analyzing timing signals.

Company: {company}
Industry: {industry}
Services: {services}
Pain Points: {pain_points}
Growth Signals: {signals}
AI Readiness: {ai_readiness}
Qualification Score: {score}/100
Qualification Tier: {tier}

Your Job:
Analyze the research data and determine WHY this company should be contacted RIGHT NOW (not in general).

Rules:
1. Each 'why_now' item must reference a specific signal, pain point, or data point from the research above.
2. DO NOT generate generic reasons like "They might benefit from AI." Every reason must be grounded in evidence.
3. If there are no strong timing signals, set urgency to 'Low' and be honest about it.
4. The recommended_angle should suggest a concrete sales approach based on their specific situation.

Generate the Opportunity Intelligence.
"""

class OpportunityAgent:
    def __init__(self):
        self.llm = LLMService(temperature=0.3)

    def analyze(self, research: CompanyResearch, qualification: Qualification) -> OpportunityIntelligence:
        if research.status != "Success" or not research.summary:
            return OpportunityIntelligence(
                why_now=[],
                urgency="Low",
                recommended_angle="Insufficient research data to determine timing."
            )

        signal_strs = [f"{s.type} ({s.confidence}%)" for s in research.signals]

        prompt = OPPORTUNITY_PROMPT.format(
            company=research.company,
            industry=research.industry or "Unknown",
            services=", ".join(research.services) if research.services else "None",
            pain_points=", ".join(research.pain_points) if research.pain_points else "None",
            signals=", ".join(signal_strs) if signal_strs else "None",
            ai_readiness=research.ai_readiness or "Unknown",
            score=qualification.score,
            tier=qualification.tier
        )

        try:
            return self.llm.generate_structured(prompt, OpportunityIntelligence)
        except Exception as e:
            return OpportunityIntelligence(
                why_now=[],
                urgency="Low",
                recommended_angle=f"LLM Error: {e}"
            )
