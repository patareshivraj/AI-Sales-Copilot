from pydantic import BaseModel, Field

class BuyerFit(BaseModel):
    buyer_fit: str = Field(description="High, Medium, or Low")
    buyer_type: str = Field(description="E.g., Potential Customer, Competitor, Partner")
    competitor_flag: bool = Field(description="True if they offer the same core services as us")
    partner_flag: bool = Field(description="True if they offer complementary services")
    reasoning: str = Field(description="Why this determination was made")
