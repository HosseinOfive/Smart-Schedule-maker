import pytest  # type: ignore
import sys
import os
from datetime import datetime, timedelta
import pytz


import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# --- 1. FORCE LOAD .ENV (FROM BACKEND FOLDER) ---
# Current file: backend/services/Test/test_api.py
# We need to go up 2 levels to find 'backend/'
current_test_path = Path(__file__).resolve()
backend_dir = current_test_path.parents[2] 
env_path = backend_dir / '.env'

print(f"🔍 Looking for .env at: {env_path}")
loaded = load_dotenv(dotenv_path=env_path)

if not loaded:
    print("❌ WARNING: .env not found! Checking if key exists in OS...")
else:
    print("✅ .env loaded successfully.")

# --- 2. PATH SETUP ---
# Add the project root (schedule/) to sys.path so imports work
project_root = backend_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# --- IMPORTS ---
from backend.services.AI_scheduler import AIScheduler
from backend.ics_core.schemas import FreeSlot, ScheduleResponse

# ... rest of the file (mock_free_slots, test function) stays the same


# --- PATH SETUP (To ensure imports work from 'schedule' root) ---
# This adds the parent directory of 'backend' to the python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- IMPORTS ---
from backend.services.AI_scheduler import AIScheduler
from backend.ics_core.schemas import FreeSlot, ScheduleResponse

# --- CONFIG ---
# Ensure you have a .env file in the root with GOOGLE_API_KEY
TORONTO_TZ = pytz.timezone("America/Toronto")

@pytest.fixture
def mock_free_slots():
    """
    Simulates the output of Phase 1 (TimeEngine).
    Creates 3 free slots in the near future.
    """
    now = datetime.now(TORONTO_TZ)
    today = now.date()
    
    # Slot 1: Today at 10:00 AM (2 hours)
    start_1 = TORONTO_TZ.localize(datetime.combine(today, datetime.strptime("10:00", "%H:%M").time()))
    if start_1 < now: # If 10am passed, move to tomorrow
         start_1 += timedelta(days=1)
    
    # Slot 2: Day after Slot 1 at 2:00 PM (2 hours)
    start_2 = start_1 + timedelta(days=1)
    start_2 = start_2.replace(hour=14, minute=0)

    # Slot 3: Day after Slot 2 at 6:00 PM (1.5 hours)
    start_3 = start_2 + timedelta(days=1)
    start_3 = start_3.replace(hour=18, minute=0)

    slots = [
        FreeSlot(
            start_time=start_1,
            end_time=start_1 + timedelta(hours=2),
            duration_min=120
        ),
        FreeSlot(
            start_time=start_2,
            end_time=start_2 + timedelta(hours=2),
            duration_min=120
        ),
        FreeSlot(
            start_time=start_3,
            end_time=start_3 + timedelta(minutes=90),
            duration_min=90
        )
    ]
    return slots

@pytest.mark.asyncio
async def test_ai_scheduler_integration(mock_free_slots):
    """
    Tests if the AI can take free slots + a goal and return valid JSON.
    """
    print("\n\n🧪 INITIALIZING PHASE 2 INTEGRATION TEST...")
    

    # let this crash naturally if the API Key is missing. Pytest will report it.
    scheduler = AIScheduler()

    # User Goal
    user_goal = "I want to hit the Gym 2 times this week."
    print(f"🎯 User Goal: {user_goal}")
    print(f"📂 Input: {len(mock_free_slots)} Free Slots provided.")

    # 3. Call the AI 
    response = await scheduler.generate_schedule(mock_free_slots, user_goal)

    # 4. Assertions & Validation
    print("\n🤖 AI RESPONSE RECEIVED:")
    print(response.model_dump_json(indent=2))

    assert isinstance(response, ScheduleResponse), "Response is not a ScheduleResponse Pydantic model"
    assert len(response.scheduled_activities) > 0, "AI returned no activities!"
    
    # Check logic
    assert len(response.scheduled_activities) <= len(mock_free_slots), "AI hallucinated more slots than available!"

    # Check consistency
    first_activity = response.scheduled_activities[0]
    assert first_activity.activity_name is not None
    assert first_activity.start_time is not None
    
    print("\n✅ TEST PASSED: Phase 2 Integration Successful!")