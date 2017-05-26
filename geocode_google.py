#
'''
Program google_geocode...
will overwrite the following base code...

sample request
https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=AIzaSyCbZioqtuHzsMKBogNaYhR9Iw2KsbjPr-g
'''

from lxml import etree
import datetime
import requests
import json

api_key='AIzaSyCbZioqtuHzsMKBogNaYhR9Iw2KsbjPr-g'

d_r = {
    'url': 'https://maps.googleapis.com/maps/api/geocode/json?',
    'd_headers' : {'Content-Type' : 'application/json', },
    # get params
    'key': api_key,
    'address': '1600+Amphitheatre+Parkway,+Mountain+View,+CA'

    }

addresses = ['lee county,FL','alachua county, FL','alachua, FL', 'lakeland,FL', 'orlando,fl', 'orange county,fl']
#counties=['lee']
for address in addresses:
    d_r['address'] = "{} county,{},USA".format(county,"FL")
    url ="{url}address={address}&key={key}".format(**d_r)
    print("url = '{}'".format(url))
    jr = requests.get(url)
    r = json.loads(jr.text)
    print(repr(r))
    data = r["results"][0]
    status = r['status']

    print("Results status='{}'".format(status))
    lat = data['geometry']['location']['lat']
    lng = data['geometry']['location']['lng']
    print ("lon={},lat={} for {}".format(lat,lng,address))
