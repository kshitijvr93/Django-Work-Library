# crafdtxml.py
# new name crafdtxml (Cross Ref Api Filter Date to xml
# Based on Crafatxml - so still may need to change occurrences of that name below in places too..
#
# API Documentation: https://github.com/CrossRef/rest-api-doc/blob/master/rest_api.md
#
# ALSO see the crawdxml notebook program that queries the cross ref "Works" api that allows selection
# of a specific DOI, where those results do include the author and affiliation string,
# with which we can do our own pattern matching on affiliation name to find variants of UF.
# Note: the upshote is that crossref affiliation filter in 20161217 DOES find some DOIs metadata, but
# only those that exactly match "University of Florida". Here we get all "filtered"
# data (including DOI) that crossref shows for a given index date, and then we use that DOI to
# do a more detailed query of the crossreff works DOI to get author-affiliation and much more detailed data
# for each DOI of interest.
# This is python 3.5.1 code
# Use the Crossref API to (1) harvest metadata for articles of a certain day and (2) later, to
# apply python filter to yield affiliations that match "University of Florida".
#
import sys
#import requests
import urllib, urllib.parse
import json
import pprint
from collections import OrderedDict
from io import StringIO, BytesIO
import shutil

from datetime import datetime

'''
This notebook is meant to develop, test, house, and entomb crafatxml (CrossRef Api To Xml)
It is initially based on ealdxml (Elsevier Api To Xml), and others (from oadoixml it borrows
json conversion using my trusty log-authoring method add_subelements(). It writes out
to ..output_crafatxml a file for each doi/item encountered by querying the crossref api for
affiliation of the University of Florida

Crafatxml reads information from CrossRef API as of 20161215, for
UF-Authored articles and related metadata.
'''
from lxml import etree
import xml.etree.ElementTree as ET
from pathlib import Path
import datetime
import pytz
import os
import urllib.request
from lxml import etree
#Note: Official Python 3.5 docs use different library, ElementTree ET
#Maybe try it if lxml causes troubles --
# update: lxml shows no troubless so far after months of use
#import xml.etree.ElementTree as ET
from pathlib import Path

def add_subelements(element, subelements, item_ids=False):
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
            add_subelements(subelement, value, item_ids=item_ids)
    elif isinstance(subelements, list):
        # Make a dict indexed by item index/count for each value in the 'value' that is a list
        for i, value in enumerate(subelements):
            id_filled = str(i+1).zfill(8)
            if item_ids:
                subelement = etree.Element("item")
                subelement.attrib['id'] = id_filled
                element.append(subelement)
            else:
                #encode the ID as a suffix to to element tag name itself
                subelement = etree.SubElement(element, 'item-{}'.format(id_filled))

            add_subelements(subelement, value, item_ids=item_ids)
    else: # Assume it is a string-like value. Just set the element.text and do not recurse.
        element.text = str(subelements)
    return True
# end def add_subelements()

''' d_affiliation_names:
key
    is local abbreviation (used as a step in output directory path)
    for a university or author affiliation,
and value
    is a list of strings to check vs an affiliation name for a match.

Initialize this dict to match CHORUS 'institution or affiliation partners' as of 20170313
Note:
'''
od_affiliation_substrings = OrderedDict({
    'university_of_florida': ['university of florida','univ.fl','univ. fl'
        ,'univ fl' ,'univ of florida'
        ,'u. of florida','u of florida']
    #first cut - just seek denver, and filter/narrow local results later
    ,'university_of_denver': [ 'university of denver']
    # 'udenver': ['university of denver']
    ,'chiba_university' : ['chiba university','university of chiba']

    #'la trobe university': ['la trobe university', 'la trobe university']
    ,'la_trobe_university': ['la trobe university', 'latrobe university']
})

