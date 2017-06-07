#ufdc oai API tests
#
import os
import sys
print("Using python sys.version={}".format(sys.version))

import requests
import urllib.parse
import json
from lxml import etree
from lxml.etree import tostring
from collections import OrderedDict


#from etl import get_result_by_url
###
doi_string = '''
10.1115/ICONE24-60736

also see specs at: https://www.openarchives.org/OAI/openarchivesprotocol.html
'''

class OAIHarvester():
    def __init__(self, url_base=None, d_params=None):
        self.url_base = url_base
        self.param_names = ['verb','set','metadataPrefix']
        self.url = None
        self.l_metadataPrefix = ['oai_dc', ]

        self.l_verb = ['ListSets','ListRecords','ListMetadataFormats','ListIdentifiers']
        if d_params is not None:
            self.set_params(d_params)
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

d_uf_dloc_params = {'set':'user-genetics-datasets', 'verb':'ListRecords',
    'metadataPrefix':'oai_dc'}
d_uf_dloc_params = {'set':'user-genetics-datasets', 'verb':'ListIdentifiers',
    'metadataPrefix':'marcxml'}
d_uf_dloc_params = {'set':'user-genetics-datasets', 'verb':'ListRecords',
    'metadataPrefix':'marcxml'}


harvester = OAIHarvester(url_base= 'https://zenodo.org/oai2d')

harvester.set_params(d_params={'set':'user-genetics-datasets', 'verb':'ListMetadataFormats',
    'metadataPrefix':'oai_dc'})
print("Got harvester.url={}".format(harvester.url))


harvester = OAIHarvester(url_base= 'http://ufdc.ufl.edu/sobekcm_oai.aspx')

d_uf_dloc_params = {'set':'dloc1', 'verb':'ListRecords',
    'metadataPrefix':'oai_dc'}

harvester.set_params(d_params=d_uf_dloc_params)
print("Got harvester.url={}".format(harvester.url))




#output_folder = etl.data_folder(linux='/home/robert', windows='U:/', data_relative_folder='data/outputs/zenodo')
