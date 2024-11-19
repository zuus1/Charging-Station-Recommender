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

# Custom CSS to expand the entire page width
st.markdown(
    """
    <style>
    .block-container {
        max-width: 2000px; /* Adjust the page width */
        padding-left: 2rem;  /* Optional: Adjust padding */
        padding-right: 2rem; /* Optional: Adjust padding */
        padding-top: 3rem;  /* Reduce the top margin */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar for input
address = st.sidebar.text_input("Current location (address)", "")
radius_charging = st.sidebar.text_input("Search radius [km]", "")

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
activity= st.sidebar.text_area("What would you like to do while you wait for charging?", height=100)

# Add a search button
if st.sidebar.button("Search"):
    if not(address and radius_charging and activity):
        st.sidebar.markdown(
            '<p style="color:red;">Please enter all required queries to search</p>',
            unsafe_allow_html=True,        
        )

    # Convert address to latitude and longitude
    location = places.get_latlng(address)

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

# Main area for output
st.title("Charging Station Recommender")
st.write("A system to help EV drivers find the most convenient charging station based on their preferences")

# Create two columns
col1, spacer, col2 = st.columns([2, 0.03, 3])

with col1:
    # Google Maps Embed API URL for Boston, MA
    map_url = f"https://www.google.com/maps/embed/v1/place?key={GOOGLE_PLACES_API_KEY}&q=Boston,MA"

    # Embed the map in Streamlit using an iframe
    st.markdown(f'<iframe src="{map_url}" width="100%" height="500"></iframe>', unsafe_allow_html=True)

with col2:
    with open("nearby_places.json", 'r') as file:
        nearby_places = json.load(file)

    # Extract relevant data from the JSON file
    extracted_data = []
    for station in nearby_places:
        if station["Nearby Facilities"]:  # Check if Nearby Facilities is not empty
            for facility in station["Nearby Facilities"]:
                extracted_data.append({
                    "Station Name": station["Station Name"],
                    "Facility Name": facility["name"],
                    "Facility Address": facility["address"],
                    "Rating": facility["rating"],
                    # "Distance (m)": facility["distance[m]"]
                })

    # Convert the extracted data to a pandas DataFrame
    df = pd.DataFrame(extracted_data)

    # Display the extracted data in the Streamlit browser
    if not df.empty:
        st.write(df)
    else:
        st.write("No nearby facilities found.")