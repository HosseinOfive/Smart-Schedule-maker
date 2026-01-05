from backend.ics_core.CONSTANTS import  TARGET_TZ, EXPANSION_MONTHS, DEFAULT_DAY_START_HOUR, DEFAULT_DAY_END_HOUR
from backend.ics_core.schemas import Event, FreeSlot
from datetime import datetime, timedelta, time
from typing import  Any, Tuple, List
from dateutil.relativedelta import relativedelta


def norm_datetime(dt: Any, target_tz=TARGET_TZ) -> datetime:
    """
    Conversts any datetime object(dt) to the target timezone(target_tz).
    Handles both naive and aware datetime objects + all date obj (full day events).
    """
    if type(dt) is not datetime: ## pure date obj (all day events)
        dt = datetime.combine(dt, datetime.min.time())
    if dt.tzinfo is None:
        return target_tz.localize(dt)  # naive type
    return dt.astimezone(target_tz)  #aware type 

def get_expansion_window() -> Tuple[datetime, datetime]:
    """
    Returns the start and end datetime for the expansion window.
    Start is current time in target timezone.
    End is start + EXPANSION_MONTHS months.
    """
    now = datetime.now(TARGET_TZ)
    lim = now + relativedelta(months=EXPANSION_MONTHS)
    return now, lim


