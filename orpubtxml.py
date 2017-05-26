'''
20170502 program orpubtxml (ORchid PUBlic records To XML)

Program orpubtxml queries the orcid public api for all public record holders with a UF
affiliation,
then it reads the api for the public information for each record holder (identified by orcid id value)
and outputs each record holder's info to the given output directory with a file
name of the form orcid_<orcid id value>.xml.

Program orpubtxml is designed and works similarly to the elsevier ealdxml program in that
(1) it first uses search API to get ids for records of interest,
(2) and for each, it uses a second API to to get more detailed info pertaining to the id,
(3) and then it saves individual xml files, one per id, in an output folder.

That output is meant to be processed by xml2rdb using study name 'orpub' (see xml2rdb code),
which produces related tables in a relational database.

'''

import requests
import json
import urllib
import sys
d_orcid = {}
'''
d_orcid holds the key information used to make requests of the orcid search and detailed record apis
'''
d_orcid = {
    'pub_search': {
        'd_request_headers': {
            'Authorization' : 'Bearer c32ea2ba-0efc-45db-b771-eb793879b232', #public search token
            'Accept' : 'application/vnd.orcid+xml',
        },
        'url_base': 'https://pub.orcid.org/v2.0/search/',
        'start_item_count': 0,
        'result_item_quantity_max': 200, # Max per ORCID docs is 200 ao 20170503
        # See ORCID docs on the solr_query_string options, field and variable names.
        # This is part of a GET URL, so use the %22 and + and any other applicable url-encodings
        'solr_query_string': 'affiliation-org-name:%22University+of+Florida%22',
        'url': '', #Do not edit - just a placeholder, a method will compute this
    },
    'pub_record': {
        'd_request_headers': {
            'Authorization' : 'Bearer c32ea2ba-0efc-45db-b771-eb793879b232',
            'Accept' : 'application/vnd.orcid+xml',
        },
        'url_format': 'https://pub.orcid.org/v2.0/{}/record',
        # Consider:'d_format': {'orcid_id':'',} #User fills in d_format values for str.format_map()
        'url': '', #Do not edit - just a placeholder, a method will compute this
    },
}

'''    Initial Orcid Project parameters, 20170501, used to gain client id, secret and then
    a /read-public access token:

    Orcid ID: Personal Orcid ID of Robert Vernon Phillips
    Name: Journal of Podengos
    Website: https://robertvernonphillips.com
    Redirect URIs: https://developers.google.com/oauthplayground

    Received upon submitting the proect parameters register an application to ORCID on 20170501:

    CLIENT ID: APP-FVQZJZUJ9FX3FO35
    CLIENT SECRET: d61ee138-4da7-40a5-9f32-3410ad88da0a
    Testing tools: Google OAuth2.0 Playground
'''

client_id = 'APP-FVQZJZUJ9FX3FO35'
client_secret = 'd61ee138-4da7-40a5-9f32-3410ad88da0a'

def orcid_production_get_search_token(client_id=None,client_secret=None, scope="/read-public"):
    if client_id is None or client_secret is None or scope is None:
        raise ValueError('get_search_token: client_id or client_secret or scope is None')
    scopes = ['/read-public', '/webhook', '/read-limited','/authenticate']
    if scope not in scopes:
        raise ValueError("Argument scopes must be in '{}'".format(repr(scopes)))
    # request a search token
    '''
    https://sandbox.orcid.org/oauth/token
    HEADER: accept:application/json
    DATA:
      client_id=[Your client ID]
      client_secret=[Your client secret]
      grant_type=client_credentials
      scope=/read-public
    '''
    d_header = { 'accept': 'application/json'}
    d_payload = {
        'client_id' : client_id,
        'client_secret' : client_secret,
        'grant_type' : 'client_credentials',
        'scope' : '/read-public',
    }
    # Orcid oauth urls: https://members.orcid.org/api/oauth/3-legged-oauth
    # sandbox_url = "https://sandbox.orcid.org/oauth/token"

    production_orcid_oauth_exchange_url = 'https://orcid.org/oauth/token'
    url = production_orcid_oauth_exchange_url
    r = requests.post(url, headers=d_header, data=d_payload)
    return r
    #
