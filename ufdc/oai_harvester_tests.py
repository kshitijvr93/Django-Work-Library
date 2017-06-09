#ufdc oai API tests
#
import sys, os, os.path, platform
sys.path.append('{}/github/citrus/modules'.format(os.path.expanduser('~')))

import requests
import urllib.parse
import json
from lxml import etree
from lxml.etree import tostring
from collections import OrderedDict
import etl

d_server_params = {
    'zenodo': {
        'name' : 'zenodo',
        'url_base': 'https://zenodo.org/oai2d',
        'output_parent' : None,
        'sets' : 'user-genetics-datasets',
    },
    'ufdc': {
        'name' : 'ufdc',
        'url_base': 'http://ufdc.ufl.edu/sobekcm_oai.aspx',
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
        harvest_folder = ('{}/{}/set/{}/records/oai_dc/'
            .format(self.output_parent, self.name, set_name))
        os.makedirs(harvest_folder, exist_ok=True)
        print("Using harvest_folder='{}'".format(harvest_folder))
        url_list = ('{}?verb=ListRecords&set={}&metadataPrefix=oai_dc'
            .format(self.url_base,set_name))

        while (url_list is not None):
            print("Sending request url_list='{}'".format(url_list))
            url_list = None
            pass
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

d_harvest_params = d_server_params['zenodo']

linux='/home/robert/'
windows='U:/'
d_harvest_params['output_parent'] = etl.data_folder(
    linux=linux, windows=windows, data_relative_folder='data/outputs')

harvester = OAIHarvester(d_harvest_params)
harvester.harvest(set_name='user-genetics-datasets')
