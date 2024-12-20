import json

######################################################
# Filter charging stations based on user preferences
######################################################

def filter_pref(plug_type, min_charging_speed, max_charging_speed):
# def filter_pref(operator_pref, plug_type_pref, min_charging_speed, max_charging_speed):

    # Load the original charging station data from the JSON file
    with open("charging_stations.json", "r") as file:
        stations = json.load(file)

    # Filter the charging stations
    filtered_stations = []
    for station in stations:
        # Filter connections based on connector type and charging speed
        valid_connections = [
            connection for connection in station["Connections"]
            if connection["Connector Type"] == plug_type and connection["Power (kW)"] >= min_charging_speed and connection["Power (kW)"] <= max_charging_speed
        ]
        # Add the station to filtered results if it has any valid connections
        if valid_connections:
            station_copy = station.copy()       # Make a copy of the station
            station_copy["Connections"] = valid_connections  # Keep only the valid connections
            filtered_stations.append(station_copy)

    #    if station["Operator"] == operator_pref:
    #         # Filter connections based on connector type and charging speed
    #         valid_connections = [
    #             connection for connection in station["Connections"]
    #             if connection["Connector Type"] == plug_type_pref and connection["Power (kW)"] >= min_charging_speed and connection["Power (kW)"] <= max_charging_speed
    #         ]
    #         # Add the station to filtered results if it has any valid connections
    #         if valid_connections:
    #             station_copy = station.copy()       # Make a copy of the station
    #             station_copy["Connections"] = valid_connections  # Keep only the valid connections
    #             filtered_stations.append(station_copy)

    # Write the filtered stations to a new JSON file
    with open("charging_stations_filtered.json", "w") as outfile:
        json.dump(filtered_stations, outfile, indent=4)

    print("Filtered charging stations saved to filtered_charging_stations.json")