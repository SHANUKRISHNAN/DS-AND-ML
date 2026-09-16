def calculate_carbon_emission(vehicle_count, emission_per_vehicle):
    return vehicle_count * emission_per_vehicle


vehicles = 100
emission_per_vehicle = 0.12

carbon_emission = calculate_carbon_emission(
    vehicles, emission_per_vehicle
)

print("EcoTwin Carbon Monitoring")
print("Vehicles:", vehicles)
print("Estimated Carbon Emission:", carbon_emission, "kg")
def calculate_traffic_density(vehicle_count, road_capacity):
    density = (vehicle_count / road_capacity) * 100
    return density


road_capacity = 200

traffic_density = calculate_traffic_density(
    vehicles, road_capacity
)

print("Traffic Density:", traffic_density, "%")
def classify_traffic_level(density):
    if density < 30:
        return "Low Traffic"
    elif density < 70:
        return "Medium Traffic"
    else:
        return "High Traffic"


traffic_level = classify_traffic_level(traffic_density)

print("Traffic Level:", traffic_level)