'''r = orcid_production_get_search_token(
        client_id=client_id,
        client_secret=client_secret, scope='/read-limited')

print("r.json()".format((r.json())))
print("r.text={}".format(r.text))

#I ran that once to get the access_token that I should use for 20 years, hard coded below:
'''

'''
See URL about the search api: https://members.orcid.org/api/tutorial/search-orcid-registry

r.text={"access_token":"c32ea2ba-0efc-45db-b771-eb793879b232",
"token_type":"bearer","refresh_token":"06f6c277-1de9-4ea0-b41a-da321daee23c",
"expires_in":631138518,"scope":"/read-public","orcid":null}
'''

'''
method add_curl_command
create curl command line from info in d_request
useful for diagnostic output.
Store it in d_request['curl_command']
'''
def add_curl_command(d_request):
    curl_options = 'curl -i '
    for key,val in d_request['d_request_headers'].items():
        curl_options += '-H "' + str(key) + ':' + str(val) + '" '
    d_request['curl_command'] = curl = curl_options + '"' + d_request['url'] +'"'
    #print("Curl={}".format(curl))
    return
#d = {"access_token":"c32ea2ba-0efc-45db-b771-eb793879b232"}
#access_token = d['access_token']
# print("Using access_token, aka search token={}".format(access_token))

def response_of_orcid_search(d_search, verbosity=0):
    me = "response_of_orcid_search"
    if d_search is None:
        raise(ValueError,"d_search is required")
    if verbosity != 0 :
        print("{}:Starting".format(me))
    d_headers = d_search['d_request_headers']
    if d_search['solr_query_string'] is None:
        # We store this default in the dictionary to output diagnostic info for exceptions
        d_search['solr_query_string'] = 'affiliation-org-name:%22University+of+Florida%22'
    q = d_search['solr_query_string']
    start_item_count = d_search['start_item_count']
    if start_item_count is None or start_item_count < 1:
        start_item_count = 1
    result_item_quantity_max = d_search['result_item_quantity_max']
    url_base = d_search['url_base']

    # Orcid starts its result item numbering at 1
    # See examples at: https://members.orcid.org/api/resources/find-myresearchers
    print("got url_base={} and now setting url".format(url_base))
    url = (url_base + '?q=' + q + "&start=" + str(start_item_count)
           + '&rows=' + str(result_item_quantity_max))
    d_search['url'] = url # save for diagnostics
    add_curl_command(d_search)
    return requests.get(url, headers=d_headers)

def response_of_orcid_record(d_search, orcid_id, verbosity=0):
    me = "response_of_orcid_record"
    if d_search is None:
        raise(ValueError,"d_search is required")
    if verbosity != 0 :
        print("{}:Starting".format(me))
    d_headers = d_search['d_request_headers']
    url_format = d_search['url_format']
    # Orcid result item numbering starts at 1
    # See examples at: https://members.orcid.org/api/resources/find-myresearchers
    url = url_format.format(orcid_id)
    d_search['url'] = url # save for diagnostics
    add_curl_command(d_search)
    return requests.get(url, headers=d_headers)

# This is python 3.5.1 code
#
import sys
#import requests
import urllib, urllib.parse
import json
import pprint
from collections import OrderedDict
from io import StringIO, BytesIO
from datetime import datetime

