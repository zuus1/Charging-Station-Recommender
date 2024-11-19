import json
import requests
from config import OPEN_CHARGE_API_KEY

def get_charging_stations(location, radius_charging, min_charging_speed, max_charging_speed):
    url = "https://api.openchargemap.io/v3/poi/"
    params = {
        "key": OPEN_CHARGE_API_KEY,
        "latitude": location["lat"],
        "longitude": location["lng"],
        "distance": radius_charging,
        "distanceunit": "km",
        "minpowerkw": min_charging_speed,  
        "maxpowerkw": max_charging_speed,
        "maxresults": 10  # Limit the number of results
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching data:", response.status_code)
        return []

def list_chargers(location, radius, min_charging_speed, max_charging_speed):
    # Get the top 10 charging stations
    stations = get_charging_stations(location, radius, min_charging_speed, max_charging_speed)

    # Prepare data to be written to JSON file
    output_data = []
    for i, station in enumerate(stations, start=1):
        # Retrieve operator name from the OperatorInfo field
        operator_name = station.get("OperatorInfo", {}).get("Title") if station.get("OperatorInfo") else "Unknown"
        
        # Retrieve latitude and longitude
        station_lat = station.get("AddressInfo", {}).get("Latitude")
        station_lng = station.get("AddressInfo", {}).get("Longitude")

        station_data = {
            "Station Number": i,
            "Name": station.get("AddressInfo", {}).get("Title"),
            "Address": station.get("AddressInfo", {}).get("AddressLine1"),
            "Operator": operator_name,
            "Latitude": station_lat,   
            "Longitude": station_lng,  
            "Connections": [],
            "Connector Counts": {}
        }
      
        # Count the number of each connector type
        connector_counts = {}

        # Collect connection details for each station
        connections = station.get("Connections", [])
        for conn in connections:
            connector_type = conn.get("ConnectionType", {}).get("Title", "Unknown")
            power_kw = conn.get("PowerKW", "Unknown")
            quantity = conn.get("Quantity", 1)  # Default to 1 if Quantity is not specified

            # Add connector type and quantity to the connector count
            if connector_type in connector_counts:
                connector_counts[connector_type] += quantity
            else:
                connector_counts[connector_type] = quantity

            # Store each connection detail
            connection_data = {
                "Power (kW)": power_kw,
                "Connector Type": connector_type,
                "Current Type": conn.get("CurrentType", {}).get("Title"),
                "Level": conn.get("Level", {}).get("Title"),
                "Quantity": quantity
            }
            station_data["Connections"].append(connection_data)

        # Add the counts of each connector type to station data
        station_data["Connector Counts"] = connector_counts
        output_data.append(station_data)

    # Write data to JSON file
    with open("charging_stations.json", "w") as json_file:
        json.dump(output_data, json_file, indent=4)

    print("Data has been written to charging_stations.json")

