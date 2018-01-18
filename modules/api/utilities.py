import urllib, urllib.parse
'''
For given url, send it, decode response to utf-8 and return it.
'''
def get_api_result_by_url(url=None, verbosity=None):
    me = "get_api_result_by_url"

    if url is None or url=="":
        raise Exception("Cannot send a request to an empty url.")
    try:
        # print("*** BULDING GET REQUEST FOR SCIDIR API RESULTS FOR URL='{}' ***".format(url))
        get_request = urllib.request.Request(url)
    except:
        raise Exception("Cannot send a request to url={}".format(url))
    try:
        # print("*** GET REQUEST='{}' ***".format(repr(get_request)))
        response = urllib.request.urlopen(get_request)
    except Exception as e:
        print("{}: Got exception instead of response for"
              " url={}, get_request={} , exception={}"
              .format(me, url, get_request, e))
        raise

    #result = json.loads(response.read().decode('utf-8'))
    return response.read().decode('utf-8')
