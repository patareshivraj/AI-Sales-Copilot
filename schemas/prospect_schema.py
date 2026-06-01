from pydantic import BaseModel, Field
from typing import List

class Prospect(BaseModel):
    company: str = Field(description="Name of the company")
    website: str = Field(description="Website URL of the company")
    source: str = Field(description="Where this was found (e.g., 'DuckDuckGo')")
    matched_keywords: List[str] = Field(description="Keywords from the search snippet that matched the ICP", default_factory=list)
    confidence: int = Field(description="Confidence score (0-100) that this company matches the ICP")

class ProspectList(BaseModel):
    prospects: List[Prospect]
