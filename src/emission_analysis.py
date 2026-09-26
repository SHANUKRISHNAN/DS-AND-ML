def calculate_emission(vehicle_count, emission_per_vehicle):
    return vehicle_count * emission_per_vehicle


def analyze_emission(emission):
    if emission < 15:
        return "Low Emission"
    elif emission < 30:
        return "Moderate Emission"
    else:
        return "High Emission"


vehicles = 150
emission_per_vehicle = 0.12

total_emission = calculate_emission(
    vehicles, emission_per_vehicle
)

emission_level = analyze_emission(total_emission)

print("EcoTwin Emission Analysis")
print("Total Emission:", total_emission, "kg")
print("Emission Level:", emission_level)