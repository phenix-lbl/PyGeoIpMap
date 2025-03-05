#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function, unicode_literals, with_statement
import argparse
import contextlib
import requests
import sys
import csv
import matplotlib
# Anti-Grain Geometry (AGG) backend so PyGeoIpMap can be used 'headless'
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from mpl_toolkits.basemap import Basemap
import geoip2.database

def get_ip(ip_file):
    """
    Returns a list of IP addresses from a file containing one IP per line.
    """
    with contextlib.closing(ip_file):
        return [line.strip() for line in ip_file]


def get_lat_lon(api_key, ip_list=[], lats=[], lons=[]):
    """
    This function connects to the FreeGeoIP web service to get info from
    a list of IP addresses.
    Returns two lists (latitude and longitude).
    """
    print("Processing {} IPs...".format(len(ip_list)))
    for ip in ip_list:
        r = requests.get("http://api.ipstack.com/" + ip + "?access_key=" + api_key)
        json_response = r.json()
        print("{ip}, {region_name}, {country_name}, {latitude}, {longitude}".format(**json_response))
        if json_response['latitude'] and json_response['longitude']:
            lats.append(json_response['latitude'])
            lons.append(json_response['longitude'])
    return lats, lons


def geoip_lat_lon(gi, ip_list=[], lats=[], lons=[]):
    """
    This function uses the MaxMind library and databases to geolocate IP addresses
    Returns two lists (latitude and longitude).
    """
    print("Processing {} IPs...".format(len(ip_list)))
    for ip in ip_list:
        try:
            r = gi.city(ip)
        except Exception:
            print("Unable to locate IP: %s" % ip)
            continue
        if r is None or r.location.latitude is None or r.location.longitude is None:
            print("Unable to find lat/long for IP: %s" % ip)
            continue
        # only keep points inside US
        if r.country.iso_code == 'US':
            lats.append(r.location.latitude)
            lons.append(r.location.longitude)
    return lats, lons


def get_lat_lon_from_csv(csv_file, lats=[], lons=[]):
    """
    Retrieves the last two rows of a CSV formatted file to use as latitude
    and longitude.
    Returns two lists (latitudes and longitudes).

    Example CSV file:
    119.80.39.54, Beijing, China, 39.9289, 116.3883
    101.44.1.135, Shanghai, China, 31.0456, 121.3997
    219.144.17.74, Xian, China, 34.2583, 108.9286
    64.27.26.7, Los Angeles, United States, 34.053, -118.2642
    """
    with contextlib.closing(csv_file):
        reader = csv.reader(csv_file)
        for row in reader:
            lats.append(row[-2])
            lons.append(row[-1])

    return lats, lons