'''
Method get_affiliations_by_name_substrings:

We are given an affiliation name and od_affiliation_substrings for which
substring matches on the given name are sought.

Return:
    A dictionary of affiliations where each key is the same as an input
    od_affiliation_substring key where one of its substrings matched the given name.
    The returned dictionary will have length of 0 of no matches were found.

NOTES: If max_affiliation is not zero, it is the maximum number of matching affiliations
to include in the returned dictionary. This allows the caller to set it to 1 to speed up
the algorithm used in this method.
'''
def get_affiliations_by_name_substrings(name, od_affiliation_substrings,
    max_affiliations = 0):
    d_affiliations = {}
    n_affils = 0;
    for affiliation, substrings in od_affiliation_substrings.items():
        for substring in substrings:
            if name.lower().find(substring) != -1:
                d_affiliations[affiliation] = '1'
                n_affils += 1
                if max_affiliations > 0 and n_affils >= max_affiliations:
                    return d_affiliations
                # Found a substring match. So no need to check the others.
                break
    return d_affiliations

'''
Method uf_affiliation_value

Arg gives a name, and this method:
returns 1 - if the name identifies the university of florida
returns 0 - otherwise
'''
def uf_affiliation(name):
    text_lower = name.lower() if name is not None else ''
    #print("Using affil argument text={}".format(repr(text)))
    for match in ['university of florida','univ.fl','univ. fl'
        ,'univ fl' ,'univ of florida'
        ,'u. of florida','u of florida']:
        if text_lower.find(match) != -1:
            #print("Match")
            return 1
    #print("NO Match")
    return 0

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
        add_subelements(node_root, d_entry)

'''
def get_json_result_by_url(url):

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
        print("get_json_result_by_url: Got exception instead of response for"
              " url={}, get_request={} , exception={}"
              .format(url, get_request, e))
        raise

    json_result = json.loads(response.read().decode('utf-8'))
    return json_result
#end get_json_result_by_url
'''
NOTE: see nice url of results to examine while finishing this method:
http://api.crossref.org/works?filter=affiliation:University%20of%20Florida,from-index-date:2016-12-01,until-index-date:2016-12-01
--
Method crafatxml: CrossRef API To XML - Read the CrossRef REST API github docs for details.

Get XML Metadata for each DOI-identified article and save it to a file named
doi_{doi-normalized}.xml under the given output directory.

