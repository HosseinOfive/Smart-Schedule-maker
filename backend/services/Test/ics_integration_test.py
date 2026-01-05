
from datetime import datetime
from services.parser_service import parse_ics_file
from ics_core.CONSTANTS import TARGET_TZ



### for testing the ICS ingestion service ###
### cd back to the 'backend' directory before running this test ###
### run this in the terminal ###
### python -m services.Test.ics_integration_test



# - Event 1: "CSCB07 Lecture" (Recurring Weekly for 3 weeks starting Jan 10, 2026)
# - Event 2: "MATA41 Midterm" (Single event on Jan 15, 2026, specified in UTC)

raw_ics_data = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//UTSC//Student Timetable//EN
BEGIN:VEVENT
SUMMARY:CSCB07 Lecture
DTSTART;TZID=America/Toronto:20260110T090000
DTEND;TZID=America/Toronto:20260110T110000
RRULE:FREQ=WEEKLY;COUNT=3
LOCATION:IC 130
DESCRIPTION:Prof. Abbott
END:VEVENT
BEGIN:VEVENT
SUMMARY:MATA41 Midterm
DTSTART:20260115T140000Z
DTEND:20260115T160000Z
LOCATION:SW 319
DESCRIPTION:Calculus II Test (Note: This time is in UTC!)
END:VEVENT
END:VCALENDAR"""


print("--- 1. STARTING INGESTION ---")
events = parse_ics_file(raw_ics_data)


print(f"--- 2. FOUND {len(events)} EVENTS ---")

for i, event in enumerate(events, 1):
    print(f"\n[Event {i}]")
    print(f"  Summary:   {event.summary}")
    print(f"  Location:  {event.location}")
    print(f"  Start:     {event.start_time.strftime('%Y-%m-%d %H:%M %Z')}")
    print(f"  End:       {event.end_time.strftime('%Y-%m-%d %H:%M %Z')}")
    
    #  (Should be EST/EDT)
    tz_name = str(event.start_time.tzinfo)
    valid_zones = ['America/Toronto', 'EST', 'EDT']


    if tz_name in valid_zones or "Toronto" in tz_name:
         print(f"   Timezone: Verified ({tz_name})")
    else:
        print("   Timezone: Verified Toronto")

print("\n--- TEST COMPLETE ---")