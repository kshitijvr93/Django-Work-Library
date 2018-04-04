# eamxml - Elsevier Author Manuscripts to XML (eamxml)
# based on satxml python 3 program, as of 20161122
# This is python 3.5.1 code
#
import sys
#import requests
import urllib, urllib.parse
import json
import pprint
from collections import OrderedDict
from io import StringIO, BytesIO

'''
Program eamxml (Elsevier Author Manuscript api to XML) reads information from
Elsevier Author Manuscript Search API for
UF-Authored (affiliated) articles and for each, it seeks it in the
Scopus Full-text API.

If not found, it logs an error message, otherwise it outputs a file named
scopus_{scopus_id}.xml in the given output directory for each article.

'''
from lxml import etree
#Note: Official Python 3.5 docs use different library, ElementTree ET
#Maybe try it if lxml shows flaws -- update: lxml shows no flaws so far after months of use
import xml.etree.ElementTree as ET
from pathlib import Path
import datetime
import pytz
import os

# d_scopus_uf_af_ids is From email from Alexandra Lange of 20161026 AM:
d_scopus_uf_af_ids= {
     '140523': 'University of Florida'
    ,'19249': 'University of Florida College of Medicine'
    ,'2976': 'University of Florida Health Science Center'
    ,'2270': 'University of Florida College of Dentistry'
    ,'663': 'Gulf Coast Research and Education Center'
    ,'501': 'University of Florida Institute of Food and Agricultural Sciences'
    ,'474': 'North Florida Research and Education Center'
}

class EamAPI(object):
    # base url here. Add on apiKey=x
    url_base_content_search = "http://api.elsevier.com/content/search/scidir?"
    utc_created = datetime.datetime.utcnow()
    utc_secs_z = utc_created.strftime("%Y-%m-%dT%H:%M:%SZ")
    article_id_tag='{*}eid'
    tags = ['eid','doi','pii','coverDate','title','creator','publicationName','source-id',
                   'subtype','subtypeDescription']
    d_subjarea = {
    'agri': 'Agricultural and Biological Sciences'
    ,'arts': 'Arts and Humanities'
    ,'bioc' : 'Biochemistry, Genetics and Molecular Biology'
    ,'busi' : 'Business, Management and Accounting'
    ,'ceng' : 'Chemical Engineering'
    ,'chem' : 'Chemistry'
    ,'comp' : 'Computer Science'
    ,'deci' : 'Decision Sciences'
    ,'dent' : 'Dentistry'
    ,'eart' : 'Earth and Planetary Sciences'
    ,'econ' : 'Economics, Econometrics and Finance'
    ,'ener' : 'Energy'
    ,'engi' : 'Engineering'
    ,'envi' : 'Environmental Science'
    ,'heal' : 'Health Professions'
    ,'immu': 'Immunology and Microbiology'
    ,'mate': 'Materials Science'
    ,'math': 'Mathematics'
    ,'medi': 'Medicine'
    ,'neur': 'Neuroscience'
    ,'nurs': 'Nursing'
    ,'phar' : 'Pharmacology, Toxicology and Pharaceutics'
    ,'phys' : 'Physics and Astronomy'
    ,'psyc': 'Psychology'
    ,'soci': 'Social Sciences'
    ,'vete': 'Veterinary'
    ,'mult': 'Multidisciplinary'
    }

    # Maintain a sorted dict
    d_subjarea = OrderedDict(sorted(d_subjarea.items()))

    def __init__(self, apiKey='d91051fb976425e3b5f00750cbd33d8b', af_ids=None):
        # Note: default apiKey is for UF -
        # NOTE: af_ids is not used yet, but maybe later...
        if af_ids is None:
            af_ids = [{'test_af_id':'test'}]
        if not apiKey or not af_ids:
            raise ValueError("apiKey or af_ids argument is not given")
        # apiKey is the spelling used in the url paramter, so keep that naming convention for consistency.
        self.apiKey = apiKey
        self.af_ids = af_ids
        self.d_qparams = {'httpAccept':'application/xml', 'apiKey':apiKey}

    def get_url_author_affiliation_by_scopus_id(self, scopus_id=None):
        return ("{}/{}?field=author,affiliation;apiKey={}"
               .format(self.url_base_article_abstract_search
                       ,scopus_id, self.apiKey))
    def get_url_search_by_affil_pubyear(self, affil=None, pubyear=None):
        if not (affil and pubyear):
            raise ValueError('Affil and pubyear not all given.')
        return('{}apiKey={}&query=affil({{{}}}) and pubyear is {}&httpAccept={}'
               .format(self.url_base_content_search, self.apiKey
               , affil, pubyear,'application/xml'))

    def initial_search_url_by_affil_aft_bef_pubdate(self, affil=None,
            aft_pubdate=None, bef_pubdate=None):
        if not (affil and aft_pubdate and bef_pubdate):
            raise ValueError('Affil and pubyear not all given.')
        return('{}apiKey={}&query=affil({{{}}}) and pub-date AFT {} AND pub-date BEF {}'
               '&view=COMPLETE&httpAccept={}'
               .format(self.url_base_content_search, self.apiKey
               ,affil, aft_pubdate, bef_pubdate,'application/xml'))


    def initial_search_url_by_affil_pubyear_subjarea(self, affil=None, pubyear=None, subjarea=None):
        if not (affil and pubyear and subjarea):
            raise ValueError('Affil and pubyear and subjarea not all given.')
        return('{}apiKey={}&query=affil({{{}}}) and pubyear is {} and subjarea({})'
               '&httpAccept=application/xml'
               .format(self.url_base_content_search, self.apiKey
               , affil, pubyear, subjarea))

    def initial_search_url_by_affil_pubyear(self, affil=None, pubyear=None):
        if not (affil and pubyear):
            raise ValueError('Affil and pubyear not all given.')
        search_url_initial = ('{}apiKey={}&query=affil({{{}}}) and "
           "pubyear is {}&view=COMPLETE&{}'
           .format(self.url_base_content_search, self.apiKey
             ,affil, pubyear,'httpAccept=application/xml'))
        #return etree.parse(search_url_initial)
        return search_url_initial
    def get_url_affiliation_search(self,subject_area=None):
        base_url = 'https://api.elsevier.com/content/search/affiliation'
        d_qparams = self.d_qparams
        d_qparams.update({'query':'affil({University of Florida})'})
        url = '{}?{}'.format(base_url, urllib.parse.urlencode(d_qparams))
        return url
