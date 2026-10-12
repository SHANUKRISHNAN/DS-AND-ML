#!/usr/bin/env bash
set -e

if [ -z "$SUMO_HOME" ]; then
    echo "ERROR: SUMO_HOME is not set. Install SUMO and export SUMO_HOME first."
    exit 1
fi

cd "$(dirname "$0")"

echo "[1/2] Generating 3x3 grid road network with traffic-light junctions..."
netgenerate --grid --grid.number=3 --grid.length=200 \
    --default.lanenumber=2 \
    --tls.guess=true \
    --output-file=city_grid.net.xml

echo "[2/2] Generating randomized traffic demand (3600s, moderate density)..."
python3 "$SUMO_HOME/tools/randomTrips.py" \
    -n city_grid.net.xml \
    -r city_grid.rou.xml \
    -e 3600 \
    -p 2.0

echo "Done. city_grid.net.xml and city_grid.rou.xml created."