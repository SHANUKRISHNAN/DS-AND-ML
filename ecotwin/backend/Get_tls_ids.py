"""
Prints every traffic-light ID in your city_grid.net.xml, in the exact form
EcoTwinEnv needs for its tls_ids list. Run this from inside the backend
folder, alongside city_grid.net.xml.
"""
import re

with open("city_grid.net.xml", encoding="utf-8") as f:
    content = f.read()

ids = re.findall(r'<tlLogic id="([^"]+)"', content)
ids = sorted(set(ids))

print(f"Found {len(ids)} traffic lights:")
print(ids)