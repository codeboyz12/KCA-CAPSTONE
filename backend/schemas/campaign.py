from pydantic import BaseModel, Field

class CampaignInput(BaseModel):
    category:      str
    goal_usd:      float = Field(gt=0)
    duration_days: int   = Field(gt=0)
    launch_month:  int   = Field(ge=1, le=12)