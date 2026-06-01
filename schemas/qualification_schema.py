from pydantic import BaseModel, Field

class ScoreBreakdown(BaseModel):
    industry_match: int = Field(description="Score awarded for industry match")
    ai_readiness: int = Field(description="Score awarded for AI readiness")
    signals: int = Field(description="Score awarded for growth signals")

class Qualification(BaseModel):
    score: int = Field(description="Deterministic total score (0-100)")
    tier: str = Field(description="'Hot', 'Warm', or 'Cold'")
    score_breakdown: ScoreBreakdown = Field(description="Breakdown of how the score was calculated")
    reasoning: str = Field(description="LLM explanation of the score and tier")
