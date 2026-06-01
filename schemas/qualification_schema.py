from pydantic import BaseModel, Field

class Qualification(BaseModel):
    score: int = Field(description="Deterministic total score (0-100)")
    tier: str = Field(description="'Hot', 'Warm', or 'Cold'")
    industry_match: bool = Field(description="True if industry matches the ICP")
    ai_readiness_score: int = Field(description="Score derived from AI readiness")
    signal_score: int = Field(description="Score derived from positive growth signals")
    reasoning: str = Field(description="LLM explanation of the score and tier")
