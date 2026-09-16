def validate_traffic_data(data):
    required_fields = [
        "vehicles",
        "road_capacity",
        "average_speed",
        "road_name"
    ]

    for field in required_fields:
        if field not in data:
            return False

    if data["vehicles"] < 0:
        return False

    if data["road_capacity"] <= 0:
        return False

    if data["average_speed"] < 0:
        return False

    return True


sample_data = {
    "vehicles": 150,
    "road_capacity": 200,
    "average_speed": 35,
    "road_name": "Main Road"
}

if validate_traffic_data(sample_data):
    print("Traffic data validation: PASSED")
else:
    print("Traffic data validation: FAILED")