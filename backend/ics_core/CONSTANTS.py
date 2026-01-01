import pytz

TARGET_TZ = pytz.timezone("America/Toronto")
EXPANSION_MONTHS = 3
DEFAULT_DAY_START_HOUR = 8  # 8 AM
DEFAULT_DAY_END_HOUR = 22   # 10 PM
MIN_FREE_SLOT_MINUTES = 30  # Minimum duration for a free slot to be considered valid
FIXED_TRAVEL_TIME_MINUTES = 15   ##THIS is the fixed travel time we add between activities 
####IT IS FOR STUB
##later we implement DURATION ESTIMATION VIA MAPBOX 
