#
'''
 crawdxml.xml

 This is python 3.5.1 code

 crawdxml (Cross Ref Api Works by DOI - Given a list of DOIS, get crossRef 'works'
 result metadata and save to xml files.
 This dev code started based on crafaxml (CrosRef Api Find Affiliated works --- 20161218)
 and oadoi (mainly the part that feeds queries using a doi string).

 The dev plan is to make crawdxml get crossref full MD query data from a doi,
 and UF will typically use it weekly to work on dois from scopus that we do not
 already have --- to get uf author affiliation data and funding data (which is NOT in
 our circa-2016 style of Scopus API feed) and other details from
 crossref for UF articles published by all publishers that are covered by scopus
 including non-elsevier-published articles.

 With that info, we might query peoplesoft for info to contact authors to ask them sources of
 funding and encourage them create OA works and go satisfy funding rqts and to get
 ORCID ids.

 An important side note about crossref:
 The crossref affiliation filter provided by their API in 20161217 DOES find some
 DOIs metadata, but  only those that exactly match the entire sought affiliation
 string exactly.

'''

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

from lxml import etree
import xml.etree.ElementTree as ET
from pathlib import Path
import datetime
import pytz
import urllib.request
#Note: Official Python 3.5 docs cover a different xml library, ElementTree ET
#Maybe try it if lxml causes troubles --
# update: lxml shows no troubles so far after months of use
#import xml.etree.ElementTree as ET
from pathlib import Path

'''
Program crawdxml
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
        etl.add_subelements(node_root, d_entry)

'''
def get_json_result_by_url(url):
    me = "get_json_result_by_url"
    if url is None or url=="":
        raise Exception("Cannot send a request to an empty url.")
    try:
        #print("*** BULDING GET REQUEST FOR SCIDIR API RESULTS FOR URL='{}' ***".format(url))
        get_request = urllib.request.Request(url, data=None)

    except:
        raise Exception("Cannot send a request to url={}".format(url))
    try:
        #print("*** GET REQUEST='{}' ***".format(repr(get_request)))
        response = urllib.request.urlopen(get_request)
    except Exception as e:
        print("{}: Got exception instead of response for"
              " url={}, get_request={} , exception={}"
              .format(me, url, get_request, e))
        return None

    json_result = json.loads(response.read().decode('utf-8'))
    return json_result

#end get_json_result_by_url
'''
NOTE: see nice url of results to examine while finishing this method:
https://api.crossref.org/works?filter=affiliation:University%20of%20Florida,from-index-date:2016-12-01,until-index-date:2016-12-01
--
Method crawdxml: CrossRef API for Works by DOI To XML -
Read the CrossRef REST API github docs for details.
The 'works' REST api is used with the DOI suffix.

Get XML Metadata for each DOI-identified article and save it to a file named
doi_{doi-normalized}.xml under the given output directory.

NOTE: it always outputs into a directory output_crawdxml/doi that is emptied first.
So MUST FIRST SAVE old results or if needed later implement new per-run output
subdirectories based on run dates as done in xml2rdb.

Param l_dois has a list of DOIS to use for the search API to use to select
which articles for which to return metadata.
'''
def crawdxml(d_params=None, input_file_name=None, verbosity=0):
    #
    # VALIDATE d_params
    # dt_start is the first orig-load-date that we want to collect
    # dt_end is the last orig-load dates that we want to collect
    me = 'crawdxml'
    required_args = ['d_params', 'input_file_name']
    if not all(required_args):
        raise Exception("Missing some required_args: {}".format(required_args))

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

    # Make an output directory for the doi results of the following query
    output_folder_doi = '{}/doi'.format(output_folder_run)

    print("{}:IMPORTANT:DELETING and re-making output_folder_doi='{}'"
          .format(me,output_folder_doi))
    if os.path.isdir(output_folder_doi):
        shutil.rmtree(output_folder_doi, ignore_errors=True)

    os.makedirs(output_folder_doi)
    input_file = open(input_file_name, 'r')

    for line in input_file:
        doi_string = line.replace('\n','')
        #2017116 per new crossref readme.md, be polite and use https and give email
        #
        url_worklist_doi = (
            "https://api.crossref.org/works/doi/{}?mailto=podengo@ufl.edu"
            .format(doi_string))
        print("{}: using url={}".format(me,url_worklist_doi))

        d_json = get_json_result_by_url(url_worklist_doi)
        if d_json is None:
            entries_excepted += 1
            continue

        #Pretty-print json data
        # print("Got json response='{}'".format(json.dumps(d_json, indent=4, sort_keys=True)))

        # Create a node root with name result
        node_root = etree.Element("response")
        # Create xml sub-nodes from the json result
        etl.add_subelements(node_root, d_json, item_ids=True)
        '''
        ---
        '''
        str_xml = etree.tostring(node_root,pretty_print=True,encoding='unicode')
        #print("XML of the response: '{}'".format(str_xml))

        # doi = 'Not in CrossRef Results'
        # PROCESS THE NODE FOR A CROSSREF DOI
        # print ("Items child {} is {}".format(i+1,node.tag))
        node_doi = node_root.find('.//DOI')
        doi = ''
        if node_doi is None:
            entries_excepted += 1
            continue
        # print("Got node_doi tag={},text={}".format(node_doi.tag,node_doi.text))
        # For some convenience for most output batches, replace slashes in doi for part of filename
        doi = node_doi.text.replace('/','_')
        if not doi:
            entries_excepted += 1
            continue

        output_filename = '{}/doi_{}.xml'.format(output_folder_doi,doi)
        #print("Writing filename={}".format(output_filename))
        # Note: below, for encoding utf-8, return value is really bytes, not a string,
        # so also we open output_filename with mode='wb',  not 'w':
        with open(output_filename, 'wb') as outfile:
            # Note: below, for encoding utf-8, return value is really bytes, not a string
            bytes_xml = etree.tostring(node_root, pretty_print=True, encoding='utf-8')
            outfile.write(bytes_xml)
        entries_collected += 1
    # end for line in input file:
    # Return n good and n bad
    return entries_collected, entries_excepted
