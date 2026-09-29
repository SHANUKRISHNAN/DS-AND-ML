# generate_network.sh
# Creates a 4x4 grid network with traffic-light-controlled intersections
netgenerate --grid --grid.number=4 --grid.length=200 \
    --default.lanenumber=2 \
    --tls.guess=true \
    --output-file=city_grid.net.xml 