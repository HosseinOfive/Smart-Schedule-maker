from datetime import datetime, timedelta, time
from typing import List
from zoneinfo import ZoneInfo
from backend.ics_core.schemas import Event, FreeSlot
from ics_core.CONSTANTS import  TARGET_TZ, EXPANSION_MONTHS, DEFAULT_DAY_START_HOUR, DEFAULT_DAY_END_HOUR, MIN_FREE_SLOT_MINUTES



class TimeEngine:
    """
    Core domain logic for analyzing schedule gaps.
    """
    @staticmethod
    def calc_free_time( events: list[Event], day_start_hour =DEFAULT_DAY_START_HOUR,
                        day_end_hour = DEFAULT_DAY_END_HOUR ) -> List[FreeSlot]: 
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
            daily_slots = TimeEngine._find_gaps_in_day(day_start, day_end, daily_events)
            free_slots.extend(daily_slots)
            ##next day
            current_date += timedelta(days=1)
        return free_slots
    
    
    
    
    
    @staticmethod
    def _find_gaps_in_day(day_start: datetime, day_end: datetime, daily_events: List[Event]) -> List[FreeSlot]:
        """
        Helper function to find gaps in a single day given the day's start and end times and the list of events for that day.
        """
        free_slots=[]
        if not daily_events:   ##the whole day is free
            duration = (day_end - day_start).total_seconds() / 60 # duration in minutes
            return [FreeSlot(
                start_time=day_start,
                end_time=day_end,
                duration_min=int(duration)
            )]
        else: ##we have something to do in the day
            ##we are free this morning before the first event
            first_event_start = max(daily_events[0].start_time, day_start)  ##if it starts at 7am and we start at 8am we cant be free before 8am 
            if day_start < first_event_start:
                TimeEngine._add_slot_if_valid(day_start, first_event_start, free_slots)
            ##we are free between events
            for i in range(len(daily_events) - 1):
                curr_end = daily_events[i].end_time ##if this was the biginning of the day it would have been handled in the past
                next_start = daily_events[i + 1].start_time 
                ##need the diffrence between curr_end and next_start


                gap_start = max(curr_end, day_start)
                gap_end = min(next_start, day_end)
                ##stuff tat gors outside working hours is dealt with here 
                if gap_start < gap_end:
                    TimeEngine._add_slot_if_valid(day_start, first_event_start, free_slots)
            last_event_end = min(daily_events[-1].end_time, day_end)
            
            ##we are free till we sleep
            if last_event_end < day_end:
                TimeEngine._add_slot_if_valid(day_start, first_event_start, free_slots)
        return free_slots
    
    
    @staticmethod
    def _add_slot_if_valid(start: datetime, end: datetime, slot_list: List[FreeSlot], min_minutes=MIN_FREE_SLOT_MINUTES):
        """Utility to DRY up the duration check."""
        duration = (end - start).total_seconds() / 60
        if duration >= min_minutes:
            slot_list.append(FreeSlot(start_time=start, end_time=end, duration_min=int(duration)))
