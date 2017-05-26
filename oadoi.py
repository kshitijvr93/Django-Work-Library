import os
import sys
print("Using python sys.version={}".format(sys.version))

import requests
import urllib.parse
import json
from lxml import etree
from lxml.etree import tostring
from collections import OrderedDict
###

import  http.client

http.client.HTTPConnection._http_vsn = 10
http.client.HTTPConnection._http_vsn_str = 'HTTP/1.0'

#print urllib2.urlopen('http://localhost/').read(

####################################################
doi_string = '''
10.1115/ICONE24-60736
'''
doi_string = '''
10.1120/jacmp. v17i4.5965
10.1123/jsm.2015-0230
10.1123/jsm.2015-029
10.1126/science.aaf7671
10.1126/scisignal.aaf6670
10.1130/L539.1
10.1136/bcr-2016-216612
10.1136/bjsports-2016-096895
10.1145/2976749.2978396
10.1145/2976749.2978398
10.1152/jn.01067.2015
10.1158/1078-0432.CCR-16-0985
10.1159/000451054
10.1161/CIRCINTERVENTIONS.116.004395
10.1161/CIRCULATIONAHA.116.023164
10.1161/CIRCULATIONAHA.116.024870
10.11646/zootaxa.4107.3.11
10.11646/zootaxa.4189.3.4
10.1177/0142723716673956
10.1177/1742395316648748
10.1177/2048872615624849
10.1186/s12909-016-0819-6
10.1186/s13073-016-0376-y
10.1186/s40168-016-0163-4
10.1214/16-EJS1201
10.1227/NEU.0000000000001447
10.1371/journal.pone.0164722
10.1371/journal.pone.0166803
10.1371/journal.pone.0166872
10.1386/tear.14.3.197_1
10.1534/g3.116.034785
10.1634/theoncologist.2016-0148
10.18520/cs/v111/i9/1500-1506
10.2105/AJPH.2016.303443
10.2146/ajhp150946
10.2146/ajhp160046
10.2146/ajhp160104
10.2174/1385272820666160805113749
10.2174/1570162X14666160720093851
10.3122/jabfm.2016.06.160138
10.3168/jds.2016-11238
10.3168/jds.2016-11537
10.3168/jds.2016-11566
10.3168/jds.2016-11727
10.3389/fphys.2016.00480
10.3390/insects7040061
10.3390/insects7040062
10.3847/0004-637X/832/1/18
10.3847/0004-637X/832/1/37
10.3847/0004-637X/832/1/95
10.3945/jn.116.237495
10.3965/j.ijabe.20160905.2091
10.3978/j.issn.2078-6891.2015.071
10.5423/PPJ.OA.05.2016.0131
'''

l_dois = doi_string.split('\n')
print(len(l_dois))

'''Method add_subelements():
Generic logging utility helper:
Given an lxml element, add subelements recursively from nested python data structures
This may be used to generate xml log files, however, it can take up too much core if used to
report per-input-file messages, and if so, it may be
better to disable for 'big' batches of xml files to convert, or break up to create multiple log files.
'''
def add_subelements(element, subelements):
    if isinstance(subelements, dict):
        d_subelements = OrderedDict(sorted(subelements.items()))
        for key, value in d_subelements.items():
            # Check for valid xml tag name:
            # http://stackoverflow.com/questions/2519845/how-to-check-if-string-is-a-valid-xml-element-name
            # poor man's check: just prefix with Z if first character is a digit..
            # the only bad type of tagname found ... so far ...
            if key[0] >= '0' and key[0] <= '9':
                key = 'Z' + key
            try:
                subelement = etree.SubElement(element, key)
            except Exception as e:
                print("Skipping etree.SubElement error='{}' for key='{}'"
                     .format(e,key))
                continue
            add_subelements(subelement, value)
    elif isinstance(subelements, list):
        # Make a dict indexed by item index/count for each value2 in the 'value' that is a list
        for i, value in enumerate(subelements):
            subelement = etree.SubElement(element, 'item-{}'.format(str(i+1).zfill(8)))
            add_subelements(subelement, value)
    else: # Assume it is a string-like value. Just set the element.text and do not recurse.
        element.text = str(subelements)
    return True
# end def add_subelements()

def get_result_by_url(url):

    if url is None or url=="":
        raise Exception("Cannot send a request to an empty url.")
    try:
        print("*** BULDING GET REQUEST FOR SCIDIR API RESULTS FOR URL='{}' ***".format(url))
        get_request = urllib.request.Request(url, data=None, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            })

    except:
        raise Exception("Cannot send a request to url={}".format(url))
    try:
        print("*** GET REQUEST='{}' ***".format(repr(get_request)))
        response = urllib.request.urlopen(get_request)
    except Exception as e:
        print("get_elsevier_api_result_by_url: Got exception instead of response for"
              " url={}, get_request={} , exception={}"
              .format(url, get_request, e))
        raise

    result = json.loads(response.read().decode('utf-8'))
    return result

def output_oadoi_xml(url_base=None, dois=None, output_folder=None):
    if not all([url_base, dois, output_folder]):
        raise Exception("Bad args")

    for i,doi in enumerate(dois):
        if doi is None or doi == '':
            continue
        # Some dois from scopus have illegal embedded spaces - just remove them for now
        url_request = '{}/{}'.format(url_base,doi).replace(' ','')
        print("Using url_request='{}'".format(url_request))
        d_result = get_result_by_url(url_request)

        #print("Got d_result='{}'".format(repr(d_result)))
        d_entry = d_result['results'][0]
        print("\n\nGot d_entry='{}'\n".format(d_entry))

        # Save the xml as a string
        node_root = etree.Element("entry")
        add_subelements(node_root, d_entry)

        #Now get doi value and normalize it to filename prefix characters
        node_doi = node_root.find('./{*}doi')
        print("-------------GOT DOI TEXT='{}'------------------".format(node_doi.text))
        norm_doi = node_doi.text.replace('/','_')
        out_filename = '{}/oadoi_{}.xml'.format(output_folder,norm_doi)
        with open(out_filename, mode='w', encoding='utf-8') as outfile:
            pretty_log = etree.tostring(node_root, pretty_print=True)
            outfile.write(pretty_log.decode('utf-8'))
        #end doi loop
    return

output_folder = 'c:/rvp/elsevier/output_oadoi'
os.makedirs(output_folder, exist_ok=True)
url_base =  'http://api.oadoi.org'

dois = doi_string.split('\n')
output_oadoi_xml(url_base=url_base,dois=dois, output_folder=output_folder)
print("Please see output xml files under folder {}. Done!".format(output_folder))
