from pydantic import BaseModel, Field
from typing import Optional

class Contact(BaseModel):
    company: str = Field(description="Company name")
    contact_name: Optional[str] = Field(description="Name of the decision maker", default=None)
    title: Optional[str] = Field(description="Job title of the contact", default=None)
    linkedin_url: Optional[str] = Field(description="Public LinkedIn URL of the contact", default=None)
    email: Optional[str] = Field(description="Publicly found email address", default=None)
    verification_level: str = Field(description="'verified', 'inferred', or 'not_found'", default="not_found")
