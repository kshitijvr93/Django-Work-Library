#ufdc oai API tests
#
import sys, os, os.path, platform, traceback
sys.path.append('{}/github/citrus/modules'.format(os.path.expanduser('~')))

import requests
import urllib.parse
import json
from lxml import etree
from lxml.etree import tostring
from collections import OrderedDict
import etl

d_server_params = {
    'zenodo_oai': {
        'name' : 'zenodo_oai', # Part of output folder path
        'url_base': 'https://zenodo.org/oai2d',
        'output_parent' : None,
        'sets' : 'user-genetics-datasets',
    },
    'ufdc_oai': {
        'name' : 'ufdc_oai', # Part of output folder path
        'url_base': 'http://ufdc.ufl.edu/sobekcm_oai.aspx',
        'output_parent' : None,
        'sets' : 'dloc1',
    },
    'ufdc_devpc': {
        'name' : 'ufdc_devpc', # Part of output folder path
        'url_base': 'http://localhost:52468/sobekcm_oai.aspx',
        'output_parent' : None,
        'sets' : 'dloc1',
    },

}

'''
OAIHarvester is initialized with a dict with details on a known
OAI server. Various paramaters are required which are evident by the __init__
code references made to values in the d_param_val argument
'''

class OAIHarvester():
    def __init__(self, d_param_val=None):
        self.name = d_param_val['name']
        self.url_base = d_param_val['url_base']
        self.output_parent = d_param_val['output_parent']
        if self.output_parent is None:
            raise Exception(ValueError,'Error: output_parent is None')
        os.makedirs(self.output_parent, exist_ok=True)

        # later, populate this from ListMetadataFormats call
        self.l_metadata_format = ['oai_dc']

        self.oai_param = ['verb','set','metadataPrefix']
        self.l_set = []
        self.l_verb = ['ListRecords','ListMetadataFormats',
                       'ListIdentifiers','ListSets','GetRecord']
        self.set_name = None
        return

        '''
        <summary>Harvest the set into xml files in the subforolder named
        by the 'sets/(set_name)' in the output folder</summary>
        <param name='set'> The name of the set to harvest</param>
        '''
    def harvest(self, set_name=None):
        me = 'harvest'
        harvest_folder = ('{}/{}/set/{}/records/oai_dc/'
            .format(self.output_parent, self.name, set_name))
        os.makedirs(harvest_folder, exist_ok=True)
        print("Using harvest_folder='{}'".format(harvest_folder))
        url_list = ('{}?verb=ListRecords&set={}&metadataPrefix=oai_dc'
            .format(self.url_base,set_name))
        # url_list='http://localhost:52468/sobekcm_oai.aspx?verb=ListRecords&set=dloc1&metadataPrefix=oai_dc&resumptionToken=000957UFDCdloc1:oai_dc'
        # n_batch = 956
        n_batch = 0
        while (url_list is not None):
            n_batch += 1
            print("{}:For batch {}, sending url_list request={}".format(me,n_batch,url_list))
            response = requests.get(url_list)

            xml = response.text.encode('utf-8')
            print("{}:Request={},Reponse has text len={}".format(me,url_list,len(xml)))

            try:
                node_root = etree.fromstring(response.text.encode('utf-8'))
            except Exception as e:
                print("For batch {}, made url request ='{}'. Skipping batch with Parse() exception='{}'"
                      .format(n_batch, url_list, repr(e)))

                print("Traceback: {}".format(traceback.format_exc()))
                # Break here - no point to continue because we cannot parse/discover the resumptionToken
                break
            #str_pretty = etree.tostring(node_root, pretty_print=True)
            d_namespaces = {key:value for key,value in dict(node_root.nsmap).items() if key is not None}
            nodes_record = node_root.findall(".//{*}record", namespaces=d_namespaces)

            print ("ListRecords request found root tag name='{}', and {} records"
                   .format(node_root.tag, len(nodes_record)))
            node_resumption = node_root.find('.//{*}resumptionToken', namespaces=d_namespaces)
            url_list = None
            if node_resumption is not None:
                url_list = ('{}?verb=ListRecords&set={}&metadataPrefix=oai_dc&resumptionToken={}'
                    .format(self.url_base, set_name, node_resumption.text))
            print("{}:Next url='{}'".format(me,url_list))
            #Set to url_list to None for testing

        return
    '''
    set params - and set the self.url
    '''
    def set_params(self, d_params):
        sep = '?'
        self.url = self.url_base
        for key, value in [ (pname, d_params.get(pname,None)) for pname in self.param_names ] :
            #ignore a param if it is not meaningful for oai url
            if value is None:
                continue
            #Later, add validations, eg a verb param may be a limited set of values per OAI specs
            self.url = self.url + sep + key + '=' + value
            sep = '&'
        #reset the url
        return

    # end class OAIHarvester

d_harvest_params = d_server_params['ufdc_oai']
#d_harvest_params = d_server_params['ufdc_devpc']
set_name = 'dloc1'
set_name = 'CNDL'

linux='/home/robert/'
windows='U:/'
d_harvest_params['output_parent'] = etl.data_folder(
    linux=linux, windows=windows, data_relative_folder='data/outputs')

harvester = OAIHarvester(d_harvest_params)
harvester.harvest(set_name=set_name)
