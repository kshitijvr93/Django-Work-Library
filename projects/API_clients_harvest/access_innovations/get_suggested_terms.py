# Based on ealdxml
# file: get_suggested_terms.py
# purpose: get suggested terms from access innovations for a given document
# See also: Data Harmony Suite Developer's Guide Version 3.13 and possibly later
#
# This is python 3.5.1 code
#
#Get local pythonpath of modules from 'citrus' main project directory
import sys, os, os.path, platform

def register_modules():
    platform_name = platform.system().lower()
    if platform_name == 'linux':
        modules_root = '/home/robert/'
        #raise ValueError("MISSING: Enter code here to define modules_root")
    else:
        # assume rvp office pc running windows
        modules_root="C:\\rvp\\"
    sys.path.append('{}git/citrus/modules'.format(modules_root))
    return
register_modules()

import sys
import requests
import urllib, urllib.parse
import json
import pprint
from collections import OrderedDict
from io import StringIO, BytesIO
from datetime import datetime
import etl

'''
File: get_suggested_terms.py

This is a Python 3.6 program.

This program is based on ealdxml.py (Elsevier Api Load Date to Xml)

It is based on eatxml (Elsevier Api To Xml), but here revised to query for
original load date rather than pub year, and also revised to create an
output directory for every single day queried for a load date.

'''
from lxml import etree
# Note: Official Python 3.5 docs use different library, ElementTree ET
# Maybe try ET if lxml shows flaws -- update: lxml shows no flaws so far after months
# of use, so sticking with lxml for last part of 2016 and beyond.
import xml.etree.ElementTree as ET
from pathlib import Path
import datetime
import pytz
import os
import urllib.request

utc_now = datetime.datetime.utcnow()
utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")

get_suggested_xml_fmt = '''
<TMMAI project="{project}" location = ".">
<Method name="getSuggestedTerms" returnType="{return_type}"/>
<VectorParam>
<VectorElement>{doc}</VectorElement>
</VectorParam>
</TMMAI>
'''

'''
def get_suggested)terms_data_harmony_api_result()
This does a 'POST' api request and return a 'response' object.

'''

# used https://ocr.space/ on 20180813 from the jpg to get the text
ocrspace_text = '''THE FLORIDA CATTLEMAN
at/ stock
owned by J- Hungerford.
Guzerat Brahman
Cattle
Are Becominé More Popular
Each Year
Why? Because:
3rd.
4th,
6th.
7th.
8th.
They are aclapteqi to our country.
They are quick growing.
They do not suffer from heat.
The cows are good mothers, giving enough rieh
milk to produce a sleek fat calf.
The quality Of ilrahman meat equal to that of
any other breed.
Tite dressing per cent is higher.
They never have pink eye.
They are very prepotent. Having the ability to
transmit the above qualification to any breed
or elass Of cattle.
NOTE: Do not confuse the other breeds of Brah-
man cattle with the Guzerat breed.
OUR SUPPLY OF GUZI'.*RAT BULLS IS EXiiAüST-
WE CAN SUPPLY WITH TWO.YEAR-OLD
BULLS IN THE SPRING OF 1038.
see
O. FLORIDA,
*tate
J. D. HUDGINS
Hungerford -Wharton County, Texas
National Stockyard*
See the anest eatt/e
in e,7/opiola.
G tries Stockmen
ana Mors *.7potn
Sections
S pOtiSOred BY
Plan Now to be in Jacksonville on
March 9 And 10. Two Big Days
e7/oric)a urea/
'''

tesseract_text = '''
ORIDA_CATTLEMAN
Guzerat Hictaee
Cattle
Are Becoming More Popular
Each

Why? Because:
Ist, They are adapted to our country,

2nd. "They are quick growing,

rd. Thay do not sutfor trom heat,

A he sows are ot mother, svg ehh seh
Talk to produce a sleek

Sth The guy of Brhman met is eu to Mat of

other bt

th, The dressing. per cont is higher.

â€˜Th. They never have pink eye.

Sth. They are very prepotent. Having the ability to
transmit the above qualification to any breed
for class of cattle,

NOTE: Do not confuse the other breeds of Brah-
man cattle with the Guzerat breed.

OUR SUPRLY OF GUZERAT BULLS Is EXHAUST.

D. WE WITH TWO-YEAR-OLD

TULL INT GPRING OF Yoos

ew HUDGINS

Hungerford -Wharton County, Texas

Third Annual

Ful Stock Shae

In Jacksonville, Florida

â€˜National Stockyards

March 9 & 10

See the Finest Cattle
Produced in Florida.
Entries by Stockmen
and Club Boys From
All Sections

Sponsored By

Sacksonville Chamber of Commerce
eo

Plan Now to be in Jacksonville on
March 9 And 10, 1937, Two Big Days

"Buy Florida flare"
'''

