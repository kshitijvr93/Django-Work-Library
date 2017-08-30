''' crafdtxml.py

Program crafdtxml - Cross Ref Api Filter Date to xml
Based on Crafatxml - so still may need to change occurrences of that name
below in places too..

CrossRef API Documentation:
https://github.com/CrossRef/rest-api-doc/blob/master/rest_api.md

ALSO see the crawdxml notebook program that queries the cross ref "Works" api
that allows selection of a specific DOI, where those results do include the
author and affiliation string, with which we can do our own pattern matching
on affiliation name to find variants of UF.

Note: the upshot is that crossref affiliation filter in 20161217 DOES find
some DOIs metadata, but only those that exactly match "University of Florida".

Here we get all "filtered-by-index or issue date" data (including DOI) that
crossref shows for a given index date, and then we use that DOI to do a
more detailed query of the crossreff works DOI to get author-affiliation
and much more detailed data for each DOI of interest.

This is python 3.5.1 code
Use the Crossref API to (1) harvest metadata for articles of a certain day
and (2) later, to apply python filter to yield affiliations that match
"University of Florida".
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
#Note: Official Python 3.5 docs use different library, ElementTree ET

''' od_affiliation_names OrderedDict
key
    is local name abbreviation (used as a step in output directory path)
    for a university or author affiliation, e.g.,'UF' or "University of Florida"
and value
    is a list of strings to check vs an affiliation name for a match.
    later may make this value a regular expression to check

Initialize this dict to match CHORUS 'institution or affiliation partners'
as of 20170313
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
    od_affiliation_substring key where one of its substrings matched the given
    name.
    The returned dictionary will have length of 0 of no matches were found.

NOTES: If max_affiliation is not zero, it is the maximum number of matching
affiliations to include in the returned dictionary. This allows the caller
to set it to 1 to speed up the algorithm used in this method.
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
    # VALIDATE d_params
    # dt_start is the first orig-load-date that we want to collect
    me = 'crafdtxml'

    days = etl.sequence_days(d_params['cymd_start'], d_params['cymd_end'])

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

    for n_day, (y4md, dt_day) in enumerate(days):
        y4 = y4md[0:4]
        mm = y4md[4:6]
        dd = y4md[6:8]

        y4_m_d = y4 + '-' + mm + '-' + dd

        # Make an output directory for the doi results of the following query
        output_folder_ymd = '{}doi/{}/{}/{}'.format(
            output_folder_base, y4, mm, dd)

        print("DELETING and RE-Making output_folder_ymd='{}'"
            .format(output_folder_ymd))

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
            print("Cannot make folder {}. File might be in use?"
                .format(output_folder_ymd))
            raise

        cursor = '*'
        result_count = 1
        uf_articles_day = 0
        articles_day = 0
        n_batch = 0

        while(1):
            # Each loop returns 1000 articles.
            # The total was 230,000 articles on 9/30/2016, but in 2016 one day
            # usually contains 5-10,000 articles
            n_batch += 1

            url_worklist_day = (
                "http://api.crossref.org/works?rows=1000&cursor={}&filter="
                "has-affiliation:true,from-deposit-date:{},until-deposit-date:{}"
                .format(cursor,y4_m_d, y4_m_d))

            print("{}: using url={}".format(me,url_worklist_day))

            d_json = etl.get_json_result_by_url(url_worklist_day)
            # Pretty-print json data
            # print(json.dumps(d_json, indent=4, sort_keys=True))

            # Create a node root with name result
            node_response_root = etree.Element("response")
            # Create xml sub-nodes from the json result
            etl.add_subelements(node_response_root, d_json, item_ids=True)

            '''
            We have a result xml tree with root 'node_response_root' our request
            url_worklist_day and it should have four main child nodes and a structure like:

               1: message: with child nodes
                  1.1: facets:
                  1.2: items: with child nodes
                         1.2.1-1.2.1.N: some individual item-000* nodes, one per DOI
                  1.3: items-per-page: (IPP) with value normally 20
                  1.4: query: with child nodes
                       1.4.1: search-terms: with value for used search terms
                       1.4.2: search-index: with index about total results in
                                result set (retrievable in multiple url-requested
                                responses numbering IPP per response page)
                  1.5: next-cursor: (present only if cursor parameter was given, which
                       we do in this program)
                       if more results exist, this is a hashy string to use as
                       the next cursor argument
                  1.6: total-results: with value N, which is the number of
                         individual item-000* nodes above

               2: message-type: should be 'work-list' for url_initial_worklist
               3: message-version: should be 1.0.0 initally -- check it later
                  if needed
               4: status: value should be OK

               We will output parse the response to get individual item-000*
               node contents and output one xml file per item-000* node with
               root element named <crossref-doi>.
            '''

            doi = 'Not in CrossRef Results'

            node_items = node_response_root.find('.//items')
            node_total_results = node_response_root.find('.//total-results')
            if n_batch == 1 and node_total_results is not None:
                print("Processing total-results count = {}"
                    .format(node_total_results.text))

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
                # RENAME this item's main node tag from 'item' to 'message' to match
                # crossref worklist
                # single-doi REST topmost node name, to facilitate re-use of
                # mining map (used in xml2rdb program) for cr* family of harvests...
                node_item.tag = 'message'
                # Adopt this item's XML subtree under this new output item root node
                node_output_root.append(node_item)

                # Get doi value because it is required by our use of the Metadata
                node_doi = node_item.find('.//DOI')
                if node_doi is None or not node_doi.text:
                    entries_excepted += 1
                    continue

                # print("Got node_doi tag={},text={}".format(node_doi.tag,
                # node_doi.text))
                # If no author has an affiliation for University of Florida,
                # Skip this article
                uf_article = False
                nodes_name = node_item.findall(
                          './/author/*//affiliation/*//name')
                if nodes_name is None:
                    # print("This doi has no affiliation names")
                    # No affiliation names given, so continue to skip it
                    continue
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
                print("{}:Writing filename={}".format(me,output_filename))
                with open(output_filename, 'wb') as outfile:
                    outfile.write(out_str)

                # future? Might be handy to append a line to a legend file that
                # pairs the result count with the doi value, and get the name
                # from a parameter... or something like that.
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
                print("{}:Got node_cursor value='{}'.".format(me,cursor))
            print("End batch {}\n".format(n_batch))

        # End loop through potential multiple result batches for this day
        print (
            "\nEnd of batches for this day={} with {} articles and {} uf articles\n"
            "===========================\n\n"
            .format(y4md, articles_day, uf_articles_day))

    # end while loop over days

    return entries_collected, entries_excepted, uf_articles
