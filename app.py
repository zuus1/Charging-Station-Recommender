import streamlit as st
import requests
from config import GOOGLE_PLACES_API_KEY
import chargers
import filter
import prompt
from prompt import classify_type
from prompt import extract_keywords
import places
from places import get_latlng
import json
import pandas as pd
import streamlit.components.v1 as components

######################################################
# Main page setup
######################################################

# Custom CSS to expand the entire page width
st.markdown(
    """
    <style>
    .block-container {
        max-width: 2000px; /* Adjust the page width */
        padding-left: 2rem;  /* Optional: Adjust padding */
        padding-right: 2rem; /* Optional: Adjust padding */
        padding-top: 2rem;  /* Reduce the top margin */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Charging Station Recommender")

######################################################
# Sidebar for input
######################################################

# Initial empty locations flags
locations_flags = []
all_flags = []

st.sidebar.write("Enter your preferences to find EV charging stations:")

address = st.sidebar.text_input("Current location (address)", "")
radius_charging_mi = st.sidebar.text_input("Search radius [mi]", "")

# Convert to kilometers if the input is valid
if radius_charging_mi:
    try:
        radius_charging = float(radius_charging_mi) * 1.60934
    except ValueError:
        st.error("Please enter a valid number for the search radius.")

option_charging_speed = st.sidebar.radio(
    "Select charging speed",
    ('Fast charging', 'Normal charging')
)

if option_charging_speed == 'Fast charging':
    min_charging_speed = 50  # kW
    max_charging_speed = 1000  # kW
else:
    min_charging_speed = 0  # kW
    max_charging_speed = 50  # kW

option_plug = st.sidebar.radio(
    "Select plug type",
    ('CCS1', 'NACS', 'CHAdeMO', 'J1772')
)

if option_plug == 'CCS1':
    plug_type = "CCS (Type 1)"
elif option_plug == 'CHAdeMO':
    plug_type = "CHAdeMO"
elif option_plug == 'J1772':
    plug_type = "Type 1 (J1772)"
elif option_plug == 'NACS':
    plug_type = "NACS / Tesla Supercharger"

# Create a text input field
activity = st.sidebar.text_area("What would you like to do while you wait for charging?", height=100)

######################################################
# Run search
######################################################

# Add a search button
if st.sidebar.button("Search"):
    if not(address and radius_charging and activity):
        st.sidebar.markdown(
            '<p style="color:red;">Please enter all required queries to search</p>',
            unsafe_allow_html=True,        
        )

    # Convert address to latitude and longitude
    location = places.get_latlng(address)

    # Create a flag for the current location
    current_flag = [{"name": "Current Location", "latitude": location["lat"], "longitude": location["lng"]}]

    # Find 10 closest charging stations using Open Charge Map API
    chargers.list_chargers(location, radius_charging, min_charging_speed, max_charging_speed)

    # Filter based on charging station preferences
    # filter.filter_pref(operator_pref, plug_type_pref, charging_speed_pref)
    filter.filter_pref(plug_type, min_charging_speed, max_charging_speed)

    # Assign a place type that best matches the user's activity using OpenAI 
    keywords = prompt.extract_keywords(activity)

    # Find places of the classified type using Google Places API
    radius_places = 150 # m
    places.find_places_keyword(radius_places, keywords)

    with open("nearby_places.json", 'r') as file:
        nearby_places = json.load(file)

    # Extract relevant data from the JSON file
    extracted_data = []
    for station in nearby_places:
        if station["Nearby Facilities"]:  # Check if Nearby Facilities is not empty
            for facility in station["Nearby Facilities"]:
                extracted_data.append({
                    "Charging Station Name": station["Station Name"],
                    "Charging Station Address": station["Address"],
                    "Latitude": station["Latitude"],
                    "Longitude": station["Longitude"],
                    "Distance [mi]": station["Distance to station [km]"]/1.60934,
                    "Operator": station["Operator"],
                    "Nearby Facility": facility["name"],
                    "Rating": facility["rating"],
                })

    # Remove lat/lng for display
    extracted_data_display = []
    for data in extracted_data:
        modified_data = data.copy()  # Create a copy of each dictionary to avoid modifying the original
        del modified_data["Latitude"]
        del modified_data["Longitude"]
        extracted_data_display.append(modified_data)

    # Convert the extracted data to a pandas DataFrame
    df = pd.DataFrame(extracted_data)
    df_display = pd.DataFrame(extracted_data_display)       

    # Extract data to create the locations_flags list in the desired format
    locations_flags = []
    for idx, row in df.iterrows():
        locations_flags.append({
            "name": row["Charging Station Name"],
            "latitude": row["Latitude"],
            "longitude": row["Longitude"]
        })

    all_flags = current_flag + locations_flags

    # Change the row numbers to start from 1
    df_display.index = range(1, len(df) + 1)

    # Display the extracted data in the Streamlit browser
    if not df_display.empty:
        st.write(df_display)
    else:
        st.write("No nearby facilities found.")

######################################################
# Visualization of icon on map
######################################################

# Function to generate JavaScript code to add markers
def generate_marker_js(all_flags):
    marker_js = ""
    
    for i, loc in enumerate(all_flags):
        # Alternate colors: Blue and Red
        icon_url = "http://maps.google.com/mapfiles/ms/icons/blue-dot.png" if i == 0 else "http://maps.google.com/mapfiles/ms/icons/red-dot.png"
        
        marker_js += f"""
        var marker{i} = new google.maps.Marker({{
          position: {{ lat: {loc["latitude"]}, lng: {loc["longitude"]} }},
          map: map,
          icon: '{icon_url}',  // Custom icon for the marker
          title: "{loc['name']}"
        }});
        var infoWindow{i} = new google.maps.InfoWindow({{
          content: "{loc['name']}"
        }});
        marker{i}.addListener('click', function() {{
          infoWindow{i}.open(map, marker{i});
        }});
        """
    return marker_js

# Set map center and zoom based on whether there are locations available
if locations_flags:
    # first_location = locations_flags[0]
    current_location = current_flag[0]
    map_center_js = f"{{ lat: {current_location['latitude']}, lng: {current_location['longitude']} }}"
    map_zoom = 12  # Zoom level closer to the locations
else:
    # Default to center of the USA if no locations available
    map_center_js = "{ lat: 39.8283, lng: -98.5795 }"
    map_zoom = 4  # Initial zoom level for the USA

# Initial empty map HTML
map_html = f"""
<!DOCTYPE html>
<html>
  <head>
    <style>
      #map {{
        height: 100%;
      }}
      html, body {{
        height: 100%;
        margin: 0;
        padding: 0;
      }}
    </style>
    <script src="https://maps.googleapis.com/maps/api/js?key={GOOGLE_PLACES_API_KEY}"></script>
    <script>
      var map;

      function initMap() {{
        map = new google.maps.Map(document.getElementById('map'), {{
          zoom: {map_zoom},
          center: {map_center_js}  // Center of USA
        }});
        {generate_marker_js(all_flags) if all_flags else ""}  // Add markers if available
      }}
    </script>
  </head>
  <body onload="initMap()">
    <div id="map" style="width: 80%; height: 400px;"></div>
  </body>
</html>
"""

# Display initial empty map
components.html(map_html, height=400)