tesseract_text2 = '''
ORIDA_CATTLEMAN
Guzerat Hictaee
Cattle
Are Becoming More Popular
Each

Why? Because:
Ist, They are adapted to our country,

2nd. "They are quick growing,

rd. Thay do not sutfor trom heat,

A he sows are ot mother, svg ehh seh
Talk to produce a sleek

Sth The guy of Brhman met is eu to Mat of

other bt

th, The dressing. per cont is higher.

â€˜Th. They never have pink eye.

Sth. They are very prepotent. Having the ability to
transmit the above qualification to any breed
for class of cattle,

NOTE: Do not confuse the other breeds of Brah-
man cattle with the Guzerat breed.

OUR SUPRLY OF GUZERAT BULLS Is EXHAUST.

D. WE WITH TWO-YEAR-OLD

TULL INT GPRING OF Yoos

ew HUDGINS

Hungerford -Wharton County, Texas

Third Annual

Ful Stock Shae

In Jacksonville, Florida

â€˜National Stockyards

March 9 & 10

See the Finest Cattle
Produced in Florida.
Entries by Stockmen
and Club Boys From
All Sections

Sponsored By

Sacksonville Chamber of Commerce
eo

Plan Now to be in Jacksonville on
March 9 And 10, 1937, Two Big Days

"Buy Florida flare"
'''

def get_suggested_terms_data_harmony_api_result(
    doc='farming and ranching in Peru', #example from DH Guide v3.13
    #url from email of xxx
    url='http://dh.accessinn.com:9084/servlet/dh',
    project='floridathes', # in 2018 or geothesFlorida'

    #return_type='java.util.String', # error
    return_type='java.util.Vector',

    log_file=sys.stdout,
    verbosity=1):

    me='get_suggested_terms_data_harmony_api_result'
    if doc is None:
        raise Exception("doc document string is required")

    d = ({'doc': doc, 'project':project, 'return_type':return_type, })
    query_xml = get_suggested_xml_fmt.format(**d)

    if url is None or url=="":
        raise Exception("Cannot send a request to an empty url.")
    try:
        # msg="*** BULDING GET REQUEST FOR SCIDIR RESULTS FOR URL='{url}' ***"
        # print(f'msg(url)')
        response = requests.post(url, data=query_xml.encode('utf-8'))
    except:
        raise Exception("Cannot post a request to url={}".format(url))

    #result = json.loads(response.read().decode('utf-8'))

    print(log_file, f'{me} got response encoding="{response.encoding}"'
      .encode('latin-1',errors='replace'))

    print(log_file, f'{me} got response text="{response.text}"'
      .encode('latin-1',errors='replace'))

    return response
# end def get_suggested_terms_data_harmony_api_result

'''
For given url, decode response to utf-8 and return that in a
python 3.6 unicode string
'''

def get_elsevier_api_result_by_url(url):

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
        print("get_elsevier_api_result_by_url: Got exception instead of response for"
              " url={}, get_request={} , exception={}"
              .format(url, get_request, e))
        raise

    #result = json.loads(response.read().decode('utf-8'))
    return response.read().decode('utf-8')

