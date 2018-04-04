# crafatxml.py
# new name crafatxml (Cross Ref Api Filter Affiliation to xml AND
# affiliation target "University of Florida" is used here.
# NOTE: 20170828 - TODO: make sure this works after 201708 because I left this
# code untested then, to pursue primping and running crafdtxml.py for an
# important analysis.
#
# NOTE: However, this afffiliation "University of Florida" argument in
# crossref has no wildcard options and it will NOT find somewhat
# nonuniform decorated affiliation names like
# "Univeristy of Florida, Gainesville", nor any with department names
# prefixed, with semicolon # separators in the text, etc.
#
# BUT - see the crawxml.xml program that queries the cross ref "Works" api that
# provides a specific DOI, eg from Scopus of Elsevier or other sources,
# and then one CAN see the author and affiliation string,
# although a harvester program (like exoldxml) would have to do its own
# pattern matching on affiliation name # to find variants of UF.
#
# SO - the upshot is that crossref affiliation filter in 20161217 DOES
# find some DOIs metadata, but only those that exactly match the sought
# affiliation.
# This is python 3.5.1 code
# Use the Crossref API to harvest metadata for affiliations that match
# "University of Florida" for dates specified by Crossref params
# from-index-date and until-index-date.
# ONLINE API DOCS: see https://github.com/CrossRef/rest-api-doc/blob/master/rest_api.md
import sys, os, os.path, platform
def get_path_modules(verbosity=0):
  env_var = 'HOME' if platform.system().lower() == 'linux' else 'USERPROFILE'
  path_user = os.environ.get(env_var)
  path_modules = '{}/git/citrus/modules'.format(path_user)
  if verbosity > 1:
    print("Assigned path_modules='{}'".format(path_modules))
  return path_modules
sys.path.append(get_path_modules())
print("Sys.path={}".format(sys.path))
sys.stdout.flush()
import etl

#import requests
import urllib, urllib.parse
import json
import pprint
from collections import OrderedDict
from io import StringIO, BytesIO
import shutil

from datetime import datetime

'''
This program is meant to develop, test, house, and entomb crafatxml
(CrossRef Api To Xml)
It is initially based on ealdxml (Elsevier Api To Xml), and others
(from oadoixml it borrows
json conversion to xml method etl.add_subelements().

It writes out to ..output_crafatxml a file for each doi/item encountered
by querying the crossref api for
affiliation of the University of Florida

Crafatxml reads information from CrossRef API as of 20161215, for
UF-Authored articles and related metadata.
'''
from lxml import etree
import xml.etree.ElementTree as ET
from pathlib import Path
import datetime
import pytz
import urllib.request
from lxml import etree
#Note: Official Python 3.5 docs use different library, ElementTree ET
#Maybe try it if lxml causes troubles --
# update: lxml shows no troubless so far after months of use
#import xml.etree.ElementTree as ET
from pathlib import Path

'''
Program crafatxml (crossref api filter affiliations To XML) reads information
from Scopus Search API for UF-Authored (affiliated) articles and for each,
it seeks it in the Scopus Full-text API.

If not found, it logs an error message, otherwise it outputs a file named
scopus_{scopus_id}.xml in the given output directory for each article.
'''
'''get_json_result_by_url
Given a url, return the expected json response.

Sample usage by caller who wants xml instead:

        print("Using url_request='{}'".format(url_request))
        d_result = get_json_result_by_url(url_request)

        #print("Got d_result='{}'".format(repr(d_result)))
        # Point into the interesting data root-depending on the url's API documents.
        #d_entry = d_result['results'][0]
        # or leave as is and examine json to see the location of desired data...
        d_entry = d_result
        #print("\n\nGot d_entry='{}'\n".format(d_entry))

        # Save the xml as a string
        node_root = etree.Element("entry")
        elt.add_subelements(node_root, d_entry)

'''

