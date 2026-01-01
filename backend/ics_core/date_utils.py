from ics_core.CONSTANTS import  TARGET_TZ, EXPANSION_MONTHS, DEFAULT_DAY_START_HOUR, DEFAULT_DAY_END_HOUR
from ics_core.schemas import Event, FreeSlot
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

######### Phase 2 ########
# everything before this line is phase 1 code 
############################

def calc_free_time( events: list[Event], day_start_hour =DEFAULT_DAY_START_HOUR, day_end_hour = DEFAULT_DAY_END_HOUR ) -> List[FreeSlot]: 
    """
    takes a list of Event objects (assumed to be sorted by start_time) and calculates free time slots between them within the specified daily hours.
    returns a list of Event objects representing free time slots. (can be given to IA)
    """
    if not events:
        return []
    
    free_slots=[]
    start_date = events[0].start_time.date()   ###since we assumed the events is already sorted by start time
    end_date = events[-1].end_time.date()
    
    current_date = start_date

    while current_date <= end_date:   ###this just iterates through each date in the range
        day_start = datetime.combine(current_date, time(day_start_hour, 0)).replace(tzinfo=TARGET_TZ)  
        day_end = datetime.combine(current_date, time(day_end_hour, 0)).replace(tzinfo=TARGET_TZ)
        
        ##thease 2 variables define the working hours for the current date (the time you are awake bassically)
        daily_events = [
            e for e in events 
            if e.start_time.date() <= current_date and e.end_time.date() >= current_date
        ]
        if not daily_events:   ##the whole day is free
            duration = (day_end - day_start).total_seconds() / 60 # duration in minutes
            free_slots.append(FreeSlot(
                start_time=day_start,
                end_time=day_end,
                duration_min=int(duration)
            ))
        else: ##we have something to do in the day
            ##we are free this morning before the first event
            first_event_start = max(daily_events[0].start_time, day_start)  ##if it starts at 7am and we start at 8am we cant be free before 8am 
            if day_start < first_event_start:
                duration = (first_event_start - day_start).total_seconds() / 60
                if duration >= 30:  ##only consider free slots of at least 30 minutes  to make it not computation dense for the AI
                    free_slots.append(FreeSlot(
                        start_time=day_start,
                        end_time=first_event_start,
                        duration_min=int(duration)
                    ))
            ##we are free between events
            for i in range(len(daily_events) - 1):
                curr_end = daily_events[i].end_time ##if this was the biginning of the day it would have been handled in the past
                next_start = daily_events[i + 1].start_time 
                ##need the diffrence between curr_end and next_start


                gap_start = max(curr_end, day_start)
                gap_end = min(next_start, day_end)
                ##stuff tat gors outside working hours is dealt with here 
                if gap_start < gap_end:
                    duration = (gap_end - gap_start).total_seconds() / 60
                    if duration >= 30:
                        free_slots.append(FreeSlot(
                            start_time=gap_start,
                            end_time=gap_end,
                            duration_min=int(duration)
                        ))
            last_event_end = min(daily_events[-1].end_time, day_end)
            
            ##we are free till we sleep
            if last_event_end < day_end:
                duration = (day_end - last_event_end).total_seconds() / 60
                if duration >= 30:
                    free_slots.append(FreeSlot(
                        start_time=last_event_end,
                        end_time=day_end,
                        duration_min=int(duration)
                    ))

        ##next day
        current_date += timedelta(days=1)
    return free_slots