'''
This notebook is meant to develop and test orpubtxml (ORchid PUBlic records to XML)

It is based on eatxml (Elsevier Api To Xml), but here revised to query for original load
date rather than pub year, and also revised to create an output directory for every single
day queried for a load date.

Further, since it queries load dates day-by-day, rather than inject the orig load date
into the xml for each article, a reader process may derive the orig load date from the
names of the 3 nearest ancestor directories that contain each xml file.

Ealdxml reads metadata information from the Elsevier Search API results of
UF-Authored articles, and Ealdxml then seeks the article results from the
Elsevier Full-text API.
If an article is not found, Ealdxml logs an error message, otherwise it outputs
a file named pii_{pii}.xml in the given an output folder for each article, where the
year,month, and day of the original load date of the article are encoded in the names
of its three nearest ancestor folders.

PII stands for Publisher Item Identifier, and it is supposed to be unique
among Elsevier articles and other pubishers (but maybe not all publishers).
See wikipedia - https://en.wikipedia.org/wiki/Publisher_Item_Identifier
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
from lxml import etree

utc_now = datetime.datetime.utcnow()
utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")

'''
Method orcid_result_entries_collect()
'''
def orcid_result_entries_collect(d_search, d_params, nodes_result, d_batch, n_batch, d_ns):

    me = 'orcid_result_entries_collect'
    verbosity = 1
    out_base_dir = d_params.get('host-output-directory','')
    output_dir = out_base_dir
    os.makedirs(output_dir, exist_ok=True)
    n_entry = 0
    n_entry_exceptions = 0
    for i,entry in enumerate(nodes_result):
        # Process the next orcid id result entry node element
        n_entry += 1
        orcid_id = entry.find('.//common:path', namespaces=d_ns).text

        #print("n_batch={}, i={}, orcid_id={}".format(n_batch,i,orcid_id))
        response_record = response_of_orcid_record(d_search, orcid_id)
        # print(repr(response_record.text))
        try:
            #print("Got response={}. Indeed!".format(r.text))
            # Parse the xml doc response and get its root node in node_root
            node_root = etree.fromstring(response_record.text.encode('utf-8'))
        except Exception as e:
            print("{}: Exception caught: cannot parse record for orcid_id={} results. e='{}'"
                  .format(me,repr(orcid_id), repr(e)))
            continue

        # Now node_root is the root of the xml document query results from the response.
        # It can have up to batch_size orcid id sections.

        # Next line strips out the default value that has None as a key, because such an
        # item choke downstream calls to my_elt.find() calls, probably other methods
        # too, on 20160307.
        d_ns = {key:value for key,value in dict(node_root.nsmap).items() if key is not None}

        # ORCID API DOCS promise that the num-found attribute has the total number of results
        # We do not really need it now as we do a single threaded sequence of queries, but if
        # it becomes time consuming, we could split it and hand off a segment of results to each
        # of multiple threads to collect the results.
        nodes_source_name = node_root.findall(".//common:source-name", namespaces=d_ns)
        if nodes_source_name and len(nodes_source_name) > 0:
            node_source_name=repr(nodes_source_name[0].tag)
        else:
            node_source_name=""
        print ("Batch item {}: orcid_id={}, name={}"
            .format(i+1,str(orcid_id),node_source_name))

        #Retrieve this orcid id's xml info
        # Save xml info to local file
        out_filename = '{}/orcid_{}.xml'.format(output_dir, orcid_id)
        with open(out_filename, 'wb') as outfile:
            outfile.write(etree.tostring(node_root, pretty_print=True))
    # end foreach entry
    response_search = None
    return response_search, n_entry, n_entry_exceptions
# end orcid_result_entries_collect()

'''
Method orpubtxml:

Based on program ealdxml 20170502: Elsevier Api Load Date to XML -
Read the Elsevier Search API for UF-Authored
articles and use the 'self' link URL along with the api_key to get XML Metadata
for each Elsevier article and save it to a file named pii_{pii}.xml under the
given output directory.

Here, we read the Orcid Search results to extract the orcid id of the returned record holders.
The caller can then search the individual public record for a given orcid id.

