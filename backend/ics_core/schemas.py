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
    ##optional fields for phase 3
    validation_status: str = "Unknown"  # "Valid", "Impossible", "Unknown"
    validation_message: Optional[str] = None

class ScheduleResponse(BaseModel):   ##the thing AI returns
    scheduled_activities: list[ScheduledActivity]



###This is a diffrent class just use to feed to the frontend to deal with it more easily
#### it has a mixture of Event and ScheduledActivity 
###they have a flag to make sure they will be valid or not if not valid we will just scratch that activity when cleaning stuff later

class MasterScheduleItem(BaseModel):

    title: str              # From 'summary' (Class) or 'activity_name' (AI)
    start: datetime
    end: datetime
    location: str
    type: str               # "fixed" (immutable) or "suggested" (AI generated)
    
    # Validation flags
    validation_status: str    # "Valid", "Impossible"
    validation_message: Optional[str] = None