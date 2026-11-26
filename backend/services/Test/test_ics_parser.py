from datetime import datetime, timedelta, timezone
from backend.services.parser_service import parse_ics_file
from backend.ics_core.CONSTANTS import TARGET_TZ


### for testing the ICS ingestion service ###
### run from the project root: pytest backend/services/Test/test_ics_parser.py

# The parser only keeps events inside the expansion window (now -> now + EXPANSION_MONTHS),
# so the dates are built relative to today instead of being hardcoded.
# - Event 1: "CSCB07 Lecture" (Recurring weekly 3 times, Toronto time)
# - Event 2: "MATA41 Midterm" (Single event, specified in UTC)

LECTURE_DAY = (datetime.now(TARGET_TZ) + timedelta(days=7)).date()
MIDTERM_UTC = datetime.combine(LECTURE_DAY + timedelta(days=5), datetime.min.time(), tzinfo=timezone.utc).replace(hour=14)


def _ics(day, midterm_utc):
    d = day.strftime("%Y%m%d")
    m = midterm_utc.strftime("%Y%m%d")
    return f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//UTSC//Student Timetable//EN
BEGIN:VEVENT
SUMMARY:CSCB07 Lecture
DTSTART;TZID=America/Toronto:{d}T090000
DTEND;TZID=America/Toronto:{d}T110000
RRULE:FREQ=WEEKLY;COUNT=3
LOCATION:IC 130
DESCRIPTION:Prof. Abbott
END:VEVENT
BEGIN:VEVENT
SUMMARY:MATA41 Midterm
DTSTART:{m}T140000Z
DTEND:{m}T160000Z
LOCATION:SW 319
DESCRIPTION:Calculus II Test (Note: This time is in UTC!)
END:VEVENT
END:VCALENDAR"""


def test_parse_ics_file():
    events = parse_ics_file(_ics(LECTURE_DAY, MIDTERM_UTC))

    lectures = [e for e in events if e.summary == "CSCB07 Lecture"]
    midterms = [e for e in events if e.summary == "MATA41 Midterm"]
    assert len(lectures) == 3, "RRULE COUNT=3 should expand into 3 lectures"
    assert len(midterms) == 1

    # recurring lectures: weekly, always 9-11 local time (even across a DST change)
    for i, lecture in enumerate(lectures):
        assert lecture.start_time.date() == LECTURE_DAY + timedelta(weeks=i)
        assert (lecture.start_time.hour, lecture.start_time.minute) == (9, 0)
        assert lecture.end_time - lecture.start_time == timedelta(hours=2)
        assert lecture.location == "IC 130"

    # UTC event must be converted to Toronto time, same instant
    midterm = midterms[0]
    assert midterm.start_time == MIDTERM_UTC
    assert midterm.start_time.utcoffset() == MIDTERM_UTC.astimezone(TARGET_TZ).utcoffset()
    assert midterm.end_time - midterm.start_time == timedelta(hours=2)

    # every event should be in Toronto time with a real offset (-5:00 or -4:00, not LMT -5:18)
    for event in events:
        assert "Toronto" in str(event.start_time.tzinfo)
        assert event.start_time.utcoffset() in (timedelta(hours=-5), timedelta(hours=-4))

    assert events == sorted(events, key=lambda e: e.start_time)


def test_events_outside_window_are_dropped():
    past_day = (datetime.now(TARGET_TZ) - timedelta(days=60)).date()
    past_utc = datetime.combine(past_day, datetime.min.time(), tzinfo=timezone.utc).replace(hour=14)
    assert parse_ics_file(_ics(past_day, past_utc)) == []
