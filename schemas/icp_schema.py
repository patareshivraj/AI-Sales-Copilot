from pydantic import BaseModel, Field
from typing import List, Optional

class ICPProfile(BaseModel):
    industries: List[str] = Field(
        description="List of target industries most likely to buy the offering. Empty if input is invalid.",
        default_factory=list
    )
    company_size: str = Field(
        description="Ideal company size range (e.g., '200-5000 employees'). Empty if input is invalid.",
        default=""
    )
    decision_makers: List[str] = Field(
        description="Key decision maker job titles (e.g., 'CTO', 'CIO'). Empty if input is invalid.",
        default_factory=list
    )
    regions: List[str] = Field(
        description="Target geographic regions. Empty if input is invalid.",
        default_factory=list
    )
    market_type: str = Field(
        description="The primary target market (e.g., 'India', 'Global', 'Pune', 'North America'). Empty if invalid.",
        default=""
    )
    keywords: List[str] = Field(
        description="Specific search keywords that can be used to find these companies (e.g., 'digital transformation', 'ai consulting').",
        default_factory=list
    )
    reasoning: str = Field(
        description="Brief reasoning for why these targets were selected. Empty if input is invalid.",
        default=""
    )
    error: Optional[str] = Field(
        description="If the input is empty, a simple greeting like 'Hello', or not a valid business offering, populate this field with a descriptive error like 'Insufficient business offering provided.' Otherwise, leave null.",
        default=None
    )