'''
Method: get_elsevier_api_uf_query_url_by_dates(d_run_params, verbosity):

Given d_run_params with required key values:
 cymd-start is start date to use for orig-load-date
 cymd-end is end date to use
 api-key is uf api key

Return the url string that represents an api search query with the given params,
suitable to submit as an Elsevier Search API url/query.

'''
def get_elsevier_api_uf_query_url_by_dates(d_run_params, verbosity):
    '''
    Caller provides a bef-aft day range to search Elsevier for UF-affiliated articles.
    The result data is returned.
    '''
    # Empricial testing shows that to get orig-load-date of say 20160315, one
    # must set cymd_bef to 20160314 and cymd_aft to 20160316. That is, both
    # params bef and aft are
    # not inclusive.
    cymd_bef = d_run_params.get('cymd-bef')
    cymd_aft = d_run_params.get('cymd-aft','')
    api_key = d_run_params.get('api-key', '')

    # Set this param here, some others below , not in incoming d_run_params,
    # because if they change, this is the natural method to make the changes
    search_http_accept = "application/xml"

    query = (
      "aff(university of florida) and orig-load-date aft {} "
      "and orig-load-date bef {}"
      .format(cymd_bef, cymd_aft))

    search_base_url = "https://api.elsevier.com/content/search/scidir"

    d_qparams = {
        "query":query,
        # "http_accept":http_accept, #incorrect name was in orig Els doc attached in sep 2015 email...
        "httpAccept": search_http_accept,
        "apikey":api_key,
    }
    api_get_qparams = urllib.parse.urlencode(d_qparams)

    # print(" *** *** *** Using get_params='{}' *** *** ***".format(get_qparams))
    d_run_params.update ({
        'search-base-url': search_base_url,
        'search-http-accept': search_http_accept,
        'search-query': query,
        })

    search_api_url = "{}?{}".format(search_base_url, api_get_qparams)

    return search_api_url
# end def get_elsevier_api_uf_query_url_by_dates()

#Given a REQUEST'S header lines, make a dictionary of key value pairs
def headers2dict(header_lines):
    lines = header_lines.splitlines(False)
    headers = {}
    for line in lines:
        parts = line.split(":")
        if len(parts) == 2:
            headers[parts[0]] = parts[1]
    return headers

