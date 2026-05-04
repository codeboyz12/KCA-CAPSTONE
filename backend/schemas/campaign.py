from pydantic import BaseModel, Field


class CampaignInput(BaseModel):
    """Full input for prediction (v2 pipeline)."""
    name:           str   = ""
    category:       str
    main_category:  str   = ""
    country:        str   = "US"
    goal_usd:       float = Field(gt=0)
    duration_days:  int   = Field(gt=0)
    launch_year:    int   = Field(default=2020, ge=2009, le=2030)
    launch_month:   int   = Field(default=6, ge=1, le=12)
    launch_day:     int   = Field(default=15, ge=1, le=31)
    launch_hour:    int   = Field(default=12, ge=0, le=23)
    launch_minute:  int   = Field(default=0, ge=0, le=59)
    deadline_year:  int   = Field(default=2020, ge=2009, le=2030)
    deadline_month: int   = Field(default=6, ge=1, le=12)
    deadline_day:   int   = Field(default=15, ge=1, le=31)
    deadline_hour:  int   = Field(default=12, ge=0, le=23)
    deadline_minute: int  = Field(default=0, ge=0, le=59)
