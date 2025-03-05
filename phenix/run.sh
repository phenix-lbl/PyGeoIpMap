# python ../pygeoipmap.py -i ./unique_ip.txt -o ./world.png --service m --db ./GeoLite2-City.mmdb >& log
python ../pygeoipmap.py -i ./unique_ip.txt  -o ./usa.png --service m --db ./GeoLite2-City_20250228/GeoLite2-City.mmdb --extents=-130/-65/23/50 >& log
