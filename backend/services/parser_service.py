import pytz
from datetime import datetime, timedelta
from dateutil import rrule
from typing import List
from backend.ics_core.schemas import Event
from backend.ics_core.date_utils import norm_datetime, get_expansion_window
from icalendar import Calendar, Component


def expand_recurrences(
        rule_str: str,
        start_dt: datetime,
        duration: timedelta,
        summary: str,
        location: str,
        description: str
    ) -> List[Event]:
    """
    takes the .ics RRULE string and expands it into individual Event instances within the expansion window.
    returns a list of Event objects. in that RRULE
    """
    window_start, window_end = get_expansion_window()
    events = []

    rule = rrule.rrulestr(rule_str, dtstart=start_dt)

    instances = rule.between(window_start, window_end, inc=True)

    for dt in instances:
        dt_localized = norm_datetime(dt)

        events.append(Event(
            summary=summary,
            start_time=dt_localized,
            end_time=dt_localized + duration,
            location=location,
            description=description 
        ))

    return events

def single_event_creation(
        start_dt: datetime,
        end_dt: datetime,
        summary: str,
        location: str,
        description: str
    ) -> List[Event]: #for it being consistent with the other function make it a list
    """
    Creates a single Event instance from provided details.

    return a list containing one Event object. for sake of consistency with the other function (Polymorphism).
    """
    
    window_start, window_end = get_expansion_window()
    event = []
    if window_start <= start_dt <= window_end:
        

        event = [Event(
            summary=summary,
            start_time=start_dt,
            end_time=end_dt,
            location=location,
            description=description 
        )]

    return event



def process_vevent_component(component: Component) -> List[Event]: 
    """
    Process a single VEVENT component from an iCalendar file.
    Handles both single and recurring events.
    returns a list of Event objects. (a single Event list if a single event)
    """
    try:
        summary = str(component.get('SUMMARY', 'No Title'))
        location = str(component.get('LOCATION', ''))
        description = str(component.get('DESCRIPTION', ''))

        raw_start = component.get('DTSTART').dt
        raw_end = component.get('DTEND').dt
        
        
        start_dt = norm_datetime(raw_start)
        end_dt = norm_datetime(raw_end)
        
        duration = end_dt - start_dt

        rrule_component = component.get('RRULE')

        if rrule_component:
            return expand_recurrences(
                rule_str=rrule_component.to_ical().decode(),
                start_dt=start_dt,
                duration=duration,
                summary=summary,
                location=location,
                description=description
            )
        else:
            return single_event_creation(
                start_dt=start_dt,
                end_dt=end_dt,
                summary=summary,
                location=location,
                description=description
            )
    except Exception as e:
        print(f"Error processing VEVENT: {e}")
        return []
    


def parse_ics_file(content: str) -> List[Event]:
    """
    takes in .ics file path, parses it, and returns a list of Event objects.
    the function that communicates with outside world (file system).
    """
    fin_schedule = []
    try:
        cal = Calendar.from_ical(content)
    except ValueError as e:
        print(f"Error parsing .ics content: {e}")
        return fin_schedule    

    for component in cal.walk():
        if component.name == "VEVENT":
            events = process_vevent_component(component)
            fin_schedule.extend(events)

    fin_schedule.sort(key=lambda x: x.start_time)
    return fin_schedule



