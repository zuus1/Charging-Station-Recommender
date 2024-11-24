import requests
import json
from config import GOOGLE_PLACES_API_KEY
from math import radians, sin, cos, sqrt, atan2

# Convert address to latitude and longitude
def get_latlng(address):
    # Base URL for the Geocoding API
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    
    # Parameters for the API request
    params = {
        "address": address,
        "key": GOOGLE_PLACES_API_KEY,
    }
    
    # Send the request to the API
    response = requests.get(url, params=params)
    data = response.json()  # Parse JSON response
    
    # Check the response for a valid result
    if data['status'] == 'OK' and len(data['results']) > 0:
        # Extract latitude and longitude
        location = data['results'][0]['geometry']['location']  # This is already a dictionary
        return location  # Return the location dictionary
    else:
        raise ValueError(f"Geocoding API returned an error: {data['status']}")
    
    # # Parse the response JSON
    # if response.status_code == 200:
    #     data = response.json()
    #     if data['status'] == 'OK':
    #         # Extract latitude and longitude
    #         lat = data['results'][0]['geometry']['location']['lat']
    #         lng = data['results'][0]['geometry']['location']['lng']
    #         return lat, lng
    #     else:
    #         print(f"Geocoding API Error: {data['status']}")
    # else:
    #     print(f"HTTP Error: {response.status_code}")
    # return None, None

# Haversine formula to calculate distance between two lat/lng points
def haversine_distance(lat1, lng1, lat2, lng2):
    R = 6371  # Earth radius in kilometers
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlng / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c # km

# Function to find nearby places for each charging station
def find_places_keyword(radius_places, keywords):
    # Load charging stations data
    with open("charging_stations_filtered.json", 'r') as file:
        charging_stations = json.load(file)

    all_results = []

    for station in charging_stations:
        station_location = {"lat": station["Latitude"], "lng": station["Longitude"]}
        
        # Search nearby places for the current station
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "key": GOOGLE_PLACES_API_KEY,
            "location": f"{station_location['lat']},{station_location['lng']}",
            "radius": radius_places,
            "keyword": keywords
        }

        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])

            # Extract the top 10 hits within the specified radius
            nearby_places = []
            for place in results[:10]:
                place_location = place.get("geometry", {}).get("location", {})
                distance = haversine_distance(
                    station_location["lat"], station_location["lng"],
                    place_location.get("lat"), place_location.get("lng")
                )
                if distance <= radius_places:
                    place_info = {
                        "name": place.get("name"),
                        "address": place.get("vicinity"),
                        "rating": place.get("rating"),
                        "distance[m]": distance
                    }
                    nearby_places.append(place_info)

            # Append the station info along with its nearby facilities
            all_results.append({
                "Station Number": station["Station Number"],
                "Station Name": station["Name"],
                "Address": station["Address"],
                "Latitude": station["Latitude"],   
                "Longitude": station["Longitude"],  
                "Distance to station [km]": station["Distance to station [km]"],
                "Operator": station["Operator"],
                "Connector Counts": station["Connector Counts"],
                "Nearby Facilities": nearby_places
            })
        else:
            print(f"Error fetching data for station {station['Station Number']}: {response.status_code}")

    # Write all results to a JSON file
    with open("nearby_places.json", 'w') as json_file:
        json.dump(all_results, json_file, indent=4)
    
    print("Results have been written to nearby_places.json")
    
    # Make copy
    all_results_filtered = all_results.copy()

    # Extract the top 3 highest-rated nearby facilities for each station
    for station in all_results_filtered:
        if "Nearby Facilities" in station and station["Nearby Facilities"]:
            # Sort facilities by rating in descending order and take the top 3
            station["Nearby Facilities"] = sorted(
                station["Nearby Facilities"], key=lambda x: x["rating"], reverse=True
            )[:2]

    # Write the updated JSON to another file
    with open("nearby_places_filtered.json", "w") as output_file:
        json.dump(all_results_filtered, output_file, indent=4)

    print("Results have been written to nearby_places_filtered.json")

def find_places_type(location, radius_places, classified_type):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "key": GOOGLE_PLACES_API_KEY,
        "location": f"{location['lat']},{location['lng']}",
        "radius": radius_places,
        "type": classified_type,
    }

    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])

        # Extract the top 10 hits
        top_10_places = []
        for place in results[:10]:
            place_info = {
                "name": place.get("name"),
                "address": place.get("vicinity"),
                "rating": place.get("rating"),
                "location": place.get("geometry", {}).get("location"),
            }
            top_10_places.append(place_info)

        # Write the results to a JSON file
        with open("nearby_places.json", 'w') as json_file:
            json.dump(top_10_places, json_file, indent=4)
        
        print(f"Results have been written to nearby_places.json")          
        return top_10_places
    else:
        print("Error fetching data:", response.status_code)
        return []