Params cymd_lo and hi are load date ranges for the search API use to select
which articles for which to return metadata.
'''
def crafdtxml(d_params, verbosity=0):
    #
    # VALIDATE d_params
    # dt_start is the first orig-load-date that we want to collect
    # dt_end is the last orig-load dates that we want to collect
    me = 'crafddtxml'
    dt_day = datetime.datetime.strptime(d_params['cymd_start'],'%Y%m%d')
    dt_end = datetime.datetime.strptime(d_params['cymd_end'], '%Y%m%d')
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

    output_folder_base = d_params['output_folder_base']

    n_day = 0;
    d_batch = dict()
    uf_articles = 0
    articles_todal = 0
    while dt_day <= dt_end:
        n_day += 1
        y4md = dt_day.strftime('%Y-%m-%d')
        d_params['cymd_day'] = y4md
        d_params['cymd_bef'] = dt_bef.strftime('%Y%m%d')
        d_params['cymd_aft'] = dt_aft.strftime('%Y%m%d')

        # Make an output directory for the doi results of the following query
        output_folder_ymd = '{}/doi/{}/{}/{}'.format(
            output_folder_base,y4md[:4],y4md[5:7],y4md[8:10])

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

        cursor = '*'
        result_count = 1
        uf_articles_day = 0
        articles_day = 0
        n_batch = 0
        while(1):
            # Each loop returns 1000 articles.
            # It was 230,000 articles on 9/30/2016, but usually 5-10,000
            n_batch += 1

            url_worklist_day = (
                "http://api.crossref.org/works?rows=1000&cursor={}&filter="
                "has-affiliation:true,from-deposit-date:{},until-deposit-date:{}"
                .format(cursor,y4md, y4md))


            print("{}: using url={}".format(me,url_worklist_day))

            d_json = get_json_result_by_url(url_worklist_day)
            # Pretty-print json data
            # print(json.dumps(d_json, indent=4, sort_keys=True))

            # Create a node root with name result
            node_response_root = etree.Element("response")
            # Create xml sub-nodes from the json result
            add_subelements(node_response_root, d_json, item_ids=True)
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
                  1.5: next-cursor: (present only if cursor parameter was given) if more results exist,
                       this is a hashy string to use as the next cursor argument
                  1.6: total-results: with value N, which is the number of
                         individual item-000* nodes above

               2: message-type: should be 'work-list' for url_initial_worklist
               3: message-version: should be 1.0.0 initally -- check it later if needed
               4: status: value should be OK

               We will output parse the response to get individual item-000* node contents and
               output one xml file per item-000* node with root element named <crossref-doi>.
            '''
            doi = 'Not in CrossRef Results'

            node_items = node_response_root.find('.//items')
            node_total_results = node_response_root.find('.//total-results')
            if n_batch == 1 and node_total_results is not None:
                print("Processing total-results count = {}".format(node_total_results.text))
            if node_items is None or len(node_items) < 1:
                print("CrossRef API Response shows no result items remain for this query.")
                break;

            #print ("Len of node_items={}".format(len(node_items)))

            for i, node_item in enumerate(node_items):
                # Create a root node for this item's xml output
                node_output_root = etree.Element("crossref-api-filter-date-UF")
                entries_collected += 1
                articles_day += 1
                d_article_affiliations = {}
                # RENAME this item's main node tag from item to message to match crossref worklist
                # single-doi REST topmost node name, to facilitate re-use of mining map (used
                # in xml2rdb program) for cr* family of harvests...
                node_item.tag = 'message'
                # Adopt this item's XML subtree under this new output item root node
                node_output_root.append(node_item)

                # Get doi value because it is required by our use of the Metadata
                node_doi = node_item.find('.//DOI')
                if node_doi is None or not node_doi.text:
                    entries_excepted += 1
                    continue

                # print("Got node_doi tag={},text={}".format(node_doi.tag,node_doi.text))
                # If no author has an affiliation for University of Florida,
                # Skip this article
                uf_article = False
                nodes_name = node_item.findall(
                          './/author/*//affiliation/*//name')
                if nodes_name is None:
                    # print("This doi has no affiliation names")
                    continue # No affiliation names given, so skip it
                # print("Found {} names in this article".format(len(nodes)))

                for node_name in nodes_name:
                    name = node_name.text
                    #print("Trying affil name='{}'".format(name))
                    '''
                    if uf_affiliation(node_name.text) == 1:
                        print("For doi={}, found UF name={} "
                              .format(node_doi.text, node_name.text ))
                        uf_article = True
                        break
                    '''
                    d_author_affiliations = get_affiliations_by_name_substrings(
                        name, od_affiliation_substrings, max_affiliations = 1)
                    if len(d_author_affiliations) == 0:
                        continue
                    for affiliation in d_author_affiliations.keys():
                        # For every found author's child affiliation,
                        # add affil_X tag to the author's child affiliation name
                        # EG (affil_uf for uf affil)
                        subelement = etree.Element("affil_{}".format(affiliation))
                        node_name.append(subelement)

                    # Bequeath this sought author-affiliation (if found)
                    # to this article
                    d_article_affiliations.update(d_author_affiliations)
                # Examined each given author affiliation name

                # if count of found article affiliations is 0, skip it.
                if len(d_article_affiliations) == 0:
                    continue #skip this article

                # This article has some sought affiliations as described in
                # od_affiliation_substrings

                uf_articles_day += 1
                uf_articles += 1

                for affiliation in d_article_affiliations:
                    # Create an xml tag for a root child, eg 'affil_uf' with value 1,
                    # if uf (or other abbrev) was found for this article
                    subelement = etree.Element("affil_{}".format(affiliation))
                    node_output_root.append(subelement)

                out_str = etree.tostring(node_output_root, pretty_print=True)
                output_filename = '{}/doi_{}.xml'.format(
                    output_folder_ymd,str(result_count).zfill(8))
                result_count += 1
                # print("Writing filename={}".format(output_filename))
                with open(output_filename, 'wb') as outfile:
                    outfile.write(out_str)

                # future? Might be handy to append a line to a legend file that pairs the result count with the
                # doi value, and get the name from a parameter... or something like that.
                #
                #
                entries_collected += 1
            # end loop through article items in this query's response

            node_cursor = node_response_root.find('.//next-cursor')
            print("Produced doi files for batch {}".format(n_batch))

            if node_cursor is None or node_cursor.text == '':
                print("Got nothing for NODE CURSOR -- end of batches")
                break;
            else:
                cursor = node_cursor.text
                print("Got node_cursor value={}. ".format(cursor))
            print("End batch {}\n".format(n_batch))

        # End loop through potential multiple result batches
        print (
            "\nEnd of batches for this day={} with {} articles and {} uf articles\n"
            "===========================\n\n"
            .format(y4md, articles_day, uf_articles_day))

        #print("Got doi={}, node_root.tostring = '{}'"
        #  .format(doi, str(etree.tostring(node_root, pretty_print=True, encoding='unicode'))))

        #set up for next day's query
        dt_day += day_delta
        dt_bef += day_delta
        dt_aft += day_delta
    # end collection while dt_day <= dt_end

    return entries_collected, entries_excepted, uf_articles
