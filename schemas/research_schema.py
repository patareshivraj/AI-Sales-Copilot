from pydantic import BaseModel, Field
from typing import List, Optional

class Signal(BaseModel):
    type: str = Field(description="Type of signal (e.g., 'Hiring', 'IPO', 'Acquisition')")
    confidence: int = Field(description="Confidence (0-100) of this signal being true based on the text")

class CompanyResearch(BaseModel):
    company: str = Field(description="Name of the company")
    website: str = Field(description="Website URL of the company")
    industry: Optional[str] = Field(description="Industry of the company. Null if not found in the scraped content.", default=None)
    summary: Optional[str] = Field(description="Brief summary of what the company does. Null if not found.", default=None)
    services: List[str] = Field(description="List of services or products offered.", default_factory=list)
    pain_points: List[str] = Field(description="List of pain points they seem to solve.", default_factory=list)
    signals: List[Signal] = Field(description="Signals of growth or hiring.", default_factory=list)
    ai_readiness: Optional[str] = Field(description="e.g., 'High', 'Medium', 'Low' based on mentions of AI/Data. Null if unknown.", default=None)
    research_confidence: int = Field(description="Confidence score (0-100) based on amount and quality of info found.", default=0)
    status: Optional[str] = Field(description="E.g., 'Success', or 'Insufficient information' if scraping failed.", default="Success")
