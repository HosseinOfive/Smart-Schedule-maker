from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List, Optional
import os, sys 
from dotenv import load_dotenv

# --- IMPORTS FROM YOUR PROJECT ---
# Ensure you have these files created as shown below!
from backend.ics_core.schemas import Event, MasterScheduleItem
from backend.services.parser_service import parse_ics_file
from backend.ics_core.time_engine import TimeEngine
from backend.services.AI_scheduler import AIScheduler
from backend.services.geo_mock import merge_and_validate_mock

load_dotenv()

app = FastAPI()

# --- CORS SETUP ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload_ics", response_model=List[MasterScheduleItem])
async def upload_ics(file: UploadFile = File(...)):
    print(f"🚀 Processing {file.filename}...")

    
    content = await file.read()   ###read the file content
    content_str = content.decode('utf-8')  ##for bytecode make it a string
    fixed_events: List[Event] = parse_ics_file(content_str)  ##get the fixed events from the ics file
    
    #print(f"✅ Parsed {len(fixed_events)} Fixed Events.") ##for debug 
    free_slots = TimeEngine.calc_free_time(fixed_events)  ##get free slots from the fixed events(what IA wants)
    #print(f"🔍 Found {len(free_slots)} Free Slots for AI.")  ## debug

    AI_result = await AIScheduler().generate_schedule(  ##wait for the AI to give us a schedule
        free_slots=free_slots,
        user_goal="Schedule 3 study sessions for Data Structures and Algorithms this week" )
    
    final_result = merge_and_validate_mock(fixed_events, AI_result)  ##merge and validate the AI result with fixed events using the MOCK service
    ##print(f"🧩 Merged schedule has {len(final_result)} items.") 

    final_result.sort(key=lambda x: x.start)   ##sort by start time easier to be read
    return final_result  ##becvk to front end
    






