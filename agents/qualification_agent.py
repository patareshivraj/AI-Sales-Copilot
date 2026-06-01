from schemas.icp_schema import ICPProfile
from schemas.research_schema import CompanyResearch
from schemas.qualification_schema import Qualification, ScoreBreakdown
from core.llm import LLMService

QUALIFICATION_PROMPT = """You are an expert Sales Qualification Agent.

I have calculated a deterministic lead score for a prospect based on their Ideal Customer Profile (ICP) match and their public research data.
Your job is to provide a clear, professional explanation (reasoning) for WHY this company received this score.

Prospect Information:
Company: {company}
Industry: {industry}
Services: {services}
AI Readiness: {ai_readiness}
Signals: {signals}

Calculated Metrics:
Total Score: {score} / 100
Tier: {tier}
Industry Matched ICP: {industry_match}

Rules:
1. Explain the score objectively, pointing to their AI readiness, industry match, and growth signals.
2. Return the structured qualification object. You MUST copy the deterministic score, tier, and metrics exactly as provided. Your only unique contribution is the 'reasoning' field.

Provide the qualification profile.
"""

class QualificationAgent:
    def __init__(self):
        self.llm = LLMService(temperature=0.3)

    def qualify(self, icp: ICPProfile, research: CompanyResearch) -> Qualification:
        score = 0
        
        # 1. Industry Match (0-30)
        industry_match = False
        if research.industry and any(research.industry.lower() in ind.lower() or ind.lower() in research.industry.lower() for ind in icp.industries):
            industry_match = True
            score += 30
            
        # 2. AI Readiness (0-40)
        ai_readiness_score = 0
        if research.ai_readiness:
            if research.ai_readiness.lower() == "high":
                ai_readiness_score = 40
            elif research.ai_readiness.lower() == "medium":
                ai_readiness_score = 20
            elif research.ai_readiness.lower() == "low":
                ai_readiness_score = 5
        score += ai_readiness_score
        
        # 3. Signals (0-30)
        signal_score = 0
        for signal in research.signals:
            if signal.confidence > 50:
                signal_score += 10
        if signal_score > 30:
            signal_score = 30
        score += signal_score
        
        # Determine Tier
        if score >= 70:
            tier = "Hot"
        elif score >= 40:
            tier = "Warm"
        else:
            tier = "Cold"
            
        # Format signals for prompt
        signal_strings = [f"{s.type} ({s.confidence}%)" for s in research.signals]
        
        prompt = QUALIFICATION_PROMPT.format(
            company=research.company,
            industry=research.industry,
            services=", ".join(research.services),
            ai_readiness=research.ai_readiness,
            signals=", ".join(signal_strings) if signal_strings else "None",
            score=score,
            tier=tier,
            industry_match="Yes" if industry_match else "No"
        )
        
        try:
            response = self.llm.generate_structured(prompt, Qualification)
            if isinstance(response, str):
                raise Exception(response)
            
            # Post-process: Enforce deterministic scores regardless of what LLM outputs
            response.score = score
            response.tier = tier
            response.score_breakdown = ScoreBreakdown(
                industry_match=30 if industry_match else 0,
                ai_readiness=ai_readiness_score,
                signals=signal_score
            )
            
            return response
        except Exception as e:
            return Qualification(
                score=score,
                tier=tier,
                score_breakdown=ScoreBreakdown(
                    industry_match=30 if industry_match else 0,
                    ai_readiness=ai_readiness_score,
                    signals=signal_score
                ),
                reasoning=f"LLM Error generating reasoning: {e}"
            )