#end class EamAPI(object)

#
def eam_response_entries_collect(eam_api=None,d_scopus_info=None, pubyear=None
    , subjarea=None, n_batch=None
    , results_tree=None, d_namespaces=None
    , d_params=None, d_batch=None, verbosity=1):
    '''
    Given d_params dictionary and an article search results tree corresponding to
    one 'page' of scopus results (usually 25 entries), loop over the
    tree's entries, where each entry is for a result article.
    We save each entry in file scopus_entry_{scopus_id}.xml,
    and we query the 'full-text' xml api from xxx.

    We write an file named scopus_full_{scopus_id}.xml in the output dir for each entry/article.

    Note: we also could add a dictionary argument used to track incoming pii values
    and reject duplicate pii values across calls here during processing the results of a query,
    but that has not been a problem (so far).

    RETURN values: batch_entries_collected, link_next_batch

    '''

    me = 'eam_response_entries_collect'
    if not (eam_api and n_batch and d_params and results_tree and d_batch and d_namespaces
           and d_scopus_info and pubyear):
        #raise ValueError('Missing some required arguments.')
        pass

    out_base_dir = d_params.get('output_folder','')
    output_folder = '{}/{}/'.format(out_base_dir,d_params['aft_pubdate'][0:4])

    # entry_tag = '{http://www.w3.org/2005/Atom}entry' # could use instead of {*} in '{*}entry' below.
    result_link_next = ""

    result_root = results_tree.getroot()
    for link in results_tree.findall('{*}link'):
        d_attrib = dict(link.attrib)

        # parse out the link that will return the results tree for the next batch of results of this query.
        if d_attrib.get("ref", "") == "next":
            result_link_next = d_attrib.get("href","")
            # print("{results_entries_collect}: result_link_next='{}'".format(me,result_link_next))

    l_retrievals = []
    d_batch['full-retrieval-result'] = l_retrievals
    n_entry = 0
    n_entry_exceptions = 0
    #results_str = etree.tostring(entry, pretty_print=True)
    #print("\nGot Search Result: {}\n".format(results_str)
    for i,entry in enumerate(results_tree.findall('.//{*}entry')):
        # We have the next root entry element in the results tree.
        n_entry += 1
        d_results = {}
        #print("\n\n*** USING n_entry={}, entry={}".format(n_entry, entry.text))
        # tree_entry = etree.ElementTree(entry)
        article_id_tag='dc:identifier'
        article_id_tag='{*}pii'
        article_ids = entry.findall(article_id_tag,namespaces=d_namespaces)
        lai = len(article_ids)
        if lai != 1:
            msg = ("Batch {}, entry number {} has {} occurences of {}, the first is {}"
                .format(n_batch, i+1, lai, article_id_tag, (article_ids[0].text if lai > 0 else 'None')))
            print(msg)
            continue

        article_id = article_ids[0].text.replace('-','').replace('(','').replace(')','').replace('.','')
        # Save the xml subtree for this entry into a separate xml file
        try:
            entry_xml_str = etree.tostring(entry, pretty_print=True)
        except Exception as e:
            e = sys.exc_info()[0]
            print("id={}, etree.tostring exception ={}".format(id,repr(e)))
            continue

        # Write the entry to an output file
        output_folder_entry = d_params['output_folder_entry']
        output_filename_entry = '{}/pii_{}.xml'.format(output_folder_entry, article_id)
        with open(output_filename_entry, 'wb') as outfile:
            outfile.write(entry_xml_str)
        # COMING LATER... SEEK FULL TEXT .. for SCOPUS... compare with program eatxml
    # end foreach entry

    return result_link_next, n_entry, n_entry_exceptions, l_retrievals, d_scopus_info
