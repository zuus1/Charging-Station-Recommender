import chargers
import filter
import prompt
from prompt import classify_type
from prompt import extract_keywords
import places

######################################################
# User Input
######################################################

# Current location
location = {"lat": 42.482039, "lng": -83.472597}  # Detriot, MI  

# Charging station preferences
operator_pref = "Electrify America"  
plug_type_pref = "CCS (Type 1)"  
charging_speed_pref = 150  # kW

# User activity preferences
# activity_pref = "I want to get milk, eggs, and bread."  # User activity
# activity_pref = "I want to get cookies."  # User activity
activity_pref = "I want to get seafood."  # User activity

# Search radius
radius_charging = 10  # km
radius_places = 200 # m

######################################################
# Data Collection & Recommendation
######################################################

# Find 10 closest charging stations using Open Charge Map API
chargers.list_chargers(location, radius_charging, charging_speed_pref)

# Filter based on charging station preferences
filter.filter_pref(operator_pref, plug_type_pref, charging_speed_pref)

# Assign a place type that best matches the user's activity using OpenAI 
keywords = prompt.extract_keywords(activity_pref)
# classified_type = prompt.classify_type(activity_pref)

# Find places of the classified type using Google Places API
places.find_places_keyword(location, radius_places, keywords)
# places.find_places_type(location, radius_places, classified_type)

######################################################
# Visualization
######################################################
