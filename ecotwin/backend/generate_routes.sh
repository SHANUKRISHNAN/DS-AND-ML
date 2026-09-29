# generate_routes.sh
# Uses SUMO's built-in random trip generator to simulate realistic demand
python "%SUMO_HOME%\tools\randomTrips.py" 
    -n city_grid.net.xml 
    -r city_grid.rou.xml 
    -e 3600 
    --period 2 
    --fringe-factor 5 
    --validate