def select_traffic_action(traffic_level):
    if traffic_level == "High Traffic":
        return "Increase Green Signal Time"
    elif traffic_level == "Medium Traffic":
        return "Maintain Signal Timing"
    else:
        return "Reduce Green Signal Time"


traffic_level = "High Traffic"

recommended_action = select_traffic_action(traffic_level)

print("EcoTwin Traffic Optimization")
print("Traffic Level:", traffic_level)
print("Recommended Action:", recommended_action)