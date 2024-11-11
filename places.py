import requests
import json
from config import GOOGLE_PLACES_API_KEY
from math import radians, sin, cos, sqrt, atan2

# Haversine formula to calculate distance between two lat/lng points
def haversine_distance(lat1, lng1, lat2, lng2):
    R = 6371  # Earth radius in kilometers
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlng / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c * 1000  # Convert km to meters

def find_places_keyword(location, radius_places, keywords):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "key": GOOGLE_PLACES_API_KEY,
        "location": f"{location['lat']},{location['lng']}",
        "radius": radius_places,
        "keyword": keywords,
    }

    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])

        # Extract the top 10 hits, ensure they are within the radius
        top_10_places = []
        for place in results[:10]:
            place_location = place.get("geometry", {}).get("location", {})
            distance = haversine_distance(
                location["lat"], location["lng"],
                place_location.get("lat"), place_location.get("lng")
            )
            if distance <= radius_places:
                place_info = {
                    "name": place.get("name"),
                    "address": place.get("vicinity"),
                    "rating": place.get("rating"),
                    # "location": place.get("geometry", {}).get("location"),
                    "distance[m]": distance
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