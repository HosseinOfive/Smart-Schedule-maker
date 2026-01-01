from datetime import datetime
from typing import List
from dateutil import parser  # distinct from icalendar, helps parse ISO strings
from backend.ics_core.schemas import Event, ScheduleResponse, ScheduledActivity, MasterScheduleItem
from backend.ics_core.CONSTANTS import FIXED_TRAVEL_TIME_MINUTES
from copy import deepcopy

def merge_and_validate_mock(
    fixed_events: List[Event], 
    ai_response: ScheduleResponse
) -> List[MasterScheduleItem]:
    """
    Converts and fits both IA activities and fixed events into a unified master schedule.
    SOrts them by start time,
    then in the mean while it will also validate the activities based on time conflicts and logical errors.
    Returns a list of Master scheduleItem objects.
    """
    master_list: List[MasterScheduleItem] = []
    ###print("at least I exist")
    # Convert fixed events to MasterScheduleItem
    for event in fixed_events:
        master_list.append(MasterScheduleItem(
            title=event.summary,
            start=event.start_time,
            end=event.end_time,
            location=event.location or "N/A",
            type="fixed",
            validation_status="Valid"
        ))
    
    # Convert AI scheduled activities to MasterScheduleItem
    for activity in ai_response.scheduled_activities:
        start_dt = parser.isoparse(activity.start_time)
        end_dt = parser.isoparse(activity.end_time)

        master_list.append(MasterScheduleItem(
            title=activity.activity_name,
            start=start_dt,
            end=end_dt,
            location=activity.location or "N/A",
            type="suggested",
            validation_status=activity.validation_status,
            validation_message=activity.validation_message
        ))
    # Sort the master list by start time
    master_list.sort(key=lambda x: x.start)

    ###print(f"DEBUG: Merged {len(master_list)} items.")


    # Validate for conflicts and logical errors
    for i in range(len(master_list) - 1):
        current_item = master_list[i]
        next_item = master_list[i+1]
        if current_item.location == next_item.location:
            continue  # No travel time needed
        # calc the gap between current end and next start
        gap_sec = next_item.start - current_item.end
        gap_min = gap_sec.total_seconds() / 60

        ##print(f"DEBUG: Checking Gap: {current_item.title} -> {next_item.title}")
        ##print(f"       Gap: {gap_min} min | Required: {FIXED_TRAVEL_TIME_MINUTES} min")

        if gap_min < FIXED_TRAVEL_TIME_MINUTES:
            ###print(f"        FLAGGING IMPOSSIBLE")
            msg = (f"Impossible: {int(gap_min)}m gap is too short for travel. "
                   f"(Need {FIXED_TRAVEL_TIME_MINUTES}m)")
            ##try to find whos faoult it is (we need to get rid of the suggested activity)
            ##also if they are both fixed events we just let it be 
            if current_item.type == "fixed" and next_item.type == "fixed":
                continue  ##we cant do anything about it)
            if next_item.type == "suggested":
                next_item.validation_status = "Impossible"
                next_item.validation_message = msg
            else:
                current_item.validation_status = "Impossible"
                current_item.validation_message = msg

    return master_list


###all you have to do is call this function with the fixed events and the AI response
###it will return the master schedule list that front end will use to display stuff
##also this will change in later versions to make it more intelligent and use MAPBOX or something similar to get real travel times


def polished_master_schedule(
    events: List[MasterScheduleItem]
) -> List[MasterScheduleItem]:
    """
    Cleans up the master schedule by removing impossible activities.
    """
    polished_list = deepcopy(events)
    for item in polished_list:
        if item.validation_status == "Impossible":
            polished_list.remove(item)
    return polished_list

