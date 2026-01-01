from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="ChronoCommute API", version="0.1.0")

@app.get("/")
async def health_check():
    return {
        "status": "online",
        "system": "ChronoCommute Logistics Engine",
        "version": "v1"
    }