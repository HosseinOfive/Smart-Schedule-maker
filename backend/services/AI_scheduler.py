import os
from pathlib import Path
from dotenv import load_dotenv
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from backend.ics_core.schemas import FreeSlot, ScheduleResponse

current_file_path = Path(__file__).resolve()
env_path = current_file_path.parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class AIScheduler: 
    """
    Interacts with google Generative AI
    this is a langchin wrapper
    in phase 3 this will be wrapped in a langGraph  ##the NOT mocked one ofc!
    """
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:  ##we dont have the API key in the .env 
            self.api_key = os.environ.get("GOOGLE_API_KEY")  ##looks in the OS
        if not self.api_key:
            raise ValueError("CRITICAL: GOOGLE_API_KEY is missing! Check your .env file.")
        
        ###initialize the model
        self.llm = ChatGoogleGenerativeAI(
            model = "gemini-2.5-flash",
            temperature=0.2,   ##keep it realistic
            api_key=self.api_key
        )

        self.parser = PydanticOutputParser(pydantic_object=ScheduleResponse)

    async def generate_schedule(self, free_slots: List[FreeSlot], user_goal: str ) -> ScheduleResponse:
            """
            takes in a list of FreeSlot objects and a user goal string
            returns a ScheduleResponse object from the AI
            """
            limited_slots = free_slots[:15] ##limit to first 15 slots to avoid token overload
            prompt = PromptTemplate(
                template="""
                You are an expert AI Scheduler.
                
                USER GOAL: "{user_goal}"
                
                AVAILABLE FREE TIME SLOTS (JSON):
                {free_slots}

                INSTRUCTIONS:
                1. Analyze the user's goal (e.g., frequency, preferred times).
                2. Select the BEST time slots from the provided list.
                3. CRITICAL: Do not invent time slots. Use ONLY the start/end times provided.
                4. Return the output strictly as a JSON object.
                
                {format_instructions}
                """,
                input_variables=["user_goal", "free_slots"],
                partial_variables={"format_instructions": self.parser.get_format_instructions()}
            )

            chain = prompt | self.llm | self.parser

            slots_json = [slot.model_dump_json() for slot in limited_slots]

            print("Sending request to AI Scheduler...\n waiting for response...")

            try: 
                result = await chain.ainvoke({
                    "user_goal": user_goal, 
                    "free_slots": slots_json
                })
                return result
            except Exception as e:
                print(f"❌ AI Service Error: {e}") #debug
                raise e 

            
