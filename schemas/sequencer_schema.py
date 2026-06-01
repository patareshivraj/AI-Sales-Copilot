from pydantic import BaseModel, Field

class FollowUpSequence(BaseModel):
    follow_up_1_insight: str = Field(description="Email providing a new insight or benchmark")
    follow_up_2_pain_point: str = Field(description="Email focusing on a specific pain point")
    follow_up_3_case_study: str = Field(description="Email sharing a relevant case study")
    follow_up_4_value_recap: str = Field(description="Email recapping the value proposition")
    follow_up_5_breakup: str = Field(description="Professional breakup email assuming bad timing")