TODO: Params cymd_lo and hi are load date ranges for the search API use.
For example, the lo value or perhaps both may be used to limit search results by the orcid
search field: profile-last-modified date (see 20170502 https://members.orcid.org/api/tutorial/search-orcid-registry)
orcid records have been recently modified)
'''
def orpubtxml(d_orcid, d_params, verbosity=0):
    #
    # VALIDATE d_params
    # dt_start is the first orig-load-date that we want to collect
    # dt_end is the last orig-load dates that we want to collect
    me = 'orpubtxml'
    print("{}:starting.".format(me))

    total_results = 0

    output_articles = 0
    entries_collected = 0
    entries_excepted = 0
    # Collect results for all entries in this search query result response
    d_batches = dict()
    d_params.update({"batches": d_batches})

    n_batch = 1;
    d_batch = dict()
    total_results = 0

    d_search = d_orcid['pub_search']
    d_record = d_orcid['pub_record']

    search_batch_size = d_search['result_item_quantity_max']
    if search_batch_size < 1 or search_batch_size > 10000:
        raise(ValueError,"result_item_quantity_max={} not in range of 1 -10000".format(batch_size))
    start_offset = 1 # Use 1 for production, 2701 or so for testing
    index_batch_search = -1
    while(index_batch_search is not None): # Tip: infinite loop over index_batch_search
        index_batch_search += 1

        # Query and retrieve response for next batch of ORCID search results.
        # For our next batch of response_search_results, we ask for a batch search
        # results starting at the start_item_count.
        d_search['start_item_count'] = index_batch_search * search_batch_size + start_offset
        try:
            response_search_results = response_of_orcid_search(d_search, verbosity=1)
        except Exception as e:
            raise(ValueError,"Exception: Search query failed. curl='{}'"
                  .format(d_search['curl_command']))
            raise e

        print("Batch={}, curl={}".format(index_batch_search, d_search['curl_command']))

        # Parse the xml doc for this batch of search results
        try:
            node_search_root = etree.fromstring(response_search_results.text.encode('utf-8'))
        except Exception as e:
            print("{}: Exception caught: cannot parse initial search results. e='{}'".format(me,repr(e)))
            continue

        # Here node_search_root is the root of the xml document search results.
        # It should have up to batch_size quantity of orcid id sections.

        # Next line strips out the default value that has None as a key, because such an
        # item choke downstream calls to some_element.findall() calls, probably other methods
        # too, on 20160307.
        d_ns = {key:value for key,value in dict(node_search_root.nsmap).items()
                if key is not None}

        # ORCID API DOCS promise that the num-found attribute has the total number of results
        # across all potential batches of results. We only need it once, as it should not change.
        # We do not really need it now as we do a single threaded sequence of queries, but if
        # it becomes time consuming, we could split it and hand off a segment of results to each
        # of multiple threads to collect the results.
        total_results = int(node_search_root.attrib['num-found']);
        #print ("Got: Search num-found={}".format(n_results))

        nodes_search_result = node_search_root.findall(".//search:result", namespaces=d_ns)
        n_found_items = len(nodes_search_result)
        print("Search Result Batch {} has {} search:result nodes in result batch"
            .format(index_batch_search, n_found_items))

        if n_found_items < 1:
            break;

        # Process this batch of ORCID record identifier items

        batch_key = 'b'+ str(index_batch_search).zfill(5)
        d_batches[batch_key] = d_batch

        # PROCESS THE SEARCH RESULTS ENTRY DATA GIVEN IN results_tree
        # FOR THIS BATCH OF ARTICLES
        response_search_results, n_collected, n_excepted = (
            orcid_result_entries_collect(
                d_record, d_params, nodes_search_result, d_batch, index_batch_search,d_ns))

        entries_collected += n_collected
        entries_excepted += n_excepted

        d_batch['n_entries_collected'] = str(n_collected)
        d_batch['n_entries_excepted'] = str(n_excepted)

        print ("Through batch {}, total entries_collected so far = {}, exceptions = {}"
               .format(index_batch_search, str(entries_collected +1), str(entries_excepted)))
    # end while index_batch_search

    print("{}:Collected {} batches of max {} results. Total={}. Ending."
         .format(me,index_batch_search, search_batch_size, total_results))

    d_params.update({
        'total-result-entries': "0" if not total_results else str(total_results),
        })

    d_stats = dict()
    d_params.update({"stats": d_stats})
    d_stats['total_entries_collected'] = str(entries_collected)
    d_stats['total_entries_excepted'] = str(entries_excepted)
    return entries_collected, entries_excepted
#end def orpubtxml()

'''
 From given dictionary, return a list of lxml tree elements, one per dictionary item.
 Arguments are: A root lxml element, and a dictionary where each item represents a sub-element.
 Add a sub-element for each item using the item key as the sub-element name.
 If the item value is a dictionary, then do a recursive call using the new sub_element as d_root and
 the item value as the d_elts parameter.
