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

