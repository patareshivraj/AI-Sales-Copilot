from schemas.research_schema import CompanyResearch
from schemas.outreach_schema import Outreach
from schemas.sequencer_schema import FollowUpSequence
from core.llm import LLMService

SEQUENCER_PROMPT = """You are an elite B2B Sales Campaign Manager.

Your task is to design a 5-step follow-up email sequence for a prospect.

Company: {company}
Industry: {industry}
Initial Outreach Email Sent:
{initial_email}

Research Highlights:
Services: {services}
Signals: {signals}

Follow-up Strategy:
Follow-up 1: New Insight (Provide an industry benchmark or insight)
Follow-up 2: Pain Point (Focus on a specific problem they likely face based on research)
Follow-up 3: Case Study (Mention a similar organization's success)
Follow-up 4: Value Recap (Summarize the core value proposition quickly)
Follow-up 5: Breakup Email (Professional close assuming timing isn't right)

Rules:
1. DO NOT use generic phrases like "Just checking in" or "Circling back".
2. Keep emails concise (under 4 sentences).
3. Maintain the same professional tone as the initial outreach email.
4. Provide a clear, distinct call to action (CTA) in each email.

Generate the 5 follow-up sequence emails.
"""

class SequencerAgent:
    def __init__(self):
        self.llm = LLMService(temperature=0.7)

    def generate_sequence(self, research: CompanyResearch, outreach: Outreach) -> FollowUpSequence:
        signal_strs = [f"{s.type} ({s.confidence}%)" for s in research.signals]
        
        prompt = SEQUENCER_PROMPT.format(
            company=research.company,
            industry=research.industry,
            initial_email=outreach.cold_email,
            services=", ".join(research.services) if research.services else "None",
            signals=", ".join(signal_strs) if signal_strs else "None"
        )
        
        try:
            return self.llm.generate_structured(prompt, FollowUpSequence)
        except Exception as e:
            return FollowUpSequence(
                follow_up_1_insight="Error",
                follow_up_2_pain_point="Error",
                follow_up_3_case_study="Error",
                follow_up_4_value_recap="Error",
                follow_up_5_breakup=f"LLM Error: {e}"
            )