'''
Method result_entries_collect(d_params, results_tree, d_batch, verbosity=1, scopus_uf_check=1):

Given d_params dictionary with required keys:
api-key,
host-output-directory,
out-cymd,

and also given and an article search results page's xml tree of metadata, loop over the \
tree's entries (usually 25 in number), where each entry is for a result article,

(SEARCH OUTPUT FILES)
We save each entry in file entry_{pii}.xml, and we query the 'full-text' xml api from Elsevier.

{FULL OUTPUT FILES)
We write a 'full-text-results' xml file named pii_{pii_norm_text}.xml in the output dir
for each entry/article.

Note: we also could add a dictionary argument used to track incoming pii values
and reject duplicate pii values across calls here during processing the results
of a query, but that has not been a problem (so far).

RETURN values: batch_entries_collected, link_next_batch

'''
def result_entries_collect(d_params, results_tree, d_batch, verbosity=1, scopus_uf_check=1):

    me = 'result_entries_collect'
    api_key = d_params.get('api-key', "")
    out_base_dir = d_params.get('host-output-directory','')
    cymd_day = d_params['cymd-day'] # this is used to derive sub-folders for output
    parts = cymd_day.split('-')
    output_dir = '{}/{}/{}/{}'.format(out_base_dir, cymd_day[0:4],cymd_day[4:6], cymd_day[6:8])
    os.makedirs(output_dir, exist_ok=True)

    #entry_tag = '{http://www.w3.org/2005/Atom}entry' # could use this instead of '{*}entry' used below.
    result_link_next = ""

    result_root = results_tree.getroot()
    for link in results_tree.findall('{*}link'):
        d_attrib = dict(link.attrib)

        # parse out the link that will return the results tree for the next batch of results of this query.
        if d_attrib.get("ref", "") == "next":
            result_link_next = d_attrib.get("href","")
            # print("results_entries_collect: result_link_next='{}'".format(result_link_next))

    l_retrievals = []
    d_batch['full-retrieval-result'] = l_retrievals
    n_entry = 0
    n_entry_exceptions = 0
    for i,entry in enumerate(results_tree.findall('.//{*}entry')):
        # We have the next root entry element in the results tree.
        n_entry += 1
        d_results = {}
        #print("\n\n*** USING n_entry={}, entry={}".format(n_entry, entry.text))
        # tree_entry = etree.ElementTree(entry)
        pii = entry.find('{*}pii')
        pii_norm_text = pii.text.replace('(','').replace(')','').replace('-','').replace('.','')
        if verbosity > 0:
            print ("***** Entry={}, pii={}, pii_norm={}".format(n_entry, pii.text, pii_norm_text))
        #if scopus_uf_check:
            #TODO: check that this PII value is in scopus with affilname="University of Florida"
            #a_name, a_city, a_country = scopus_affilname_by_pii(pii_norm_text)
            # TODO: add a folder, 'nonuf', sibling to folder full to put xml output for nonuf articles.
        # Save the xml subtree for this entry into a separate xml file
        if 1 == 2:
            # these files get produced ok, but I do not use them now and they
            # take up a bit of space so comment them out now. Maybe restore later
            entry_xml_str = etree.tostring(entry, pretty_print=True)
            out_filename = '{}/entry_{}.xml'.format(output_dir, pii_norm_text)
            with open(out_filename, 'wb') as outfile:
                outfile.write(entry_xml_str)

        # print("ENTRY_XML_STR={}".format(xml_str))
        full_filename = '{}/pii_{}.xml'.format(output_dir, pii_norm_text)
        for link in entry.findall('{*}link'):
            d_attrib = dict(link.attrib)
            # print("Link d_attrib = {}".format(repr(d_attrib)))
            if d_attrib.get("ref", "") != "self":
                continue

            # Use this entry's self-link value to parse pii and compose and issue a full-text
            # API textxml retrieval,
            # and save the xml into a file under out_base_dir
            # into a .xml output file for the downstream extmets process to convert to a mets file
            # for SobekCM Builder to build.

            # From search entry 'self' link's href, create url_fulltext for API request
            ft_link_base = d_attrib.get("href","")
            # It is not expected for pii calculation to not equal pii_norm_text,
            # but just in case, use pii parsing.
            pii = ft_link_base.split('/')[-1]
            d_results['pii'] = pii
            d_results['result'] = 'success'
            # Do not waste d_results-copied log space with url string unless a failure
            url_fulltext = ('{}?httpAccept=text/xml&apikey={}'
                .format(ft_link_base, api_key))

            # print("Making request for FULL-TEXT API URL url_fulltext={}".format(url_fulltext))
            try:
                # print("Full-Text API request URL='{}' ***".format(ur_fulltext))
                get_request = urllib.request.Request(url_fulltext)
            except Exception as e:
                d_results['result'] = 'failure'
                d_results['exception-message'] = repr(e)
                d_results['message-nature'] = (
                    "Exception in urllib.request.Request({})".format(url_fulltext))
                l_retrievals.append(d_results)
                n_entry_exceptions += 1
                continue

            # Get Response for that request.
            try:
                response = None
                response = urllib.request.urlopen(get_request)

            except urllib.error.HTTPError as e:
                # The except HTTPError must come first, otherwise except URLError will also catch an HTTPError.
                # Not too useful.. this info is also in the exception message, repr(e)
                if not hasattr(e, "code"):
                    e.code = "None"
                if hasattr(e, "reason"):
                    d_results['exception-reason'] = e.reason
                if response:
                    # Response can be non-null for some HTTPError exceptions, so show it.
                    d_results['response-content'] = response.content
                    d_results['response-error-read'] = response.read().decode('utf-8')
                    d_results['response-reason'] = response.reason
                else:
                    # Later we could parse this e,read() xml stream and pretty it for
                    # the run log output, but not needed now.
                    d_results['response-error-read'] = e.read().decode('utf-8')

                if hasattr(e, "headers"):
                    str_headers = e.headers.as_string()
                    #print("e.headers='{}'".format(str_headers))
                    d_headers = headers2dict(str_headers)
                    #print("d_headers='{}'".format(d_headers))
                    #d_results['headers'] = str_headers
                    # Maybe add more header types of interest to this list
                    for header in ['X-ELS-Status']:
                        d_results[header] = d_headers.get(header,"None")
                    # print("HEADER TYPE FOR ERROR", str(type(e.headers)))

                d_results['exception-code'] = e.code
                d_results['url'] = url_fulltext
                d_results['result'] = 'failure'
                d_results['exception-message'] = repr(e)
                d_results['exception-get-url'] = e.geturl()
                d_results['exception-info']    = e.info()
                l_retrievals.append(d_results)
                n_entry_exceptions += 1
                continue
            except urllib.error.URLError as e:
                d_results['exception-message'] ='We failed to reach a server.'
                d_results['exception-reason'] = e.reason
                l_retrievals.append(d_results)
                n_entry_exceptions += 1
                continue

            try:
                #l_retrievals.append(d_results)
                #continue; #remove when finishing testing test this try...except

                # Send the Full-text API request for this pii in url_fulltext, and receive
                # and parse the XML RESPONSE into lxml tree object 'ft_tree'.
                # ft_tree = etree.parse(url_fulltext)

                ft_tree = etree.parse(StringIO(response.read().decode('utf8')))

                # The Full text result's xml tree may specify a service-error failure message
                nodes = ft_tree.findall('.//{*}service-error')
                if not nodes:
                    nodes = ft_tree.findall('.//{*}status')
                if not nodes:
                    nodes = ft_tree.findall('//status')
                # if nodes and len(nodes) > 0:
                if nodes:
                    service_error = nodes[0]
                    # full-retrieval fails with service-error
                    status_text = service_error.find('{*}statusText')
                    msg_text = status_text.text if status_text else "None"
                    msg_code = service_error.find('{*}statusCode') if status_code else "None"

                    d_results['pii'] = pii
                    d_results['status-text'] = msg_text
                    d_results['status-code'] = msg_code

                    n_entry_exceptions += 1
                    print("got service-error: and pii={},error={}".format(pii,emsg))
                else:
                    # We got an ft_tree and found no service_errors, so presumably OK.
                    d_results['pii'] = pii
                    d_results['result'] = 'success'

                l_retrievals.append(d_results)

            except Exception as e :
                # lxml parser threw exception..
                d_results['result'] = 'failure'
                d_results['error-message'] = repr(e)
                d_results['pii'] = pii
                d_results['parser-exception'] = 'here'

                l_retrievals.append(d_results)
                n_entry_exceptions += 1
                continue;

            # Put the FT xml response to a serialized string
            try:
                full_xml_str = etree.tostring(ft_tree.getroot(), pretty_print=True)

                # Save this entry's full text xml
                with open(full_filename, 'wb') as outfile:
                    outfile.write(full_xml_str)
            except Exception as e:
                n_entry_exceptions += 1
                print("Skipping bad full_xml_str....")
                continue;

            # end if link has ref='self'
        # end for each link ()
    # end foreach entry

    return result_link_next, n_entry, n_entry_exceptions, l_retrievals
