# Smart-Schedule-maker : LLM-Powered Calendar Assistant
## What it is
Smart-Schedule-maker is an AI-powered scheduling assistant that reads real calendar data and automatically reschedules events based on natural-language instructions.

Users can upload a `.ics` calendar file, describe what they want to change in plain English (e.g. “I want to go to gym 3 time a week but not in the mornings or Fridays”). The system uses an LLM to reason over time conflicts and update the calendar via API calls. 

This project explores how large language models can be used as **decision-making engines** for real-world productivity tools.

## What is does
1.  **Ingests:** Parses raw `.ics` files (e.g., UofT Semester Schedule).
2.  **Analyzes:** Algorithmic gap detection identifies usable time blocks(optimizes LLM usage and inference cost).
3.  **Optimizes:** Uses **Google Gemini 2.5 Flash** (via LangChain) to reason through natural language constraints (e.g., *"I need to study for CSCB36 for 6 hours, but only in 2-hour blocks"*).
4.  **Validates:** Ensures suggested activities are physically feasible by calculating commute buffers between locations.

## How it works 
* User upload an `.ics` file + natural language request ( I wanna go to the gym 3 times a week)
* Calendar data is converted into a class and free time is calculated
* LangChain send the free time and the request to LLM
* The LLM outputs the scheduling decisions
* The backend validates those changes based on the commute time of the locations
* The backend applies those changes via API calls and sends them to Frontend
* The Frontend displayes the new shcedule

## Tech Stack
### Backend 
* **Python 3.12** & **FastAPI** (High-performance Async API)
* **LangChain** (Orchestration for LLM workflows)
* **Google Gemini 2.5 Flash** (Generative AI for constraint reasoning)
* **Pydantic** (Strict data validation & serialization)
* **Icalendar** (RFC 5545 parsing standards)

### Frontend (The Interface)
* **TypeScript** & **Next.js 14** (App Router)
* **React Big Calendar** (Scheduling visualization)
* **Tailwind CSS** (Modern UI styling)

### Testing
*  API endpoints are covered by automated tests written with pytest.
*  Used mocked dependencies to isolate and test scheduling logic.
## Known limitations
* Commute time is currently mocked at 15 minutes
* Some UI controls are not wired yet
* Uses LangChain instead of LangGraph for linear workflows
* These were intentional tradeoffs to focus on validating the core AI-driven scheduling pipeline.

## Demo



https://github.com/user-attachments/assets/b17243bd-011d-45d5-83ff-77c34a938515



## Future Work
* Replace mocked commute with real map APIs
* Switch to LangGraph for branching workflows
* Add full command-line and mobile UI
