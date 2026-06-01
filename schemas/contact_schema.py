from pydantic import BaseModel, Field
from typing import Optional

class Contact(BaseModel):
    company: str = Field(description="Company name")
    contact_name: Optional[str] = Field(description="Name of the decision maker", default=None)
    title: Optional[str] = Field(description="Job title of the contact", default=None)
    linkedin_url: Optional[str] = Field(description="Public LinkedIn URL of the contact", default=None)
    email: Optional[str] = Field(description="Publicly found email address", default=None)
    verification_level: str = Field(description="'verified', 'inferred', or 'not_found'", default="not_found")
    source_url: Optional[str] = Field(description="URL where the contact was found", default=None)
    source_type: str = Field(description="E.g., 'linkedin_search', 'company_website', or 'none'", default="none")
    contact_confidence: int = Field(description="Confidence (0-100) that this is the correct decision maker", default=0)
