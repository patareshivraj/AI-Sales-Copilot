from pydantic import BaseModel, Field

class Outreach(BaseModel):
    subject: str = Field(description="Email subject line")
    cold_email: str = Field(description="Body of the cold email")
    linkedin_message: str = Field(description="Short LinkedIn connection message (under 300 chars)")
    personalization_reason: str = Field(description="Explanation of how the email uses research data to personalize")