# end def crafdtxml

####### RUN main CRAFATXML program
# PARAMETERS -- set these manually per run for now... but only cymd_start
# and cymd_end would normally change.
#

me = 'main code to run crafatxml'
utc_now = datetime.datetime.utcnow()
utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")

verbosity = 0

#NOTE: CrossRef query parameters provide FROM dates and UNTIL dates, inclusive of those days.
# Compare: Elsevier api parameters provide BEF and AFT dates, exclusive of those days.
# So here, since we are using CrossRef APIs, the cymd_start and cymd_end days are INCLUDED
# in the API query results.
cymd_start = '20170306'
#cymd_start = '20161213'
# cymd_end = '20160206'
# CRAFATXML - Here, we do only one day at a time...
cymd_end = '20170306'

utc_now = datetime.datetime.utcnow()
# secsz_start: secz means seconds in utc(suffix 'z') when this run started
secsz_start = utc_now.strftime("%Y-%m-%dT%H-%M-%SZ")
output_folder_base = 'c:/rvp/elsevier/output_crafdtxml_chorus'
output_folder_run = '{}/run/{}'.format(output_folder_base, secsz_start)

print ("START CRAFDTXML RUN at {}\n\twith:\ncymd_start='{}', cymd_end='{}'\n  "
       "output_folder_base={},verbosity={}"
       .format(secsz_start, cymd_start, cymd_end, output_folder_base, verbosity))

if not os.path.isdir(output_folder_base):
    os.makedirs(output_folder_base)

if not os.path.isdir(output_folder_run):
    os.makedirs(output_folder_run)

worker_threads = 1 # TODO
# Dict of metadata run parameter info on this run
d_params={
    "secsz_start": secsz_start,
    "cymd_start" : cymd_start,
    "cymd_end"   : cymd_end,
    "output_folder_base" : output_folder_base,
    "python_version" : sys.version,
    "max-queries" : "0", # TODO
    }

# Process the Elsevier Search and Full-Text APIs to create local xml files
entries_collected = 0
entries_excepted = 0

###### MAIN CALL TO CRAFDTXML() ########

if (1 == 1): # test with or without call to eatxml
    entries_collected, entries_excepted, uf_articles = crafdtxml(d_params, verbosity=verbosity)

############### WRAP-UP MISC OUTPUT ################

# Also record some summary output results in d_params for saving as xml file
#
utc_now = datetime.datetime.utcnow()
secsz_end = utc_now.strftime("%Y-%m-%dT%H-%M-%SZ")

d_params.update({
    "total-entries-collected" : entries_collected,
    "total-entries-excepted" : entries_excepted,
    "uf-articles-count" : uf_articles,
    "secsz-end" : secsz_end,
    # Prevent actual api-key value from being stored in the output
    "api-key" : '*UF-Smathers Proprietary*'
    })

# Wrap up and write out the run parameters log file.
e_root = etree.Element("uf_crossref_works_aff_uf_harvest")
add_subelements(e_root, d_params)
out_filename = '{}/run_crafdxml_{}.xml'.format(output_folder_run, secsz_start)
os.makedirs(output_folder_run, exist_ok=True)

with open(out_filename, 'wb') as outfile:
    outfile.write(etree.tostring(e_root, pretty_print=True))
print('Collected {} articles, excepted {}, and {} were uf articles'
     .format(entries_collected, entries_excepted, uf_articles))
print("Done!")