def generate_map(output, lats=[], lons=[], wesn=None):
    """
    Using Basemap and the matplotlib toolkit, this function generates a map and
    puts a red dot at the location of every IP addresses found in the list.
    The map is then saved in the file specified in `output`.
    """
    print("Generating map and saving it to {}".format(output))
    projection = 'merc'
    # if wesn:
    #     wesn = [float(i) for i in wesn.split('/')]
    #     m = Basemap(projection=projection, resolution='l',
    #             llcrnrlon=wesn[0], llcrnrlat=wesn[2],
    #             urcrnrlon=wesn[1], urcrnrlat=wesn[3])
    # else:
    #     m = Basemap(projection=projection, resolution='l')


    fig, ax = plt.subplots()

    # Lambert Conformal map of lower 48 states.
    m = Basemap(llcrnrlon=-119,llcrnrlat=20,urcrnrlon=-63,urcrnrlat=50,
                projection='lcc',lat_1=33,lat_2=45,lon_0=-95,resolution=None)

    # Mercator projection, for Alaska and Hawaii
    # m = Basemap(llcrnrlon=-185,llcrnrlat=17,urcrnrlon=-66,urcrnrlat=72.5,
    #             projection='merc',lat_ts=20)  # do not change these numbers

    shp_info = m.readshapefile('cb_2018_us_state_500k','states',drawbounds=True,
                               linewidth=0.45,color='black')

    # AREA_1 = 0.005  # exclude small Hawaiian islands that are smaller than AREA_1
    # AREA_2 = AREA_1 * 30.0  # exclude Alaskan islands that are smaller than AREA_2
    # AK_SCALE = 0.19  # scale down Alaska to show as a map inset
    # HI_OFFSET_X = -1900000  # X coordinate offset amount to move Hawaii "beneath" Texas
    # HI_OFFSET_Y = 250000    # similar to above: Y offset for Hawaii
    # AK_OFFSET_X = -250000   # X offset for Alaska (These four values are obtained
    # AK_OFFSET_Y = -750000   # via manual trial and error, thus changing them is not recommended.)

    # for nshape, shapedict in enumerate(m.states_info):  # plot Alaska and Hawaii as map insets
    #     if shapedict['NAME'] in ['Alaska', 'Hawaii']:
    #         seg = m.states[int(shapedict['SHAPENUM'] - 1)]
    #         print(shapedict)
    #         if shapedict['NAME'] == 'Hawaii' and float(shapedict['ALAND']) > AREA_1:
    #             seg = [(x + HI_OFFSET_X, y + HI_OFFSET_Y) for x, y in seg]
    #         elif shapedict['NAME'] == 'Alaska' and float(shapedict['ALAND']) > AREA_2:
    #             seg = [(x*AK_SCALE + AK_OFFSET_X, y*AK_SCALE + AK_OFFSET_Y)\
    #                    for x, y in seg]
    #         poly = Polygon(seg, facecolor='white', edgecolor='black', linewidth=.45)
    #         ax.add_patch(poly)

    # # #%% ---------  Plot bounding boxes for Alaska and Hawaii insets  --------------
    # light_gray = [0.8]*3  # define light gray color RGB
    # x1,y1 = m([-190,-183,-180,-180,-175,-171,-171],[29,29,26,26,26,22,20])
    # x2,y2 = m([-180,-180,-177],[26,23,20])  # these numbers are fine-tuned manually
    # m.plot(x1,y1,color='black',linewidth=0.8)  # do not change them drastically
    # m.plot(x2,y2,color='black',linewidth=0.8)

    x, y = m(lons, lats)
    m.scatter(x, y, s=1, color='blue', marker='o', alpha=0.3)

    plt.savefig(output, dpi=600, bbox_inches='tight')


def main():
    parser = argparse.ArgumentParser(description='Visualize community on a map.')
    parser.add_argument('-i', '--input', dest="input", type=argparse.FileType('r'),
            help='Input file. One IP per line or, if FORMAT set to \'csv\', CSV formatted file ending with latitude and longitude positions',
            default=sys.stdin)
    parser.add_argument('-o', '--output', default='output.png', help='Path to save the file (e.g. /tmp/output.png)')
    parser.add_argument('-a', '--apikey', help='API-KEY from ipstack.com')
    parser.add_argument('-f', '--format', default='ip', choices=['ip', 'csv'], help='Format of the input file.')
    parser.add_argument('-s', '--service', default='f', choices=['f','m'], help='Geolocation service (f=ipstack, m=MaxMind local database)')
    parser.add_argument('-db', '--db', default='./GeoLiteCity.dat', help='Full path to MaxMind database file (default = ./GeoLiteCity.dat)')
    parser.add_argument('--extents', default=None, help='Extents for the plot (west/east/south/north). Default global.')
    args = parser.parse_args()

    output = args.output

    if args.format == 'ip':
        ip_list = get_ip(args.input)
        if args.service == 'm':
            gi = geoip2.database.Reader(args.db)
            lats, lons = geoip_lat_lon(gi, ip_list)
        else:  # default service
            if args.apikey:
                lats, lons = get_lat_lon(args.apikey,ip_list)
            else:
                print("You need the API-KEY!!")
                exit(1)
    elif args.format == 'csv':
        lats, lons = get_lat_lon_from_csv(args.input)

    generate_map(output, lats, lons, wesn=args.extents)


if __name__ == '__main__':
    main()