# end result_entries_collect()

'''
Method ealdxml: Elsevier Api Load Date to XML - Read the Elsevier Search API for UF-Authored
articles and use the 'self' link URL along with the api_key to get XML Metadata
for each Elsevier article and save it to a file named pii_{pii}.xml under the
given output directory.

Params cymd_lo and hi are load date ranges for the search API use to select
which articles for which to return metadata.
'''
def ealdxml(d_params, verbosity=0):
    #
    # VALIDATE d_params
    # key 'cymd-start' has value of the first orig-load-date that we want to collect
    # key 'cymd-end' has value of the last orig-load dates that we want to collect
    me = 'ealdxml'
    dt_day = datetime.datetime.strptime(d_params['cymd-start'],'%Y%m%d')
    dt_end = datetime.datetime.strptime(d_params['cymd-end'], '%Y%m%d')
    day_delta = datetime.timedelta(days=1)

    dt_bef = dt_day - day_delta
    dt_aft = dt_day + day_delta
    total_results = 0

    output_articles = 0
    entries_collected = 0
    entries_excepted = 0
    # Collect results for all entries in this search query result response
    d_batches = dict()
    d_params.update({"batches": d_batches})

    d_batch = dict()
    n_batch = 1

    while dt_day <= dt_end:
        day = dt_day.strftime('%Y%m%d')
        d_params['cymd-day'] = day
        d_params['cymd-bef'] = dt_bef.strftime('%Y%m%d')
        d_params['cymd-aft'] = dt_aft.strftime('%Y%m%d')

        url_search = get_elsevier_api_uf_query_url_by_dates(d_params, verbosity)

        # Get results tree directly from the parse() method that does its own API
        # request for url_search_results
        #print ("***** Making l_tree from API search URL={}".format(url_search))

        try:
            # Note: Per lxml docs, tree is an ElementTree object, and 'root' is an element object.
            results_tree = etree.parse(url_search)
        except Exception as e:
            print("{}: cannot parse initial search results. e='{}'".format(me,repr(e)))
            continue

        # print("RESULTS XML={}".format(etree.tostring(results_root, pretty_print=True)))

        # Below we just use the source document's namespace definitions (may take a bit more time
        # than setting it as a constant here by copy-pasting a sample set of namespaces -
        # but some xml files on input may vary, so why take a chance?)

        # Note: The root element, though it may have attribute-looking xmlns map assignments, they are
        # xml qualifiers, and not attributes, so we must use root.nsmap to get them, rather than root.attrib.

        # We may check this dict in future code, too, to see if it satisfies future required namespaces.

        # Next line strips out the default value that has None as a key, because such an item chokes
        # downstream calls to my_elt.find() calls, probably other methods too, on 20160307.
        results_root = results_tree.getroot()
        d_ns = {key:value for key,value in dict(results_root.nsmap).items() if key is not None}

        #print ("***** using namespaces in dict={}".format(d_ns))
        day = dt_day.strftime('%Y%m%d')
        print ("\n***** {}:For DAY={}, Starting with batch={}, making initial results_tree for url_search = {}"
               .format(me,day,str(n_batch), url_search))
        n_results = int(results_tree.find('.//opensearch:totalResults', namespaces=d_ns).text)
        print("This day's NUMBER OF SEARCH RESULT ENTRIES = {} *****" .format( n_results))
        total_results += n_results

        if n_results > 0:
            while (1==1):
                batch_key = 'b'+ str(n_batch).zfill(5)
                d_batches[batch_key] = d_batch
                print ("Batch={}, Processing results_tree from url_search = {}".format(str(n_batch), url_search))

                # PROCESS THE SEARCH RESULTS ENTRY DATA GIVEN IN results_tree FOR THIS BATCH OF ARTICLES
                url_search, n_collected, n_excepted, l_retrievals = (
                    result_entries_collect(
                        d_params, results_tree, d_batch)
                    )
                entries_collected += n_collected
                entries_excepted += n_excepted

                d_batch['n_entries_collected'] = str(n_collected)
                d_batch['n_entries_excepted'] = str(n_excepted)

                print ("Total entries_collected so far = {}, exceptions = {}"
                       .format(str(entries_collected), str(entries_excepted)))
                if (not url_search or url_search ==''):
                    break
                n_batch += 1
                print ("Batch={}, Making results_tree for url_search = {}".format(str(n_batch), url_search))
                try:
                  results_tree = etree.parse(url_search)
                except ParseError:
                  print("{}: ERROR: Cannot parse results tree from result of url_search={}"
                        .format(me,url_search))
                  raise
                # end loop over batches of this day's query
            # end n_results > 0
        #set up for next day's query
        dt_day += day_delta
        dt_bef += day_delta
        dt_aft += day_delta
    # end collection while dt_day <= dt_end

    d_params.update({
        'total-result-entries': "0" if not total_results else str(total_results),
        })

    d_stats = dict()
    d_params.update({"stats": d_stats})
    d_stats['total_entries_collected'] = str(entries_collected)
    d_stats['total_entries_excepted'] = str(entries_excepted)
    return entries_collected, entries_excepted
