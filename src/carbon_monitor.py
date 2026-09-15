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