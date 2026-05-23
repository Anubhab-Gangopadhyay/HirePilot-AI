from pydantic import BaseModel, Field


class PriceRequest(BaseModel):
    followers: float = Field(ge=0)
    engagement_rate: float = Field(ge=0)
    niche_score: float = Field(ge=0)
    audience_quality: float = Field(ge=0)
    platform_weight: float = Field(ge=0)


class RoiRequest(BaseModel):
    budget: float = Field(ge=0)
    expected_reach: float = Field(ge=0)
    engagement_rate: float = Field(ge=0)
    conversion_rate: float = Field(ge=0)
    avg_order_value: float = Field(ge=0)


class IncomeRequest(BaseModel):
    followers: float = Field(ge=0)
    engagement_rate: float = Field(ge=0)
    active_campaigns: float = Field(ge=0)
    avg_campaign_rate: float = Field(ge=0)