# end def crafdtxml

####### RUN main CRAFATXML program
# PARAMETERS -- set these manually per run for now... but only cymd_start
# and cymd_end would normally change.
#

def run():
  me = 'main code to run crafatxml'
  utc_now = datetime.datetime.utcnow()
  utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")

  verbosity = 0

  # NOTE: CrossRef query parameters provide FROM dates and UNTIL dates,
  # inclusive of those days.
  # Compare: Elsevier api parameters provide BEF and AFT dates, exclusive of
  # those days.
  # So here, since we are using CrossRef APIs, the cymd_start and
  # cymd_end days are INCLUDED in the API query results.

  cymd_start = '20170306'

  # CRAFATXML - Here, we do only one day at a time...
  cymd_end = '20170824'

  utc_now = datetime.datetime.utcnow()
  # secsz_start: secz means seconds in utc(suffix 'z') when this run started
  secsz_start = utc_now.strftime("%Y-%m-%dT%H-%M-%SZ")

  output_folder_base = etl.data_folder(linux='/home/robert/', windows='U:/',
      data_relative_folder='data/elsevier/output_crafdtxml/')

  print ("START CRAFDTXML RUN at {}\n\twith:\ncymd_start='{}', cymd_end='{}'\n  "
         "output_folder_base={},verbosity={}"
         .format(secsz_start, cymd_start, cymd_end, output_folder_base, verbosity))

  if not os.path.isdir(output_folder_base):
      os.makedirs(output_folder_base)

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
      entries_collected, entries_excepted, uf_articles = crafdtxml(
          d_params, verbosity=verbosity)

  ############### WRAP-UP MISC OUTPUT ################
  # Also record some summary output results in d_params for saving as xml file

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
  etl.add_subelements(e_root, d_params)

  out_filename = '{}/run_crafdxml_{}.xml'.format(output_folder_base, secsz_start)
  os.makedirs(output_folder_base, exist_ok=True)

  with open(out_filename, 'wb') as outfile:
      outfile.write(etree.tostring(e_root, pretty_print=True))
  print('Collected {} articles, excepted {}, and {} were uf articles'
       .format(entries_collected, entries_excepted, uf_articles))
  print("Done!")

# end def run()

# RUN
run()
