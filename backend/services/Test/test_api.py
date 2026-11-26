import os
from datetime import datetime, time, timedelta
from pathlib import Path

import pytest  # type: ignore
from dotenv import load_dotenv

from backend.ics_core.CONSTANTS import TARGET_TZ
from backend.ics_core.schemas import FreeSlot, ScheduleResponse
from backend.services.AI_scheduler import AIScheduler

# Load GOOGLE_API_KEY from backend/.env (this file is backend/services/Test/test_api.py)
load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

# This test calls the real Gemini API: skipped when there is no key.
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="GOOGLE_API_KEY not set (add it to backend/.env)"),
]


def _slot(day, hour, minutes):
    # localize each slot separately so the offset is right even across a DST change
    start = TARGET_TZ.localize(datetime.combine(day, time(hour, 0)))
    return FreeSlot(start_time=start, end_time=start + timedelta(minutes=minutes), duration_min=minutes)


@pytest.fixture
def mock_free_slots():
    """
    Simulates the output of Phase 1 (TimeEngine).
    Creates 3 free slots on the next 3 days.
    """
    tomorrow = datetime.now(TARGET_TZ).date() + timedelta(days=1)
    return [
        _slot(tomorrow, 10, 120),                      # Slot 1: 10:00 AM (2 hours)
        _slot(tomorrow + timedelta(days=1), 14, 120),  # Slot 2: 2:00 PM (2 hours)
        _slot(tomorrow + timedelta(days=2), 18, 90),   # Slot 3: 6:00 PM (1.5 hours)
    ]


def _fits_in_a_slot(activity, slots):
    start = datetime.fromisoformat(activity.start_time)
    end = datetime.fromisoformat(activity.end_time)
    if start.tzinfo is None:
        start, end = TARGET_TZ.localize(start), TARGET_TZ.localize(end)
    return any(s.start_time <= start and end <= s.end_time for s in slots)


async def test_ai_scheduler_integration(mock_free_slots):
    """
    Tests if the AI can take free slots + a goal and return valid JSON.
    """
    scheduler = AIScheduler()
    user_goal = "I want to hit the Gym 2 times this week."

    response = await scheduler.generate_schedule(mock_free_slots, user_goal)
    print(response.model_dump_json(indent=2))

    assert isinstance(response, ScheduleResponse), "Response is not a ScheduleResponse Pydantic model"
    assert len(response.scheduled_activities) > 0, "AI returned no activities!"
    assert len(response.scheduled_activities) <= len(mock_free_slots), "AI hallucinated more slots than available!"

    for activity in response.scheduled_activities:
        assert activity.activity_name
        assert _fits_in_a_slot(activity, mock_free_slots), f"{activity.activity_name} is outside every free slot"
