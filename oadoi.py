#Get local pythonpath of modules from 'citrus' main project directory
import sys, os, os.path, platform, datetime
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


'''
Get an api result for a url decoded as utf-8.
If json_loads is True, read the API result as a JSON result,
so decode it to a Python result and return that.
Otherwise just return the utf-8 result.
'''
def get_result_by_url(url, json_loads=True):

    if url is None or url=="":
        raise Exception("Cannot send a request to an empty url.")
    try:
        print("*** BULDING GET REQUEST FOR API RESULTS FOR URL='{}' ***"
            .format(url))
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
    result = response.read().decode('utf-8')
    if json_loads == True:
        result = json.loads(result)
    return result

def output_oadoi_xml(url_base=None, dois=None, output_folder=None):
    if not all([url_base, dois, output_folder]):
        raise Exception("Bad args")
    me = 'output_oadoi_xml'
    for i,doi in enumerate(dois):
        if doi is None or doi == '':
            continue
        # Some dois from scopus have illegal embedded spaces - remove them
        url_request = '{}/{}'.format(url_base,doi).replace(' ','')
        print("{}:Using url_request='{}'".format(me,url_request))
        sys.stdout.flush()
        d_result = get_result_by_url(url_request)

        #print("{}:Got d_result={}".format(me,repr(d_result)))
        sys.stdout.flush()

        d_entry = d_result['results'][0]
        #print("\n\nGot d_entry={}\n".format(repr(d_entry)))

        # Save the xml as a string
        node_root = etree.Element("entry")
        etl.add_subelements(node_root, d_entry)

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

def run(doi_string):

    secsz_start = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")

    output_folder_run = etl.data_folder(linux='/home/robert/', windows='U:/',
        data_relative_folder='data/outputs/oadoi/run/{}/'
            .format(secsz_start))

    url_base =  'http://api.oadoi.org'

    dois = doi_string.split('\n')
    output_oadoi_xml(url_base=url_base,dois=dois, output_folder=output_folder_run)
    print("Please see output xml files under folder {}. Done!".format(output_folder_run))
#end def run

