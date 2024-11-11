import chargers
import filter
import places
from places import classify_type

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
activity_pref = "I want to get milk, eggs, and bread."  # User activity

# Search radius (< remaining EV range)
radius = 10  # Radius in miles

######################################################
# Data Collection & Recommendation
######################################################

# Find 10 closest charging stations using Open Charge Map API
chargers.main(location, radius, charging_speed_pref)

# Filter based on charging station preferences
filter.main(operator_pref, plug_type_pref, charging_speed_pref)

# Assign a place type that best matches the user's activity using OpenAI 
classified_type = places.classify_type(activity_pref)
print("Type:", classified_type)

# Find places of the classified type using Google Places API
