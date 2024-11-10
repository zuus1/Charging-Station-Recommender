import requests
from config import API_KEY

def test_places_api():
    # Define a location (latitude and longitude) and a radius
    # location = "42.3601,-71.0589"  # Example: Boston, MA
    location = "42.49250677392543, -83.47123073472288"  # Example: Detroit, MI
    radius = 10000  # Radius in meters (5 km)

    # Define the URL for the Places API (New) Nearby Search
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    # Set the parameters for the API request
    params = {
        "location": location,
        "radius": radius,
        "type": "electric_vehicle_charging_station",        
        "key": API_KEY
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    # Debugging: Print the full response JSON to see status or error messages
    print("Full Response JSON:", data)

    # Check if there are results
    if data.get("status") == "OK" and "results" in data:
        print("API Test Successful! Here’s a sample response:")
        for place in data["results"][:3]:
            print("\n--- Place ---")
            print("Name:", place.get("name"))
            print("Address:", place.get("vicinity"))
            print("Rating:", place.get("rating"))
    else:
        # Print status and error message if the request was unsuccessful
        print("Error or no results found. Status:", data.get("status"))
        if "error_message" in data:
            print("Error message:", data["error_message"])
            
# Run the test
test_places_api()