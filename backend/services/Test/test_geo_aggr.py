from datetime import datetime
from backend.ics_core.CONSTANTS import TARGET_TZ
from backend.ics_core.schemas import Event, ScheduleResponse, ScheduledActivity, MasterScheduleItem
from backend.services.geo_mock import merge_and_validate_mock, polished_master_schedule


def _lecture():
    return Event(
        summary="CSCB07 Lecture",
        start_time=TARGET_TZ.localize(datetime(2025, 1, 15, 9, 0)),
        end_time=TARGET_TZ.localize(datetime(2025, 1, 15, 10, 0)),  # Ends at 10:00 AM
        location="UTSC Campus",
        description="Software Design"
    )


def _gym(start, end, location="Pan Am Sports Centre"):
    return ScheduleResponse(scheduled_activities=[
        ScheduledActivity(activity_name="Morning Gym Session", start_time=start, end_time=end, location=location)
    ])


def _suggested(master_schedule):
    return next(item for item in master_schedule if item.type == "suggested")


def test_aggregator_flags_impossible_gap():
    # 5 minute gap to a different location, less than FIXED_TRAVEL_TIME_MINUTES
    master_schedule = merge_and_validate_mock(
        [_lecture()], _gym("2025-01-15T10:05:00-05:00", "2025-01-15T11:00:00-05:00"))

    assert len(master_schedule) == 2
    assert [item.type for item in master_schedule] == ["fixed", "suggested"]  # sorted by start
    gym_session = _suggested(master_schedule)
    assert gym_session.validation_status == "Impossible"
    assert "too short for travel" in gym_session.validation_message
    assert master_schedule[0].validation_status == "Valid"  # the fixed lecture is never blamed


def test_aggregator_allows_enough_travel_time():
    master_schedule = merge_and_validate_mock(
        [_lecture()], _gym("2025-01-15T10:30:00-05:00", "2025-01-15T11:30:00-05:00"))

    assert _suggested(master_schedule).validation_status != "Impossible"


def test_aggregator_same_location_needs_no_travel():
    master_schedule = merge_and_validate_mock(
        [_lecture()], _gym("2025-01-15T10:05:00-05:00", "2025-01-15T11:00:00-05:00", location="UTSC Campus"))

    assert _suggested(master_schedule).validation_status != "Impossible"


def test_polished_master_schedule_removes_adjacent_impossible_items():
    def item(title, status):
        return MasterScheduleItem(
            title=title, start=TARGET_TZ.localize(datetime(2025, 1, 15, 9, 0)),
            end=TARGET_TZ.localize(datetime(2025, 1, 15, 10, 0)),
            location="X", type="suggested", validation_status=status)

    items = [item("a", "Valid"), item("b", "Impossible"), item("c", "Impossible"), item("d", "Valid")]
    assert [i.title for i in polished_master_schedule(items)] == ["a", "d"]
    assert len(items) == 4  # input list is left untouched
