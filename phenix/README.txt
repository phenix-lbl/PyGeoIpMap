# helpful links

# map shape data
# https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html

# database of ip addresses and map locations
# do not commit database to repository
# https://dev.maxmind.com/geoip/geoip2/geolite2/

# instructions

# create new environment with Python
conda create -n map python=3.11
conda activate map

# install dependencies for PyGeoIpMap
python -m pip install -r ../requirements.txt

# run script to create usa.png
./run.sh
