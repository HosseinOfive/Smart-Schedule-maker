"""Compare input tokens: full parsed calendar vs. the free slots actually sent to the LLM.
Usage (from the repo root):  python -m measure_tokens path/to/calendar.ics
"""
import sys, json
from dotenv import load_dotenv
from google import genai
from backend.services.parser_service import parse_ics_file
from backend.ics_core.time_engine import TimeEngine

load_dotenv("backend/.env")
load_dotenv()

events = parse_ics_file(open(sys.argv[1], encoding="utf-8").read())
slots = TimeEngine.calc_free_time(events)[:15]   # same cap as AIScheduler

client = genai.Client()  # reads GOOGLE_API_KEY
def count(text: str) -> int:
    return client.models.count_tokens(model="gemini-2.5-flash", contents=text).total_tokens

full = count(json.dumps([e.model_dump(mode="json") for e in events]))
trimmed = count(json.dumps([s.model_dump(mode="json") for s in slots]))
print(f"events: {len(events)} | free slots sent: {len(slots)}")
print(f"full calendar: {full} tokens | free slots: {trimmed} tokens | saved {1 - trimmed / full:.0%}")