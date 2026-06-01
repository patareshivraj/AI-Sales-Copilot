from schemas.research_schema import CompanyResearch
from schemas.qualification_schema import Qualification
from schemas.outreach_schema import Outreach
from core.llm import LLMService

OUTREACH_PROMPT = """You are an elite B2B Sales Copywriter.

Write a highly personalized outreach email and LinkedIn message to this company.

Company: {company}
Industry: {industry}
Their Pain Points: {pain_points}
Their Growth Signals: {signals}
Qualification Reason: {qualification_reason}

Rules:
1. NEVER start with a generic "We help businesses with AI."
2. Reference specific signals or research points found above.
3. Ground the outreach in evidence. If they are hiring, mention their team expansion.
4. Keep the email concise, punchy, and value-focused.
5. The LinkedIn message must be under 300 characters.

Generate the outreach.
"""

class OutreachAgent:
    def __init__(self):
        self.llm = LLMService(temperature=0.7)

    def draft_outreach(self, research: CompanyResearch, qualification: Qualification) -> Outreach:
        signal_strs = [f"{s.type} ({s.confidence}%)" for s in research.signals]
        
        prompt = OUTREACH_PROMPT.format(
            company=research.company,
            industry=research.industry,
            pain_points=", ".join(research.pain_points) if research.pain_points else "None specified",
            signals=", ".join(signal_strs) if signal_strs else "None specified",
            qualification_reason=qualification.reasoning
        )
        
        try:
            response = self.llm.generate_structured(prompt, Outreach)
            if isinstance(response, Outreach):
                return response
        except Exception as e:
            return Outreach(
                subject="Error",
                cold_email="Error generating outreach.",
                linkedin_message="Error",
                personalization_reason=str(e)
            )
            
        return Outreach(
            subject="Error",
            cold_email="Failed to generate outreach.",
            linkedin_message="Error",
            personalization_reason="Parsing failed."
        )
