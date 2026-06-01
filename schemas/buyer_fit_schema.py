from pydantic import BaseModel, Field

class BuyerFit(BaseModel):
    buyer_fit: str = Field(description="High, Medium, or Low")
    buyer_type: str = Field(description="E.g., Potential Customer, Competitor, Partner")
    competitor_flag: bool = Field(description="True if they offer the same core services as us")
    partner_flag: bool = Field(description="True if they offer complementary services")
    reasoning: str = Field(description="Why this determination was made")
    outreach_allowed: bool = Field(description="Calculated field: True if outreach is permitted based on fit", default=False)
    disqualification_reason: str = Field(description="If not allowed, the specific reason why (e.g. 'Company provides overlapping AI consulting services')", default="")
