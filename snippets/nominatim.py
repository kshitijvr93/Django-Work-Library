#geocode_nominatim
# see http://wiki.openstreetmap.org/wiki/Nominatim
from lxml import etree
import datetime
import requests
import json
d_geo_request = {
    'url': 'http://nominatim.openstreetmap.org/search',
    'd_headers' : {'Content-Type' : 'application/json', },
    'city' : 'Gainesville',
    'state': 'Florida',
    'country' : 'USA',
    'email' : 'podengo@ufl.edu',
    'format': 'json',
    'limit': 10,
    'url_geo_format' : ('{url}?city={city}&county={county}&state={state}'
                        '&country={country}&format={format}')
    }
places = ['valencia,,,spain',',,FL,USA', 'lakeland,,FL,USA'
    , ',lee,fl,USA', ]
#counties=['lee']
for place in places:
    parts = place.split(',')
    format = 'json'
    format = 'xml' #both work... not sure if the backslashes in this output are useful?
    format = 'json'
    d_geo_request['format'] = format
    d_geo_request['city'] = parts[0]
    d_geo_request['county'] = parts[1]
    d_geo_request['state'] = parts[2]
    d_geo_request['country'] = parts[3]
    url = d_geo_request['url_geo_format'].format(**d_geo_request)
    print("\nURL={}".format(url))
    r = requests.get(url)
    if format == json:
        jr = json.loads(r.text)
        print("\nJSON RESULT FOR Place={}:".format(place))
        print(repr(jr.text))
    else:
        print("\nXML result for place={}:".format(place))
        print(repr(r.text))
