import pytz
from datetime import datetime
from typing import  Optional
from pydantic import BaseModel


TARGET_TZ = pytz.timezone("America/Toronto")
EXPANSION_MONTHS = 3

class Event(BaseModel):
    summary: str
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    description: Optional[str] = None

#####Phase 2 ######
class FreeSlot(BaseModel):  ##we feed a list of this to the AI
    start_time: datetime
    end_time: datetime
    duration_min: int

class ScheduledActivity(BaseModel):  ##AI gives us a list of this
    activity_name: str
    start_time: str
    end_time: str
    location: str

class ScheduleResponse(BaseModel):   ##the thing AI returns
    scheduled_activities: list[ScheduledActivity]
