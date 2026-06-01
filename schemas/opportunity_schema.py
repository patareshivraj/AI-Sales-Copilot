from pydantic import BaseModel, Field
from typing import List

class OpportunityIntelligence(BaseModel):
    why_now: List[str] = Field(description="List of reasons why this company should be targeted right now", default_factory=list)
    urgency: str = Field(description="'High', 'Medium', or 'Low' based on the strength of the why_now signals", default="Low")
    recommended_angle: str = Field(description="Suggested sales approach based on the signals and pain points", default="")