'''
NOTE: see nice url of results to examine while finishing this method:
http://api.crossref.org/works?filter=affiliation:University%20of%20Florida,from-index-date:2016-12-01,until-index-date:2016-12-01
--
Method crafatxml: CrossRef API To XML -
Read the CrossRef REST API github docs for details.

Get XML Metadata for each DOI-identified article and save it to a file named
doi_{doi-normalized}.xml under the given output directory.

Params cymd_lo and hi are load date ranges for the crossref search API
parameters 'from-index-date' and 'until-index-date' used to select for
which articles to return metadata.
'''

def crafatxml(d_params, verbosity=0):
    #
    # VALIDATE d_params
    # dt_start is the first orig-load-date that we want to collect
    # dt_end is the last orig-load dates that we want to collect
    me = 'crafatxml'
    dt_day = datetime.datetime.strptime(d_params['cymd_start'],'%Y%m%d')
    dt_end = datetime.datetime.strptime(d_params['cymd_end'], '%Y%m%d')

    day_delta = datetime.timedelta(days=1)

    total_results = 0

    output_articles = 0
    entries_collected = 0
    entries_excepted = 0
    # Collect results for all entries in this search query result response
    d_batches = dict()
    d_params.update({"batches": d_batches})

    output_folder_run = d_params['output_folder_run']

    n_batch = 1;
    d_batch = dict()

    dt_bef = dt_day - day_delta
    dt_aft = dt_day + day_delta

    while dt_day <= dt_end:

        y4md = dt_day.strftime('%Y-%m-%d')
        d_params['cymd_day'] = y4md
        d_params['cymd_bef'] = dt_bef.strftime('%Y%m%d')
        d_params['cymd_aft'] = dt_aft.strftime('%Y%m%d')

        # Make an output directory for the doi results of the following query
        output_folder_ymd = '{}/doi/{}/{}/{}'.format(
            output_folder_run,y4md[:4],y4md[5:7],y4md[8:10])

        print("DELETING and RE-Making output_folder_ymd='{}'".format(output_folder_ymd))
        if os.path.isdir(output_folder_ymd):
            try:
                shutil.rmtree(output_folder_ymd, ignore_errors=True)
            except:
                print("Cannot rmtree folder {}. File or folder might be in use?"
                      .format(output_folder_ymd))
                raise
        try:
            os.makedirs(output_folder_ymd)
        except:
            print("Cannot make folder {}. File might be in use?".format(output_folder_ymd))
            raise
        protocol = 'https'
        url_worklist_day = (
            "{}://api.crossref.org/works?rows=1000&filter=affiliation:University%20of%20Florida,"
            "from-index-date:{},until-index-date:{}".format(protocol,y4md, y4md))
        print("{}: using url={}".format(me,url_worklist_day))

        d_json = etl.get_json_result_by_url(url_worklist_day)
        # Pretty-print json data
        # print(json.dumps(d_json, indent=4, sort_keys=True))

        # Create a node root with name result
        node_response_root = etree.Element("response")
        # Create xml sub-nodes from the json result
        elt.add_subelements(node_response_root, d_json, item_ids=True)
        ''' The root node 'response' from url_worklist_day has had/should have four child nodes:

           1: message: with child nodes
              1.1: facets:
              1.2: items: with child nodes
                     1.1.1-N: some individual item-000* nodes, one per DOI
              1.3: items-per-page: (IPP) with value normally 20f
              1.4: query: with child nodes
                   1.4.1: search-terms: with value for used search terms
                   1.4.2: search-indix: with index about total results in result set
                            (retrievable in multiple url-requested responses numbering
                            IPP per response page)
              1.5: total-results: with value N, which is the number of
                     individual item-000* nodes above

           2: message-type: should be 'work-list' for url_initial_worklist
           3: message-version: should be 1.0.0 initally -- check it later if needed
           4: status: value should be OK

           We will output parse the response to get individual item-000* node contents and
           output one xml file per item-000* node with root element named <crossref-doi>.
        '''
        #doi = 'Not in CrossRef Results'
        node_items = node_response_root.find('.//items')
        #print ("Len of node_items={}".format(len(node_items)))

        for i,node in enumerate(node_items):
            # Create a root node for this item's xml output
            node_item_root = etree.Element("crossref-api-filter-aff-UF")

            # RENAME this item's main node tag from item to message to match crossref worklist
            # single-doi REST topmost node name, to facilitate re-use of mining map (used
            # in xml2rdb program) for cr* family of harvests...
            node.tag = 'message'
            # Adopt this item's XML subtree under this new item root node
            node_item_root.append(node)

            # Get doi value to construct output filename
            node_doi = node.find('.//DOI')

            # Add another node node 'message' to match
            # doi = ''
            if node_doi is None:
                entries_excepted += 1
                continue
            # Replace pesky slash characters to create a filesysetm (fs) name for the doi to
            # put all xml output in one tidy output folder.
            # Later, one must look IN the file to get the real doi.
            fs_doi = node_doi.text.replace('/','_')

            if not fs_doi:
                entries_excepted += 1
                continue

            out_str = etree.tostring(node_item_root, pretty_print=True)
            output_filename = '{}/doi_{}.xml'.format(output_folder_ymd,fs_doi)
            #print("Writing filename={}".format(output_filename))
            with open(output_filename, 'wb') as outfile:
                outfile.write(out_str)
            entries_collected += 1

        # end loop through items in this query's response
        # NOTE: now we get up to 1000 nodes, which is suffienct 'per-day' for UF articles,
        # however, we need to use the offset or cursor features if more items appear in a response.
        # We do that now in program crawdxml.py or similar name...

        #print("Got doi={}, node_root.tostring = '{}'"
        #  .format(doi, str(etree.tostring(node_root, pretty_print=True, encoding='unicode'))))

        #set up for next day's query
        dt_day += day_delta
        dt_bef += day_delta
        dt_aft += day_delta
    # end collection while dt_day <= dt_end

    return entries_collected, entries_excepted
