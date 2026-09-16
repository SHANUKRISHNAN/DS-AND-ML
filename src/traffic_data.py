def collect_traffic_data():
    traffic_data = {
        "vehicles": 150,
        "road_capacity": 200,
        "average_speed": 35,
        "road_name": "Main Road"
    }

    return traffic_data


data = collect_traffic_data()

print("EcoTwin Traffic Data")
print("Road:", data["road_name"])
print("Vehicles:", data["vehicles"])
print("Road Capacity:", data["road_capacity"])
print("Average Speed:", data["average_speed"], "km/h")