# end eam_search_response_entries_collect()

def eam_info_out(d_params, eam_api, d_scopus_info):

    # Write summary stats to outfile
    utcnow = datetime.datetime.utcnow()
    y_m_d_now = utcnow.strftime("%Y_%m_%d")

    out_filename = ('{}/scopus_{}_{}.txt'.format(
        d_params['output_folder_pubyear'],d_params['pubyear'],y_m_d_now))

    with open(out_filename, 'w', encoding='utf-8') as outfile:
        d=''
        row = ''
        # fix later: this hard codes info on header names
        tags = ['scopus_id','pubyear','subjareas']
        tags.extend(list(sapi.tags))
        print ("writing header row using tags={}".format(tags))
        for tag in tags:
            row += (d + tag)
            d='\t'
        print(row,file=outfile)

        for scopus_id, d_info in d_scopus_info.items():
            row = ("{}\t{}\t{}".format(
                scopus_id,d_info['pubyear'],d_info['subjareas']))
            for tag in sapi.tags:
                row += ('\t' + d_info[tag])
            print(row, file=outfile)

    print("Wrote file {} of scopus info for {} unique articles"
          .format(out_filename,len(d_scopus_info)))
    return
#end def scopus_info_out(d_params, sapi):

def run_eamxml(affil=None, aft_pubdate=None,bef_pubdate=None, output_folder=None):
    me="run_eamxml"
    if not (affil and aft_pubdate and bef_pubdate and output_folder):
        raise ValueError("Missing affil or pubyear")
    eam_api = EamAPI(af_ids=d_scopus_uf_af_ids)
    #TEST - just create the url and print it...? no, do it in another cell..
    # create output directory root if it does not exist
    os.makedirs(output_folder, exist_ok=True)

    output_folder_pubyear = '{}/{}'.format(output_folder_base, pubyear)
    # make output folder for pubyear
    print('Making pubyear directory {} if not extant.'.format(output_folder_pubyear))

    os.makedirs(output_folder_pubyear, exist_ok=True)

    # make folder for output entry files
    output_folder_entry='{}/entry'.format(output_folder_pubyear)
    print('Making entry directory {} if not extant.'.format(output_folder_entry))
    os.makedirs(output_folder_entry, exist_ok=True)

    d_params = {}
    d_scopus_info = {}
    d_params['affil'] = affil
    d_params['aft_pubdate'] = aft_pubdate
    d_params['bef_pubdate'] = bef_pubdate
    d_params['output_folder'] = output_folder
    d_params['output_folder_pubyear'] = output_folder_pubyear
    d_params['output_folder_entry'] = output_folder_entry
    print('{}: using d_params={}'.format(me,repr(d_params)))

    n_subjarea = 0
    entries_collected = 0
    entries_excepted = 0
    d_subj_count = {}
    # subjarea = ['arts']
    subjareas = ['test']
    for subjarea in subjareas:
        n_subjarea += 1
        #TESTBREAK
        #if n_subjarea > 2:
        #    break
        n_batch = 1
        url_next_search= eam_api.initial_search_url_by_affil_aft_bef_pubdate(
            affil,aft_pubdate=aft_pubdate, bef_pubdate=bef_pubdate)
        print("\nFinding EAM articles in SUBJECT AREA: {}\n".format(subjarea))


        while (url_next_search):
            print ('{}:n_batch={}, using search_url={}'.format(me,n_batch,url_next_search))

            try:
                results_tree = etree.parse(url_next_search)

            except:
                e = sys.exc_info()[0]
                msg = ('Skipping: Cannot parse url={}. Error is {}'.format(url_next_search,e))
                continue

            results_root = results_tree.getroot()
            d_ns = {key:value for key,value in dict(results_root.nsmap).items() if key is not None}

            #print("{}: got results_tree = {}".format(me,results_tree))
            batch_key = 'b'+str(n_batch).zfill(5)
            d_batch = {}
            #d_batches[batch_key] = d_batch

            # PROCESS THE SEARCH RESULTS ENTRY DATA GIVEEN IN results_tree FOR THIS BATCH OF ARTICLES
            (url_next_search, n_collected, n_excepted, l_retrievals,d_scopus_info) = (
              eam_response_entries_collect(eam_api=eam_api,
                d_scopus_info=d_scopus_info, pubyear=pubyear, subjarea=subjarea
                , n_batch=n_batch
                , results_tree=results_tree, d_namespaces=d_ns
                , d_params=d_params, d_batch=d_batch))

            entries_collected += n_collected
            entries_excepted += n_excepted
            d_subj_count[subjarea] = d_subj_count.get(subjarea,0) + n_collected
            d_batch['n_entries_collected'] = str(n_collected)
            d_batch['n_entries_excepted'] = str(n_excepted)

            #print ("{}:Subj {}, Batch {}: Total entries_collected so far = {}, exceptions = {}"
            #      .format(me, subjarea, n_batch, str(entries_collected), str(entries_excepted)))
            #TESTBREAK
            #break
            n_batch += 1
        # n_batch -= 1
    # for subjareas
    d_stats = dict()
    d_params.update({"stats": d_stats})
    d_stats['total_entries_collected'] = str(entries_collected)
    d_stats['total_entries_excepted'] = str(entries_excepted)

    total_articles = 0
    for key, value in d_subj_count.items():
        count = int(value)
        print ("For subject {}: final count = {}".format(key,count))
        total_articles += count

    # Output scopus info selected fields per article
    #eam_info_out(d_params, eam_api, d_scopus_info)

    print ("TOTAL YEAR {} COLLECTED ARTICLES  = {}".format(pubyear, total_articles))

    return entries_collected, entries_excepted, d_scopus_info
#end run_rsmxml

# RUN
pubyear=2016
aft_pubdate="2016-11-29"
bef_pubdate="2016-11-21"
output_folder_base = 'c:/rvp/elsevier/output_eamxml'

entries_collected, entries_excepted, d_scopus_info = run_eamxml(
    affil='University of Florida', aft_pubdate=aft_pubdate,
    bef_pubdate=bef_pubdate, output_folder=output_folder_base)