#end def ealdxml()

####### RUN main EALDXML program
def runold():

    # PARAMETERS -- set these manually per run for now... but only cymd_start
    # and cymd_end would normally change.
    # See the current output directory and identify missing date ranges of interest
    # that you want to collect. Otherwise if you want to re-collect, possibly to get updates from
    # elsevier, set cymd_start and cymd_end to already-extand dates in the output structure.
    # CAUTION: files of those dates will be overwritten, so save older ones if desired.
    #
    cymd_start = '20161212'
    # cymd_end = '20160206'
    cymd_start = '20170209'
    cymd_start = '20170817'
    # EALDXML - Here, we do only one day at a time...
    cymd_end = '20170824'
    cymd_start = '20170825'
    cymd_end = '20180102'
    print("TEST SETTING: cymd_start={},cymd_end={}"
          .format(cymd_start,cymd_end))

    worker_threads = 1 # TODO
    # WARNING: now hardcoded, and later we may condsider to get these by programmatic introspection
    agent_creator_individual = 'UFAD\lib-adm-podengo'
    agent_creator_host = 'UFLIBSHGKDND2.ad.ufl.edu'
    agent_creator_software = "ealdxml-0.2" #may add attributes programming-language, revision-date, hash ...
    # Elsevier-Dave Santucci Jan 2015 gave UF this api_key = "d91051fb976425e3b5f00750cbd33d8b"
    api_key = 'd91051fb976425e3b5f00750cbd33d8b'
    verbosity = 0

    out_base_dir = etl.data_folder(linux='/home/robert/', windows='U:/',
          data_relative_folder='data/elsevier/output_ealdxml/')
    #out_base_dir = 'c:/rvp/elsevier/output_ealdxml'

    # create output directory root if it does not exist
    os.makedirs(out_base_dir, exist_ok=True)

    # make other output directories (hardcoded now here and in eatxml())
    for sub_name in ['entry', 'full','run']:
        os.makedirs('{}/{}'.format(out_base_dir,sub_name), exist_ok=True)

    utc_now = datetime.datetime.utcnow()
    # secsz_start: secz means seconds in utc(suffix 'z') when this run started
    secsz_start = utc_now.strftime("%Y-%m-%dT%H-%M-%SZ")

    print ("START EALDXML RUN at {}\n\twith:\ncymd_start='{}', cymd_end='{}'\n  "
           "outbase_dir={},verbosity={}"
           .format(secsz_start, cymd_start, cymd_end, out_base_dir, verbosity))

    if (cymd_end != ''):
        api_search_query = (
          "aff(university of florida) and orig-load-date aft {} and orig-load-date bef {}"
          .format(cymd_start, cymd_end))
    else:
        api_search_query = (
          "aff(university of florida) and orig-load-date aft {}"
          .format(cymd_start))

    # Dict of metadata run parameter info on this run
    d_params={
        "secsz-start": secsz_start,
        "cymd-start" : cymd_start,
        "cymd-end"   : cymd_end,
        "host-output-directory" : out_base_dir,
        "agent-creator-individual" : agent_creator_individual,
        "agent-creator-software" : agent_creator_software,
        "agent-creator-host" : agent_creator_host,
        "python-version" : sys.version,
        "api-key" : api_key,
        "worker-threads-count" : int(worker_threads),
        "api-search-query" : api_search_query,
        "max-output-articles" : "0", # TODO
        }

    # Process the Elsevier Search and Full-Text APIs to create local xml files
    entries_collected = 0
    entries_excepted = 0

    ###### MAIN CALL TO EATXML() ########

    if (1 == 1): # test with or without call to eatxml
        entries_collected, entries_excepted = ealdxml(d_params, verbosity=verbosity)

    ############### WRAP-UP OUTPUT ################

    # Also record some summary output results in d_params for saving as xml file
    #
    utc_now = datetime.datetime.utcnow()
    secsz_end = utc_now.strftime("%Y-%m-%dT%H-%M-%SZ")

    d_params.update({
        "total-entries-collected" : entries_collected,
        "total-entries-excepted" : entries_excepted,
        "secsz-end" : secsz_end,
        # Prevent actual api-key value from being stored in the output
        "api-key" : '*UF-Smathers Proprietary*'
        })

    # Write out the run parameters.
    e_root = etree.Element("uf-api-harvest")
    etl.add_subelements_from_dict(e_root, d_params)

    out_filename = '{}/run/run_ealdxml_{}.xml'.format(out_base_dir, secsz_start)
    with open(out_filename, 'wb') as outfile:
        outfile.write(etree.tostring(e_root, pretty_print=True))

    ########### IMPORTANT - MANUALLY DO IMMEDIATELY AFTER A RUN...!!  *#############

    # (Later Add code here to do it) but now do manually in a terminal window cd'ed to the out_base_dir
    # $git add -A .; git commit -m "<secsz_start>xxxx</secsz-start>"
    # where secsz start is found in the out_filename file.

    '''
        # TODO:
        # The code can require that the output_base_dir is a git repo, because that is the plan.
        # We can add code to invoke an OS-level command
        # "git commit -ma? 'secz_start={secz_start}'.format(secsz_start)" command near the end
        # of this program, before exiting.
        # Then we can manually query the git log to get the git commit hash value for any secz_start,
        # or list all the secz_start commits, etc.
        # Then with the git hash value we can issue git commands to see what exactly changed in the
        # output_base_dir as a result of any run of this code, identified by secsz_start.
        # A reporting program can be written to do that work, of course.
        # This way we can track changes in the
        # API results, as they evolve or get broken or enhanced by outside providers.
    '''
    print("Done")

#end def runold

def run():
    import html
    doc = ocrspace_text
    doc = etl.escape_xml_text(tesseract_text)
    project = 'floridathes'
    r = get_suggested_terms_data_harmony_api_result(project=project, doc=doc)
    project = 'geothesFlorida'
    r = get_suggested_terms_data_harmony_api_result(project=project, doc=doc)

run()
