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
http://api.crossref.org/works?filter=affiliation:University%20of%20Florida,from-index-date:2016-12-01,until-index-date:2016-12-01
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
def crawdxml(d_params=None, file_name_doi_strings=None, verbosity=0):
    #
    # VALIDATE d_params
    # dt_start is the first orig-load-date that we want to collect
    # dt_end is the last orig-load dates that we want to collect
    me = 'crawdxml'
    if not d_params and file_name_doi_strings:
        raise Exception("Missing arg d_params or file_name_doi_strings")

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
    input_file = open(file_name_doi_strings, 'r')

    for line in input_file:
        doi_string = line.replace('\n','')

        url_worklist_doi = (
            "http://api.crossref.org/works/doi/{}".format(doi_string))
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
    # end for doi_string in l_dois:
    # Return n good and n bad
    return entries_collected, entries_excepted
# end def crawdxml

# doi_strings 2017 open access articles
file_name_doi_strings = 'U:/data/tmp/aus20170601_20170824_cross_doi.txt'
#
doi_strings = '''
10.1016/j.ijheatmasstransfer.2016.11.032
10.1016/j.ecolmodel.2016.11.015
10.1016/j.softx.2016.12.002
10.1016/j.omtm.2016.12.003
10.1016/j.epsl.2016.11.054
10.1016/j.pmedr.2016.12.008
10.1016/j.omto.2016.12.002
10.1016/j.visj.2016.10.004
10.1016/j.pcorm.2016.12.004
10.1016/j.physletb.2016.12.017
10.1016/j.jdcr.2016.10.002
10.1016/S0140-6736(16)32621-6
10.1016/j.cbpa.2016.12.005
10.1016/j.eucr.2016.11.002
10.1016/j.chb.2016.09.030
10.1016/j.bbadis.2016.09.020
10.1016/j.jik.2016.12.006
10.1016/j.jns.2017.02.042
10.1016/j.ijpddr.2017.02.002
10.1016/j.colsurfb.2017.02.025
10.1016/j.gecco.2016.12.005
10.1016/j.yebeh.2016.11.022
10.1016/j.aaf.2017.01.004
10.1016/j.rbo.2016.11.006
10.1016/j.gdata.2017.02.011
10.1016/j.apgeog.2017.02.009
10.1016/j.cja.2017.01.002
10.1016/j.ijwd.2017.02.012
10.1016/j.tree.2017.01.007
10.1016/j.rmcr.2017.02.015
10.1016/j.rse.2017.01.037
10.1016/j.cja.2017.02.005
10.1016/j.radcr.2017.01.008
10.1016/j.ekir.2017.02.002
10.1016/j.ymthe.2017.01.015
10.1016/j.amepre.2016.10.001
10.1016/j.nicl.2017.02.012
10.1016/j.amepre.2016.10.011
10.1016/j.rse.2017.01.039
10.1016/j.cellsig.2017.02.002
10.1016/j.physletb.2017.02.032
10.1016/j.ymthe.2016.11.009
10.1016/j.idcr.2017.02.002
10.1016/j.celrep.2017.01.019
10.1016/j.ijrobp.2017.05.014
10.1016/j.ijge.2016.06.003
10.1016/j.nicl.2017.05.001
10.1016/j.xocr.2017.05.001
10.1016/j.epsc.2017.05.014
10.1016/j.hemonc.2017.04.002
10.1016/j.dsr.2017.05.002
10.1016/j.pmedr.2017.05.006
10.1016/j.molmet.2017.05.001
10.1016/j.physletb.2017.05.045
10.1016/j.redox.2017.05.007
10.1016/j.ympev.2017.05.014
10.1016/j.jsamd.2017.05.008
10.1016/j.envpol.2017.05.019
10.1016/j.landurbplan.2017.05.004
10.1016/j.jpain.2017.02.421
10.1016/j.ajem.2017.05.002
10.1016/j.jacc.2017.03.528
10.1016/j.jdcr.2017.03.007
10.1016/j.tranon.2017.03.009
10.1016/j.trci.2017.04.006
10.1016/j.fiae.2017.03.003
10.1016/j.epidem.2017.03.006
10.1016/j.ajhg.2017.04.003
10.1016/j.gsf.2017.05.001
10.1016/j.celrep.2017.05.018
10.1016/j.visj.2017.04.011
10.1016/j.ejop.2017.05.005
10.1016/j.sajce.2017.05.001
10.1016/j.trpro.2017.03.009
10.1016/j.rvsc.2017.05.021
10.1016/j.trpro.2017.03.055
10.1016/j.trpro.2017.03.046
10.1016/j.trpro.2017.03.027
10.1016/j.adro.2017.05.004
10.1016/j.jse.2017.03.013
10.1016/j.compedu.2017.05.006
10.1016/j.rmcr.2017.05.003
10.1016/j.parepi.2017.05.001
10.1016/j.ijinfomgt.2017.04.006
10.1016/j.dib.2017.05.047
10.1016/j.physletb.2017.07.062
10.1016/j.dsr2.2017.08.008
10.1016/j.jfda.2017.07.013
10.1016/j.epsc.2017.08.016
10.1016/j.jctube.2017.08.002
10.1016/j.physletb.2017.08.015
10.1053/j.ajkd.2017.07.004
10.1016/j.conctc.2017.08.005
10.1016/j.idcr.2017.08.011
10.1016/j.physletb.2017.08.027
10.1016/j.livres.2017.08.002
10.1016/j.parkreldis.2017.08.006
10.1016/j.jdcr.2017.05.008
10.1016/j.rinp.2017.08.023
10.1016/j.leukres.2017.07.008
10.1016/j.celrep.2017.07.018
10.1016/j.marpol.2017.08.004
10.1016/j.ebiom.2017.08.010
10.1016/j.jsamd.2017.07.010
10.1016/j.agsy.2017.07.010
10.1016/j.artd.2017.06.008
10.1016/j.jams.2017.08.002
10.1016/j.adro.2017.07.004
10.1016/j.ijppaw.2017.08.003
10.1016/j.tjog.2017.04.037
10.1016/j.dcn.2017.08.001
10.1016/j.conctc.2017.04.003
10.1016/j.omtm.2017.04.004
10.1016/j.jlumin.2017.04.017
10.1016/j.ttbdis.2017.04.009
10.1016/j.celrep.2017.04.003
10.1016/j.rinp.2017.03.022
10.1016/j.jvsv.2016.12.016
10.1016/j.euf.2017.04.005
10.1016/j.afjem.2017.04.005
10.1016/j.pvr.2017.04.004
10.1016/j.radcr.2017.03.004
10.1016/j.procs.2017.03.160
10.1016/j.cub.2017.04.002
10.1016/j.rausp.2017.02.001
10.1016/j.expneurol.2017.04.015
10.1016/j.curtheres.2017.04.004
10.1016/j.physletb.2017.04.069
10.1016/j.ijcha.2017.03.005
10.1016/j.heliyon.2017.e00279
10.1016/j.trecan.2017.03.003
10.1016/j.eucr.2016.05.009
10.1016/j.ymthe.2017.03.029
10.1016/j.eucr.2017.02.014
10.1016/j.ymgme.2017.04.013
10.1016/j.aap.2017.03.015
10.1016/j.radcr.2017.03.022
10.1016/j.adro.2017.01.006
10.1016/j.abrep.2017.01.002
10.1016/j.jbi.2016.12.013
10.1016/j.asej.2016.08.017
10.1016/j.proeps.2017.01.001
10.1016/j.abrep.2017.01.003
10.1016/j.amjcard.2016.11.066
10.1016/j.tourman.2016.12.014
10.1016/j.taml.2017.01.004
10.1016/j.joems.2016.11.001
10.1016/j.tjem.2016.11.007
10.1016/j.biocon.2017.01.007
10.1016/j.fcr.2016.12.004
10.1016/j.aej.2016.11.008
10.1016/j.bjan.2016.05.002
10.1016/j.hpj.2017.01.002
10.1016/j.pmedr.2017.01.004
10.1016/j.ymgme.2017.01.001
10.1016/j.pmedr.2017.01.009
10.1016/j.critrevonc.2017.01.005
10.1016/j.agsy.2017.05.006
10.1016/j.aqrep.2017.06.002
10.1016/j.mehy.2017.06.016
10.1016/j.ebiom.2017.06.014
10.1016/j.trci.2017.06.003
10.1016/j.ekir.2017.06.009
10.1016/j.jhep.2017.06.011
10.1016/j.jtbi.2017.06.013
10.1016/j.omtn.2017.06.011
10.1016/j.wjorl.2017.05.001
10.1016/j.ijscr.2017.06.032
10.1016/j.jdcr.2017.05.001
10.1016/j.trpro.2017.05.314
10.1016/j.trpro.2017.05.218
10.1016/j.trpro.2017.05.319
10.1016/j.celrep.2017.06.006
10.1016/j.dib.2017.06.040
10.1016/j.hrthm.2017.06.020
10.1016/j.jip.2017.06.002
10.1016/j.trpro.2017.05.002
10.1016/j.amjcard.2017.06.023
10.1016/j.hemonc.2017.05.012
10.1016/j.procs.2017.05.176
10.1016/j.procs.2017.05.260
10.1016/j.scitotenv.2017.06.002
10.1016/j.addr.2017.06.002
10.1016/j.procs.2017.05.053
10.1016/S2214-109X(17)30215-2
10.1016/j.ajoc.2017.06.002
10.1016/j.cyto.2017.05.024
10.1016/j.idcr.2017.06.012
10.1016/j.ijpe.2017.06.032
10.1016/j.ijscr.2017.06.003
10.1016/j.dib.2017.03.024
10.1016/j.eucr.2016.11.004
10.1016/j.urolonc.2017.01.025
10.1016/j.conctc.2017.03.002
10.1016/j.radcr.2017.02.002
10.1016/j.eucr.2017.02.009
10.1016/j.ymthe.2017.02.017
10.1016/j.jns.2017.03.030
10.1016/j.joca.2017.03.006
10.1016/j.diin.2017.02.002
10.1016/j.apmr.2017.02.001
10.3168/jds.2016-11815
10.1016/j.cois.2017.03.003
10.1016/j.jmpt.2017.02.001
10.1016/j.quageo.2017.03.001
10.1016/j.omtm.2017.02.004
10.1016/j.ccc.2016.12.008
10.1016/j.jdcr.2017.01.026
10.1016/j.pecon.2017.02.002
10.1016/j.dib.2017.03.008
10.1016/j.rmcr.2017.03.018
10.1016/j.rbms.2017.03.001
10.1016/j.ijppaw.2017.03.001
10.1016/j.aaf.2017.03.002
10.1016/j.eucr.2017.03.003
10.3168/jds.2016-12103
10.1016/j.urolonc.2017.03.008
10.1016/j.jcde.2017.03.002
10.1016/j.jvs.2016.12.136
10.1016/j.stemcr.2017.03.002
10.1016/j.jdcr.2017.01.008
10.1016/j.nefroe.2016.12.009
10.1016/j.jacl.2017.03.007
10.1016/j.omtm.2017.03.005
10.1016/j.fertnstert.2017.01.022
10.1016/j.anres.2016.12.008
10.1016/j.jesf.2017.07.001
10.1016/j.prro.2017.07.008
10.1016/j.jdcr.2017.03.009
10.1016/j.onehlt.2017.07.001
10.1016/j.hrcr.2017.07.001
10.1016/j.desal.2017.07.012
10.1016/j.ecoleng.2017.07.012
10.1016/j.omtm.2017.07.003
10.1016/j.epsc.2017.07.007
10.1016/j.anres.2017.04.002
10.1016/j.dib.2017.07.035
10.1016/j.vetimm.2017.07.004
10.1016/j.pneurobio.2017.07.004
10.1016/j.hrthm.2017.07.008
10.1016/j.eucr.2017.06.013
10.1016/j.jfda.2017.06.002
10.1016/j.jcrc.2017.07.047
10.1016/j.ebiom.2017.07.008
10.1016/j.idcr.2017.06.014
10.1016/j.procs.2017.06.119
10.1016/j.procs.2017.06.115
10.1016/j.rbe.2017.06.006
10.1016/j.hkjot.2017.06.001
10.1016/j.jped.2017.06.002
10.1016/j.heliyon.2017.e00344
10.1016/j.eujim.2017.07.005
10.1016/j.ihj.2017.07.014
10.1016/j.joep.2017.07.009
10.1016/j.jacc.2017.06.012
10.1016/j.solener.2017.07.064'''

