import requests
import json
from config import GOOGLE_PLACES_API_KEY
from math import radians, sin, cos, sqrt, atan2

######################################################
# Convert address to latitude and longitude
######################################################

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
    
######################################################
# Haversine formula to calculate distance between two lat/lng points
######################################################

def haversine_distance(lat1, lng1, lat2, lng2):
    R = 6371  # Earth radius in kilometers
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlng / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c  # km

######################################################
# Find nearby places for each charging station
######################################################

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

                # Get the place_id for further details
                place_id = place.get("place_id")
                website_url = None
                google_maps_url = None

                # Get place details to extract the URL using place_id
                if place_id:
                    place_details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                    place_details_params = {
                        "key": GOOGLE_PLACES_API_KEY,
                        "place_id": place_id,
                        "fields": "name,website,url"  # Specify the fields to get website and Google Maps URL
                    }

                    details_response = requests.get(place_details_url, params=place_details_params)
                    if details_response.status_code == 200:
                        details_data = details_response.json().get("result", {})
                        website_url = details_data.get("website")
                        google_maps_url = details_data.get("url")

                if distance <= radius_places:
                    place_info = {
                        "name": place.get("name"),
                        "address": place.get("vicinity"),
                        "rating": place.get("rating"),
                        "distance[m]": distance,
                        "website": website_url,
                        "google_maps_url": google_maps_url                        
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

    # Extract the top 3 highest-rated nearby facilities for each station
    all_results_filtered = all_results.copy()

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

    # Remove duplicates from the list of nearby facilities
    all_results_no_duplicates = all_results_filtered.copy()

    # Set to store (address, facility name) pairs for detecting duplicates
    seen_pairs = set()

    # Iterate through stations to identify and remove duplicate facilities
    for station in all_results_no_duplicates:
        station_address = station["Address"]

        # Loop through nearby facilities to detect and remove duplicates
        updated_nearby_facilities = []
        for facility in station["Nearby Facilities"]:
            facility_name = facility["name"]

            # Create a unique pair to identify duplicates
            station_pair = (station_address, facility_name)

            # Check if the pair has been seen before
            if station_pair not in seen_pairs:
                seen_pairs.add(station_pair)
                updated_nearby_facilities.append(facility)
        
        # Update the station's nearby facilities list
        station["Nearby Facilities"] = updated_nearby_facilities

    # Write the updated JSON to another file
    with open("nearby_places_no_duplicates.json", "w") as output_file:
        json.dump(all_results_no_duplicates, output_file, indent=4)

    print("Results have been written to nearby_places_no_duplicates.json")

######################################################
# Find places based on type
######################################################

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