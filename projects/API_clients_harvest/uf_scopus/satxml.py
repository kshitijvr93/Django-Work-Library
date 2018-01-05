import sys, os, os.path, platform

def get_path_modules(verbosity=0):
  env_var = 'HOME' if platform.system().lower() == 'linux' else 'USERPROFILE'
  path_user = os.environ.get(env_var)
  path_modules = '{}/git/citrus/modules'.format(path_user)
  if verbosity > 1:
    print("Assigned path_modules='{}'".format(path_modules))
  return path_modules
sys.path.append(get_path_modules())

import etl

from io import StringIO, BytesIO
import shutil

'''
Program satxml (Scopus Api To XML) reads information from Scopus Search API for
UF-Authored (affiliated) articles and for each, it seeks it in the Scopus Full-text API.

NOTE: Scopus has a 5000 article per request maximum. That is why each request is limited to
a subject area, subj_area, and the UF affiliation, to make sure the 5K maximum is not exceeded, otherwise
there would be no known way to get data after the 5000th article in any request. Currently for UF and
subj area of medicine, for pub year 2016, is around 4000 at the end of the year, so if UF gets much more
prolilfic, some UF med articles would be/may become inaccessible via this Scopus API/Policy.

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

class ScopusAPI(object):
    # base url here. Add on apiKey=x
    url_base_content_search = "http://api.elsevier.com/content/search/scopus?"
    # url_search based on 20161025 docs. Note that one result tag, dc:identifier, which
    # provides content: SCOPUS_ID:x, where x is the scopus id of the sought url, parroted back.
    url_base_article_abstract_search = "http://api.elsevier.com/content/abstract/scopus_id/"
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
        # Note: default apiKey is for UF
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

    def initial_search_url_by_affil_pubyear_subjarea(self, affil=None, pubyear=None, subjarea=None):
        if not (affil and pubyear and subjarea):
            raise ValueError('Affil and pubyear and subjarea not all given.')
        return('{}apiKey={}&query=affil({{{}}}) and pubyear is {} and subjarea({})'
               '&httpAccept=application/xml'
               .format(self.url_base_content_search, self.apiKey
               ,affil, pubyear, subjarea))

    def initial_search_url_by_affil_pubyear(self, affil=None, pubyear=None):
        if not (affil and pubyear):
            raise ValueError('Affil and pubyear not all given.')
        search_url_initial = ('{}apiKey={}&query=affil({{{}}}) and pubyear is {}&{}'
               .format(self.url_base_content_search, self.apiKey
               , affil, pubyear,'httpAccept=application/xml'))
        #return etree.parse(search_url_initial)
        return search_url_initial
    def get_url_affiliation_search(self,subject_area=None):
        base_url = 'http://api.elsevier.com/content/search/affiliation'
        d_qparams = self.d_qparams
        d_qparams.update({'query':'affil({University of Florida})'})
        url = '{}?{}'.format(base_url, urllib.parse.urlencode(d_qparams))
        return url

#end class ScopusAPI(object)

#
def scopus_response_entries_collect(sapi=None,d_scopus_info=None, pubyear=None
    , subjarea=None, n_batch=None
    , results_tree=None, d_namespaces=None
    , d_params=None, d_batch=None, verbosity=1):
    '''
    Given d_params input params dictionary and an article search results tree corresponding to
    one 'page' of scopus results (usually 25 entries), loop over the
    tree's entries, where each entry is for a result article.
    We save each entry in file scopus_entry_{scopus_id}.xml,
    and we query the 'full-text' xml api from xxx.

    For each entry/article, we write in the output dir:
    (1) We write a file named entry/scopus_{scopus_id}.xml
    (2) We write a file under doi/doi_{doi-normalized}.xml

    Note: we also could add a dictionary argument used to track incoming pii values
    and reject duplicate pii values across calls here during processing the results of a query,
    but that has not been a problem (so far).

    RETURN values: batch_entries_collected, link_next_batch

    '''
    me = 'scopus_response_entries_collect'
    if not (sapi and subjarea and n_batch and d_params and results_tree and d_batch
        and d_namespaces and d_scopus_info and pubyear):
        #raise ValueError('Missing some required arguments.')
        pass

    #api_key = sapi.apiKey
    output_folder = d_params.get('output_folder','')
    output_folder_pubyear = '{}/{}/'.format(output_folder,d_params['pubyear'])
    output_folder_entry = '{}/entry'.format(output_folder_pubyear)
    output_folder_doi = '{}/doi'.format(output_folder_pubyear)

    # Remove old output folder - we will rewrite the entire year of doi data since
    # the 2016 scopus API only provides a full year date range.
    entry_tag = '{http://www.w3.org/2005/Atom}entry' # could use instead of {*} in '{*}entry' below.
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
    for i,node_entry in enumerate(results_tree.findall('.//{*}entry')):
        # We have the next root entry element in the results tree.
        n_entry += 1
        d_results = {}
        #print("\n\n*** USING n_entry={}, entry={}".format(n_entry, entry.text))
        # tree_entry = etree.ElementTree(entry)
        article_id_tag='dc:identifier'
        article_ids = node_entry.findall(article_id_tag,namespaces=d_namespaces)
        lai = len(article_ids)
        if lai != 1:
            msg = ("Batch {}, entry number {} has {} occurences of {}, the first is {}"
                .format(n_batch, i+1, lai, article_id_tag,
                    (article_ids[0].text if lai > 0 else 'None')))
            print(msg)
            continue

        article_id = article_ids[0].text
        #print("{}: n_entry={},got scopus_id={}".format(me,n_entry,id))
        if not article_id.startswith('SCOPUS_ID:'):
            msg = ("Batch {}, entry number {} skipping -- bad SCOPUS_ID {}"
                .format(batch, i+1, id ))
            print(msg)
            continue

        scopus_id = article_id[10:]

        # Seek or create d_info value for this scopus id
        d_info = d_scopus_info.get(scopus_id, None)
        if d_info is None:
            d_info = {}
            d_scopus_info[scopus_id] = d_info

        d_info['pubyear'] = pubyear
        # Add this subject area as one for this scopus id
        subjareas = d_info.get('subjareas', None)
        if subjareas == None:
            d_info['subjareas'] = subjarea
        else:
            d_info['subjareas'] = subjareas + '|' + subjarea
            # All we had to do was add the new subjarea. Assume all other values are unchanged.
            continue

        # Note: Now - we assume for multiple entry results for same scopus id in a run that all
        # other xml tag values
        # will match - later can add tests here to see whether eid, misc fields, differ
        # from one appearance of a scopus_id to the next...

        #glean the values for specified sapi.tags
        for sought_tag in sapi.tags:
            found_tags = node_entry.findall('{*}' + sought_tag )
            n_found = len(found_tags)
            d_info[sought_tag] = ''
            found_text = ''
            if sought_tag == 'doi':
                if n_found != 1:
                    msg = ("WARN:Scopus_ID {}, Batch {}, entry number {} has {} occurences of tag '{}'"
                        .format(scopus_id, n_batch, i+1, n_found, sought_tag))
                    print(msg)
                    continue
                # CLEAN the doi to prevent future problems from past issues
                # (remove spaces, convert to lowercase)
                found_text = found_tags[0].text.replace(' ','').lower()
            elif n_found > 0:
                found_text = found_tags[0].text
            d_info[sought_tag] = found_text

        # ADD uf-harvest element to this entry with time of this harvesting run
        # to be added to the output of each output doi document
        node_utcz = etree.SubElement(node_entry, "uf-harvest")
        node_utcz.text = sapi.utc_secs_z

        if verbosity > 5:
            print ("\n***** Entry={}, scopus_id={}".format(n_entry, scopus_id))

        # Save the xml subtree for this entry into a separate xml file
        try:
            entry_xml_str = etree.tostring(node_entry, pretty_print=True)
        except:
            e = sys.exc_info()[0]
            print("scopus id={}, etree.tostring exception ={}".format(id,repr(e)))
            continue

        # Write the entry to an output file with DOI-normalized value in the filename.
        node_doi = node_entry.find('./{*}doi')
        if node_doi is not None:
            # Remove a fault (an inserted space) found in some scopus API results
            doi_nospace = node_doi.text.replace(' ','')
            node_doi.text = doi_nospace

            # To construct part of a filename for output, also replace slashes in the doi
            doi_filename_suffix = doi_nospace.replace('/','-')

            entry_xml_str = etree.tostring(node_entry, pretty_print=True)

            output_filename = '{}/doi_{}.xml'.format(output_folder_doi, doi_filename_suffix)

            print('writing to filename={}'.format(output_filename))
            with open(output_filename, 'wb') as outfile:
                outfile.write(entry_xml_str)
        else:
            # print("Missing doi")
            pass

        # Write the entry to an output file with SCOPUS_ID in the filename
        output_filename = '{}/scopus_{}.xml'.format(output_folder_entry, scopus_id)
        with open(output_filename, 'wb') as outfile:
            outfile.write(entry_xml_str)
        # COMING LATER... SEEK FULL TEXT .. for SCOPUS... compare with program eatxml
    # end foreach entry

    return result_link_next, n_entry, n_entry_exceptions, l_retrievals, d_scopus_info
# end scopus_search_response_entries_collect()

'''
From data given in d_scopus_info, write to outfile
'''
def scopus_info_out(d_params, sapi, d_scopus_info):
    utcnow = d_params['run_utcnow']
    ymd_now = d_params['run_ymd']
    pubyear = d_params['pubyear']

    out_filename = ('{}/{}/scopus_{}_{}.txt'.format(
        d_params['output_folder'],pubyear,pubyear,ymd_now))

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

def run_satxml_by_affil_pubyear(affil=None, pubyear=None,d_params=None):
    me="run_satxml_by_affil_pubyear"
    if not (affil and pubyear and d_params):
        raise ValueError("Missing affil or pubyear")
    output_folder = d_params['output_folder']
    sapi = ScopusAPI(af_ids=d_scopus_uf_af_ids)

    d_scopus_info = {}
    n_subjarea = 0
    entries_collected = 0
    entries_excepted = 0
    d_subj_count = {}
    # subjarea = ['arts']
    subjareas = list(sapi.d_subjarea.keys())
    # TEST OVERRIDE ON NEXT LINE....
    # subjareas = subjareas[1:2]
    for subjarea in subjareas:
        n_subjarea += 1
        #TESTBREAK
        #if n_subjarea > 2:
        #    break
        n_batch = 1
        url_next_searchi = sapi.initial_search_url_by_affil_pubyear_subjarea(affil, pubyear,subjarea)
        print("\n{}:Finding articles in SUBJECT AREA: {}\n".format(me, subjarea), file=stdout)

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
              scopus_response_entries_collect(sapi=sapi,
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
            n_batch += 1
        # end while url_nextsearch
    # for subjareas
    d_stats = dict()
    d_params.update({"stats": d_stats})
    d_stats['total_entries_collected'] = str(entries_collected)
    d_stats['total_entries_excepted'] = str(entries_excepted)

    total_articles = 0
    for key, value in d_subj_count.items():
        count = int(value)
        print ("For subject {}: final count = {}".format(key,count), file=sys.stdout)
        total_articles += count

    # Output scopus info selected fields per article
    scopus_info_out(d_params, sapi, d_scopus_info)

    print ("TOTAL YEAR {} COLLECTED ARTICLES  = {}".format(pubyear, total_articles))

    return entries_collected, entries_excepted, d_scopus_info
#end run_satxml

# MAIN - define RUN PARAMS and run it
me = 'main'
# Set two normally changed parameters:
#201703 - use 2017 alone, instead of [2016,2017] because 2016 has sort of settled out by now
pubyears=[2017]
output_folder = 'c:/rvp/elsevier/output_satxml'

# Save also run context parameters
d_params = {}
d_params['scopus_info'] = {}

utcnow = datetime.datetime.utcnow()
d_params['run_utcnow'] = utcnow
d_params['run_ymd'] = utcnow.strftime("%Y_%m_%d")
# Change stdout later to a file, if put this code as a notebook into git.
stdout = sys.stdout
d_params['stdout'] = stdout

d_params['output_folder'] = output_folder
print('{}: using d_params={}'.format(me,repr(d_params)))
#
# create output folder root if it does not exist
os.makedirs(output_folder, exist_ok=True)

for pubyear in pubyears:
    d_params['pubyear'] = pubyear
    output_folder_pubyear = '{}/{}'.format(output_folder, pubyear)
    print('Making output pubyear folder {} if not extant.'.format(output_folder_pubyear))
    os.makedirs(output_folder_pubyear, exist_ok=True)

    output_folder_doi = '{}/{}/doi'.format(output_folder, pubyear)

    # DOIs are tracked by harvest, and each harvest has a full dump of all data so far
    # (because we only query by full pub year),
    # so first remove all doi file from prior harvests for this year
    shutil.rmtree(output_folder_doi, ignore_errors=True)
    # A known bug in os.makedirs makes it fail here, so use workaround in next clause.
    # os.makedirs(output_folder_doi, exist_ok=True)
    if not os.path.isdir(output_folder_doi):
        os.makedirs(output_folder_doi)

    # make folder for output Scopus-id-keyed entry files
    # scopus ids/files are not supposed to ever disappear nor be overwritten, as new scopus ids are
    # created for any updates or new dois. So do not bother to remove them here, though we did for DOIS.
    output_folder_entry='{}/entry'.format(output_folder_pubyear)
    print('Making output entry folder {} if not extant.'.format(output_folder_entry))
    os.makedirs(output_folder_entry, exist_ok=True)

    entries_collected, entries_excepted, d_scopus_info = run_satxml_by_affil_pubyear(
        affil='University of Florida', pubyear=pubyear, d_params=d_params)
    print("Done with pubyear={}. Collected {} and excepted {} article dois"
         .format(pubyear, entries_collected, entries_excepted))
    print('\n\n============================================================\n\n')
print("DONE with all pubyears.")
#