'''
def run() takes a single parameter, doi_strings, like:
doi_strings=***
abc
def
ghi
klm***

Using that form make it easier to quickly copy-paste a list of dois to
support a quick run

'''

def run(input_file_name='u:/data/tmp/cross_doi_20170601_20170824.txt'):
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

    print("{}: Reading input file = {}".format(me,input_file_name))

    print ("START CRAWDXML RUN at {}\n, using output_folder_run={}"
           .format(secsz_start,  output_folder_run))

    if not os.path.isdir(output_folder_run):
        os.makedirs(output_folder_run)

    worker_threads = 1 # TODO
    # Dict of metadata run parameter info on this run
    d_params={
        "secsz_start": secsz_start,
        "input_file_name" : input_file_name,
        "doi_strings" : doi_strings,
        "output_folder_run" : output_folder_run,
        "python_version" : sys.version,
        "max-queries" : "0", # TODO
        }

    # Process the Elsevier Search and Full-Text APIs to create local xml files
    entries_collected = 0
    entries_excepted = 0

    ###### MAIN CALL TO CRAWDXML() ########

    if (1 == 1): # test with or without call to crawdxml
        entries_collected, entries_excepted = crawdxml(d_params=d_params,
          file_name_doi_strings=file_name_doi_strings,
          verbosity=verbosity)

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
#end def run()

#run
run(doi_strings)
#