'''
def add_subelements_from_dict(element, d_subelements):
    # Use an OrderedDct that is sorted by key for easier human-reading
    # First argument must be an lxml element
    # second argument must be a dictionary with
    #  (1) keys being legal XML tag names (not checked here),
    #  but note that they should begin with an alphabetic character, not a digit nor special character.
    # and (2) values being either
    # (a) a string or
    # (b) another dictionary of key values pairs, or
    # (c) a list of dicts with key-value pairs
    d_subelements = OrderedDict(sorted(d_subelements.items()) )
    for key, value in d_subelements.items():
        #For given element, create a new sub-element from this key
        # Check for valid xml tag name: http://stackoverflow.com/questions/2519845/how-to-check-if-string-is-a-valid-xml-element-name
        # poor man's check: just prefix with Z if first character is a digit.. the only bad type of tagname found so far...
        if key[0] >= '0' and key[0] <= '9':
            key = 'Z' + key
        subelement = etree.SubElement(element, key)

        if isinstance(value, dict):
            # Add  value-dict's subelements to this element
            add_subelements_from_dict(subelement, value)
        elif isinstance(value, list):
            #Use the key value as a parent element and the list index(plus 1) as a count attribute
            for i,value2 in enumerate(value):
                subelement2 = etree.SubElement(subelement, 'item')
                subelement2.attrib['count'] = str(i+1)
                add_subelements_from_dict(subelement2, value2)
        else:
            # Assume the value is a string for this element's text value
            subelement.text = str(value)
# end add_subelements_from_dict

# To an lxml tree, add subelements recursively from nested python data structures
# This is useful to register log message traces and to output into xml format at the end of a run.
def add_subelements(element, subelements):
    if isinstance(subelements, dict):
        d_subelements = OrderedDict(sorted(subelements.items()))
        for key, value in d_subelements.items():
            # Check for valid xml tag name:
            # http://stackoverflow.com/questions/2519845/how-to-check-if-string-is-a-valid-xml-element-name
            # poor man's check: just prefix with Z if first character is a digit..
            # the only bad type of tagname encountered using various applications... so far ...
            if key[0] >= '0' and key[0] <= '9':
                key = 'Z' + key
            subelement = etree.SubElement(element, key)
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

####### main run program

def orpubtxml_run(d_orcid=None):
    # PARAMETERS -- set these manually per run for now... but only cymd_start
    # and cymd_end would normally change.
    #
    if d_orcid is None:
        raise(ValueError, "d_orcid is None. That's exceptional.")
    cymd_start = '20170209'
    # cymd_end = '20160206'
    # EALDXML - Here, we do only one day at a time...
    cymd_end = '20170209'

    worker_threads = 1 # TODO
    # WARNING: now hardcoded, and later we may condsider to get these by programmatic introspection
    agent_creator_individual = 'UFAD\lib-adm-podengo'
    agent_creator_host = 'UFLIBS91B6D42.ad.ufl.edu'
    agent_creator_software = "orpubtxml-0.1" #may add attributes programming-language, revision-date, hash ...
    verbosity = 0

    out_base_dir = 'c:/rvp/elsevier/output_orpubtxml'

    # create output directory root if it does not exist
    os.makedirs(out_base_dir, exist_ok=True)

    # make other output directories (hardcoded now here)
    for sub_name in ['search', 'records','run']:
        os.makedirs('{}/{}'.format(out_base_dir,sub_name), exist_ok=True)

    utc_now = datetime.datetime.utcnow()
    # secsz_start: secz means seconds in utc(suffix 'z') when this run started
    secsz_start = utc_now.strftime("%Y-%m-%dT%H-%M-%SZ")

    print ("START ORPUBTXML RUN at {}\n\twith:\ncymd_start='{}', cymd_end='{}'\n  "
           "outbase_dir={},verbosity={}"
           .format(secsz_start, cymd_start, cymd_end, out_base_dir, verbosity))

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
        "worker-threads-count" : int(worker_threads),
        "api-search-query" : "",
        "max-output-articles" : "0", # TODO
        }

    # Process the Elsevier Search and Full-Text APIs to create local xml files
    entries_collected = 0
    entries_excepted = 0

    ###### MAIN CALL TO orpubtxml() ########

    if (1 == 1): # test with or without call to eatxml
        entries_collected, entries_excepted = orpubtxml(d_orcid, d_params, verbosity=verbosity)

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
    e_root = etree.Element("uf-orcid-api-harvest")
    add_subelements_from_dict(e_root, d_params)

    out_filename = '{}/run/run_orpubtxml_{}.xml'.format(out_base_dir, secsz_start)
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
    return
#=========================================================

orpubtxml_run(d_orcid)
print("Done")
