import sys
import os
from datetime import datetime


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

# Add project root to sys.path so we can import 'backend.ics_core'
if project_root not in sys.path:
    sys.path.insert(0, project_root)


from backend.ics_core.schemas import Event, ScheduleResponse, ScheduledActivity
from backend.services.geo_mock import merge_and_validate_mock 

def test_aggregator_logic():
    print(f"🧪 Running Aggregator Test...\n")

    fixed_events = [
        Event(
            summary="CSCB07 Lecture",
            start_time=datetime(2025, 1, 15, 9, 0),
            end_time=datetime(2025, 1, 15, 10, 0), # Ends at 10:00 AM
            location="UTSC Campus",
            description="Software Design"
        )
    ]

    ai_suggestions = ScheduleResponse(
        scheduled_activities=[
            ScheduledActivity(
                activity_name="Morning Gym Session",
                start_time="2025-01-15T10:05:00", # Starts 10:05 AM
                end_time="2025-01-15T11:00:00",
                location="Pan Am Sports Centre"
            )
        ]
    )


    print("🔄 Merging and Validating...")
    master_schedule = merge_and_validate_mock(fixed_events, ai_suggestions)

    
    print(f"📊 Generated {len(master_schedule)} items.\n")

    gym_session = master_schedule[1] # The second item

    if gym_session.validation_status == "Impossible":
        print("✅ SUCCESS: The aggregator correctly flagged the impossible gap.")
        print(f"   Reason: {gym_session.validation_message}")
    else:
        print("❌ FAILURE: The aggregator failed to catch the impossible gap.")
        print(f"   Status was: {gym_session.validation_status}")

    
    print("\n--- Visual Output ---")
    for item in master_schedule:
        icon = "🟢" if item.validation_status == "Valid" else "🔴"
        print(f"{icon} {item.start.strftime('%H:%M')} - {item.end.strftime('%H:%M')} | {item.title} ({item.location})")

if __name__ == "__main__":
    test_aggregator_logic()