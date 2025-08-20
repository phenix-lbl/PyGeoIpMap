# python ../pygeoipmap.py -i ./unique_ip.txt -o ./world.png --service m --db ./GeoLite2-City.mmdb >& log
python ../pygeoipmap.py -i ./unique_ip.txt  -o ../../phenixwebsite_metrics/figures/fig_usa.png --service m --db ./GeoLite2-City_20250819/GeoLite2-City.mmdb --extents=-130/-65/23/50 >& log