doi_strings_els_open_access = '''
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

'''use [silodb];
select doi
from e2017b_doc
where uf_affil_count > 0
and open_access = 0
and cover_year = 2017
and doi is not null'''
dois_uf_els_not_open_access='''10.1016/j.jmaa.2016.07.011
10.1016/j.jspi.2016.08.002
10.1016/j.still.2016.07.009
10.1016/B978-0-12-802574-1.01002-4
10.1016/j.paid.2016.07.033
10.1016/j.apergo.2016.07.010
10.1016/j.compstruct.2016.10.132
10.1016/j.jebo.2016.11.005
10.1016/j.pmpp.2016.11.004
10.1016/j.spl.2016.11.003
10.1016/j.jempfin.2016.11.006
10.1016/j.ijhm.2016.09.005
10.1016/j.ccc.2016.08.006
10.1016/j.jembe.2016.11.013
10.1016/j.chb.2016.11.031
10.1016/j.ecoleng.2016.11.027
10.1016/j.quascirev.2016.08.032
10.1016/j.margeo.2016.11.006
10.1016/j.expneurol.2016.11.004
10.1016/j.funeco.2016.10.008
10.1016/j.isprsjprs.2016.11.001
10.1016/j.xjep.2016.10.006
10.1016/j.biomaterials.2016.11.004
10.1016/B978-0-12-805196-2.01002-5
10.1016/j.eja.2016.11.004
10.1016/j.nlm.2016.10.012
10.1016/j.agsy.2016.10.006
10.1016/j.jviromet.2016.11.014
10.1016/j.cropro.2016.11.022
10.1016/j.appet.2016.11.033
10.1016/j.fuel.2016.10.108
10.1016/j.addbeh.2016.11.018
10.1016/j.rser.2016.11.135
10.1016/j.jocrd.2016.11.004
10.1016/B978-0-323-24288-2.00176-8
10.1016/B978-0-12-803623-5.00011-3
10.1016/j.neuropharm.2016.09.018
10.1016/B978-0-12-802168-2.01002-2
10.1016/B978-0-12-803527-6.03001-8
10.1016/B978-0-12-803527-6.01002-7
10.1016/j.ijmultiphaseflow.2016.09.006
10.1016/j.jcis.2016.09.063
10.1016/j.neurobiolaging.2016.09.013
10.1016/j.jss.2016.09.038
10.1016/B978-0-12-802582-6.01002-8
10.1016/j.ijhcs.2016.08.006
10.1016/j.apsusc.2016.08.049
10.1016/j.jhazmat.2016.08.079
10.1016/B978-0-12-802810-0.06001-3
10.1016/j.ympev.2016.08.021
10.1016/j.cam.2016.08.039
10.1016/j.cej.2016.09.122
10.1016/j.gca.2016.09.009
10.1016/j.iheduc.2016.09.002
10.1016/B978-0-12-803237-4.01002-8
10.1016/j.tele.2016.09.007
10.1016/j.patcog.2016.09.045
10.1016/j.jbi.2016.12.008
10.1016/j.ecoenv.2016.11.026
10.1016/j.athoracsur.2016.05.114
10.1016/j.tsf.2016.11.042
10.1016/j.cherd.2016.11.032
10.1016/j.ympev.2016.12.017
10.1016/j.earscirev.2016.12.002
10.1016/j.ijpara.2016.11.002
10.1016/j.foodchem.2016.12.088
10.1016/j.jasrep.2016.09.013
10.1016/j.jacc.2016.11.027
10.1016/j.actatropica.2016.12.024
10.1016/j.jvs.2016.10.020
10.1016/j.jocrd.2016.12.006
10.1016/j.jpeds.2016.08.013
10.1016/j.jvs.2016.10.014
10.1016/j.biortech.2016.12.072
10.1016/j.gloplacha.2016.11.018
10.1016/j.taap.2016.12.014
10.1016/j.exger.2016.12.013
10.1016/j.ecolmodel.2016.11.016
10.1016/j.cvsm.2016.09.003
10.3168/jds.2016-11452
10.1016/j.automatica.2016.09.030
10.1016/j.envres.2016.12.002
10.1016/j.jclepro.2016.12.089
10.1016/j.ajog.2016.11.579
10.1016/j.ajog.2016.11.969
10.1016/j.jalgebra.2016.10.047
10.1016/j.ajog.2016.11.339
10.1016/j.ajog.2016.11.165
10.1016/j.ajog.2016.11.384
10.1016/j.ajog.2016.11.612
10.1016/j.ajog.2016.11.338
10.1016/j.ajog.2016.11.818
10.1016/j.ajog.2016.11.792
10.1016/j.camwa.2016.11.026
10.1016/j.nima.2016.12.016
10.1016/j.jasrep.2016.11.043
10.1016/j.ypmed.2016.12.049
10.1016/j.ijrefrig.2016.12.004
10.1016/j.jhazmat.2016.12.023
10.1016/j.jclepro.2016.12.059
10.1016/j.biochi.2016.11.014
10.1016/j.xjep.2016.11.002
10.1016/B978-0-12-812271-6.00208-8
10.1016/j.vacuum.2016.12.001
10.1016/j.actamat.2016.12.038
10.1016/j.jtbi.2016.12.020
10.1016/j.ijheatmasstransfer.2016.11.092
10.1016/j.agee.2016.12.010
10.1016/j.ecolind.2016.12.015
10.1016/j.polgeo.2016.11.015
10.1016/j.phytochem.2016.12.001
10.1016/j.yhbeh.2016.11.018
10.1016/j.cct.2016.12.011
10.1016/j.oraloncology.2016.12.001
10.1016/j.pscychresns.2016.12.008
10.1016/j.poly.2016.11.046
10.1016/j.ejca.2016.11.022
10.1016/j.ijcard.2016.12.113
10.1016/j.finel.2016.11.006
10.1016/j.bcp.2016.12.010
10.1016/j.chb.2016.12.046
10.1016/j.cpr.2016.12.004
10.1016/j.fcr.2016.12.012
10.1016/j.jss.2016.12.032
10.1016/j.automatica.2016.10.004
10.1016/j.jesp.2016.05.005
10.1016/j.ijepes.2016.06.002
10.1016/B978-0-323-35214-7.00179-7
10.1016/j.jsc.2016.03.009
10.1016/j.jsc.2016.03.007
10.1016/j.mssp.2016.10.002
10.1016/j.archoralbio.2016.10.018
10.1016/j.marstruc.2016.09.005
10.1016/j.ces.2016.10.043
10.1016/j.carbon.2016.10.037
10.1016/j.rser.2016.10.011
10.1016/B978-0-12-802381-5.01002-2
10.1016/B978-0-12-803685-3.01002-8
10.1016/B978-0-08-100154-7.00019-3
10.1016/j.aim.2016.09.034
10.1016/j.actamat.2016.10.005
10.1016/j.eswa.2016.10.029
10.1016/j.fcr.2016.10.004
10.1016/j.indcrop.2016.10.013
10.1016/j.jallcom.2016.09.286
10.1016/j.chemosphere.2016.09.109
10.1016/j.jembe.2016.10.005
10.1016/j.ejmech.2016.10.010
10.1016/j.jallcom.2016.10.037
10.1016/j.foreco.2016.10.042
10.1016/j.physe.2016.10.006
10.1016/j.foodcont.2016.07.014
10.1016/j.foodchem.2016.07.163
10.1016/j.jvs.2016.10.099
10.1016/j.jvs.2016.12.100
10.1016/j.carpath.2017.01.007
10.1016/j.ymgme.2016.11.221
10.1016/j.ymgme.2016.11.158
10.1016/j.ccell.2017.01.001
10.1016/j.ymgme.2016.11.364
10.1016/j.ymgme.2016.11.146
10.1016/j.ymgme.2016.11.335
10.1016/j.agsy.2017.01.025
10.1016/j.compag.2017.01.017
10.1016/j.fpsl.2017.02.001
10.1016/j.amjmed.2017.01.049
10.1016/j.icarus.2017.02.023
10.1016/j.jval.2016.11.008
10.1016/j.tmaid.2017.02.007
10.1016/j.chemosphere.2017.02.124
10.1016/j.scienta.2017.02.018
10.1016/j.agwat.2017.02.015
10.1016/j.jnca.2017.02.012
10.1016/j.gie.2017.02.007
10.1016/j.jpsychires.2017.02.017
10.1016/j.cag.2017.01.006
10.1016/j.beproc.2017.01.020
10.1016/j.scienta.2017.01.054
10.1016/j.fcr.2017.01.013
10.1016/j.measurement.2017.02.028
10.1016/j.jcin.2016.11.047
10.1016/j.tcs.2017.02.001
10.1016/j.fishres.2017.02.007
10.1016/j.foreco.2017.02.026
10.1016/j.ympev.2017.02.007
10.1016/j.clinph.2017.01.024
10.1016/j.oooo.2017.02.008
10.1067/j.cpradiol.2017.02.006
10.1016/j.ecoleng.2017.01.034
10.1016/j.watres.2017.02.052
10.3168/jds.2016-12223
10.1016/j.amjmed.2017.01.035
10.3168/jds.2016-12135
10.1016/j.foreco.2017.02.001
10.1016/j.trb.2017.01.018
10.1016/j.jsbmb.2017.02.006
10.1016/j.gde.2017.01.007
10.1016/j.jamda.2016.12.077
10.1016/j.watres.2017.02.013
10.1016/j.jhydrol.2017.02.039'''

run(dois_uf_els_not_open_access)