# end def crafatxml

def run():
    ####### RUN main CRAFATXML program
    # PARAMETERS -- set these manually per run for now... but only cymd_start
    # and cymd_end would normally change.
    #

    me = 'main code to run crafatxml'
    utc_now = datetime.datetime.utcnow()
    utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")

    verbosity = 0
    cymd_start = '20160206'
    cymd_start = '20170309'
    #cymd_start = '20161213'
    # cymd_end = '20160206'
    # CRAFATXML - Here, we do only one day at a time...
    cymd_end = '20170309'

    utc_now = datetime.datetime.utcnow()
    # secsz_start: secz means seconds in utc(suffix 'z') when this run started
    secsz_start = utc_now.strftime("%Y-%m-%dT%H-%M-%SZ")

    output_folder_run = etl.data_folder(linux='/home/robert/', windows='U:/',
        data_relative_folder='data/outputs/crafatxml/run/{}/'
            .format(secsz_start))

    print ("START CRAFATXML RUN at {}\n\twith:\ncymd_start='{}', cymd_end='{}'\n  "
           "output_folder_run={},verbosity={}"
           .format(secsz_start, cymd_start, cymd_end, output_folder_run, verbosity))

    if not os.path.isdir(output_folder_run):
        os.makedirs(output_folder_run)

    worker_threads = 1 # TODO
    # Dict of metadata run parameter info on this run
    d_params={
        "secsz_start": secsz_start,
        "cymd_start" : cymd_start,
        "cymd_end"   : cymd_end,
        "output_folder_run" : output_folder_run,
        "python_version" : sys.version,
        "max-queries" : "0", # TODO
        }

    # Process the Elsevier Search and Full-Text APIs to create local xml files
    entries_collected = 0
    entries_excepted = 0

    ###### MAIN CALL TO CRAFATXML() ########

    if (1 == 1): # test with or without call to eatxml
        entries_collected, entries_excepted = crafatxml(d_params, verbosity=verbosity)

    ############### WRAP-UP MISC OUTPUT ################

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

    # Wrap up and write out the run parameters log file.
    e_root = etree.Element("uf_crossref_works_aff_uf_harvest")
    elt.add_subelements(e_root, d_params)
    out_filename = '{}/run_crafatxml_{}.xml'.format(output_folder_run, secsz_start)
    os.makedirs(output_folder_run, exist_ok=True)

    with open(out_filename, 'wb') as outfile:
        outfile.write(etree.tostring(e_root, pretty_print=True))

    print("Done!")
#end def run():

# RUN
#
run()
