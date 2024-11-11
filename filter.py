import json

def filter_pref(operator_pref, plug_type_pref, charging_speed_pref):
    # Load the original charging station data from the JSON file
    with open("charging_stations.json", "r") as file:
        stations = json.load(file)

    # Filter the charging stations
    filtered_stations = []
    for station in stations:
        if station["Operator"] == operator_pref:
            # Filter connections based on connector type and charging speed
            valid_connections = [
                connection for connection in station["Connections"]
                if connection["Connector Type"] == plug_type_pref and connection["Power (kW)"] >= charging_speed_pref
            ]
            # Add the station to filtered results if it has any valid connections
            if valid_connections:
                station_copy = station.copy()       # Make a copy of the station
                station_copy["Connections"] = valid_connections  # Keep only the valid connections
                filtered_stations.append(station_copy)

    # Write the filtered stations to a new JSON file
    with open("charging_stations_filtered.json", "w") as outfile:
        json.dump(filtered_stations, outfile, indent=4)

    print("Filtered charging stations saved to filtered_charging_stations.json")