# end def crawdxml

def run(input_file_name=None):
    ####### RUN main CRAWDML program
    # PARAMETERS -- set these manually per run for now... but only cymd_start
    # and cymd_end would normally change.
    #

    me = 'run()'
    utc_now = datetime.datetime.utcnow()
    verbosity = 0
    # secsz_start: secz means seconds in utc(suffix 'z') when this run started
    secsz_start = utc_now.strftime("%Y-%m-%dT%H-%M-%SZ")

    output_folder_run = etl.data_folder(linux='/home/robert/', windows='U:/',
        data_relative_folder='data/outputs/crawdxml/run/{}/'
            .format(secsz_start))

    print("{}: Reading input_file_name = {}".format(me,input_file_name))

    print ("xxxSTART CRAWDXML RUN at {}\n, using input_file_name={}, output_folder_run={}"
           .format(secsz_start, input_file_name, output_folder_run))

    if not os.path.isdir(output_folder_run):
        os.makedirs(output_folder_run)

    worker_threads = 1 # TODO
    # Dict of metadata run parameter info on this run
    d_params={
        "secsz_start": secsz_start,
        "input_file_name" : input_file_name,
        "output_folder_run" : output_folder_run,
        "python_version" : sys.version,
        "max-queries" : "0", # TODO
        }

    # Process the Elsevier Search and Full-Text APIs to create local xml files
    entries_collected = 0
    entries_excepted = 0


    ###### MAIN CALL TO CRAWDXML() ########
    print("Calling crawdxml with INPUT_FILE_NAME={}".format(input_file_name))

    crawdxml(d_params=d_params, input_file_name=input_file_name)

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
    e_root = etree.Element("uf_crossref_works_list_harvest")
    etl.add_subelements(e_root, d_params)
    out_filename = '{}/run_crawdxml_{}.xml'.format(output_folder_run, secsz_start)
    os.makedirs(output_folder_run, exist_ok=True)

    with open(out_filename, 'wb') as outfile:
        outfile.write(etree.tostring(e_root, pretty_print=True))

    utc_now = datetime.datetime.utcnow()
    # secsz_start: secz means seconds in utc(suffix 'z') when this run started
    secsz_now = utc_now.strftime("%Y-%m-%dT%H-%M-%SZ")

    print ("END CRAWDXML RUN at {}\n\twith:\n input file '{}', using "
           "output_folder_run={}, with {} dois collected, and {} excepted"
           .format(secsz_now, input_file_name, output_folder_run, entries_collected, entries_excepted))

    print("Done!")
#end:def run()

#run
'''
SET BASE INPUT FILE NAME -- EDIT THIS PER RUN. 01_20170824.txt'
'''

base_input_file_name = "cross_doi_tmp.txt" # temp test doi
base_input_file_name = "cross_doi_20170601_20170824.txt" #64K records

input_folder = etl.data_folder(
  linux='/home/robert/Downloads/', windows='U:/data/tmp/')

input_file_name="{}{}".format(input_folder,base_input_file_name)

print("Using input_file_name={}".format(input_file_name))

run(input_file_name=input_file_name)
#
