
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
import time
import urllib.parse

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

'''
def gen_entitlment_nodes_by_piis:

From a list of pii values (with a  maximum of 100 in the list),
generate an Elsevier entitlement request and yield a tuple of
node_entitlement and d_namespaces context data for use by lxml methods.
'''

def gen_entitlement_nodes_by_piis(piis=None,verbosity=1):
    me = 'gen_entitlement_nodes_by_piis'

    if len(piis) == 0:
      return #OK, Done.
    if len(piis) > 100:
      raise ValueError('ERROR: piis list has {}, over max of 100'
                       .format(len(piis)))
    url = 'http://api.elsevier.com/content/article/entitlement/pii/'
    sep = ''
    for pii in piis:
        url += sep + str(pii)
        sep = ','

    # UF's api key
    #url += '?httpAccept=text/xml&apiKey=d91051fb976425e3b5f00750cbd33d8b'

    #url += '?httpAccept=application/xml&apiKey=d91051fb976425e3b5f00750cbd33d8b'
    url += '?httpAccept=application/xml&apiKey=d91051fb976425e3b5f00750cbd33d8b'
    if verbosity > 0:
      print('{}:got {} piis, using url={}'.format(me,len(piis),url))

    try:
      xml_tree = etree.parse(url)
    except Exception as ex:
      print("For url='{}' got lxml error='{}'. Skipping this url."
            .format(me,url,repr(ex)))
      yield -1, -1 #Sentinel to caller to skip, but try again...
    else:
      node_root_input = xml_tree.getroot()
      input_xml_str =  etree.tostring(node_root_input, pretty_print=True)

      if verbosity > 0:
        print("{}:got input xml string={}".format(me,input_xml_str))

      d_namespaces = {key:value
              for key,value in dict(node_root_input.nsmap).items()
              if key is not None}
      nodes_entitlement = node_root_input.findall(
          'document-entitlement', namespaces=d_namespaces)

      print('{}: got {} piis, made entitlement request {}, and got {} nodes_entitlement'
            .format(me,len(piis),url,len(nodes_entitlement)))

      for node_entitlement in nodes_entitlement:
          yield node_entitlement, d_namespaces

    return None

'''
Params:
input_file_name: name of an input file of utf8 encoding, where each line is a set of fields.
delim: delimiter character that separates fields in each input file's line
pii_index: an index specifying the field in a line that holds a pii value
normalized: True means all pii fluff characters are removed already
            False means fluff characters could exist in the pii value
'''
def gen_entitlement_nodes_by_input_file(input_file_name=None, pii_index=2
    , delim='\t', normalized=True, max_batch_piis=20, verbosity=0):
    me = 'gen_entitlement_nodes_by_input_file'
    if verbosity > 0:
      print("{}: using input_file_name={}, delim='{}'".format(me,input_file_name,delim))
    n_line = 0
    batch_piis = []
    with open (input_file_name, "r") as input_file:
      #lines = input_file.readlines()
      #for input_line in lines:
      for input_line in input_file:
        input_line = input_line.replace('\n','')
        n_line += 1
        fields = input_line.split(delim)
        # if deleted field, field 6 has a 1, skip it. Don't care about its entitlement.
        # print("fields[6]='{}'".format(fields[6]))
        if fields[6] == '1':
          print('Skip pii on deleted n_line={}'.format(n_line))
          continue
        try:
          pii = fields[pii_index]
          pii = pii.replace('?oac=t','') # ignore open access sentinel
        except IndexError as ex:
          raise IndexError("File {}, delim='{}', line {}, number {} lacks field with index {}"
                .format(input_file_name,delim,input_line,n_line, pii_index))
        if (normalized == False):
          pii = pii.replace('(','').replace(')','').replace('-','').replace('.','')
        if verbosity > 0:
          print("n_line={}, appending pii={}".format(n_line,pii))
        batch_piis.append(pii)
        if n_line % max_batch_piis == 0:
          #print("n_line={} mod {} == 0, appending pii={}".format(n_line,max_batch_piis,pii))
          for node_entitlement, d_namespaces in gen_entitlement_nodes_by_piis(batch_piis):
              # Check sentinel value for bad syntax in api response...
              if node_entitlement == -1:
                continue
              yield node_entitlement, d_namespaces
          batch_piis = []
        # end yields for a batch of piis
      # end processing input file line with pii value
    # end  with open... input_file
    if verbosity > 0:
      print('{}: input file {} had {} lines'.format(me,input_file_name,n_line))
    #Get last batch
    for node_entitlement, d_namespaces in gen_entitlement_nodes_by_piis(batch_piis):
        # Check sentinel value for bad syntax in api response...
        if node_entitlement == -1:
          break
        yield node_entitlement, d_namespaces

    return


''' RUN()
   PREREQUISITE - input file is current and in place with name set by run()
'''

def run(output_folder_name=None,verbosity=0):

    me = "run"
    print('{}: making output folder {}'.format(me,output_folder_name))
    os.makedirs(output_folder_name, exist_ok=True)
    # Create known input file_name - of source bibinfo data stored in this git project
    input_data_folder = etl.data_folder(linux="/home/robert/"
        , windows='C:/users/podengo/'
        , data_relative_folder='git/citrus/data/sobekcm/')

    input_file_name = '{}sobekdb_prod_bibinfo.txt'.format(input_data_folder)

    #CAUTION: 20170918 - atom cannot detect tabs in input files... so I changed all tabs
    # to ! characters after verifying that no ! characters existed in this input file!
    for node_entitlement, d_namespaces in gen_entitlement_nodes_by_input_file(
        input_file_name=input_file_name, delim='\t', pii_index=4
        ):

        # Print the pii and open access value
        node_pii = node_entitlement.find("./pii-norm",namespaces=d_namespaces)
        if node_pii is None:
          print("Cannot node_pii {} has no text in an entitlment... skipping"
                .format(repr(node_pii)))
          continue
        if verbosity > 0:
          print("Got node_pii= {}".format(repr(node_pii)))
        pii = node_pii.text

        entitled = node_entitlement.find("./entitled",namespaces=d_namespaces).text

        if verbosity > 0:
            print("{}:From entitlement, pii-norm={}, entitled={}"
              .format(me,pii,entitled))

        with open ("{}pii_{}.xml".format(output_folder_name,node_pii.text), 'wb') as outfile:
            outfile.write(etree.tostring(node_entitlement, pretty_print=True))

# end run()


output_folder_name = etl.data_folder(linux='/home/robert', windows='U:',
      data_relative_folder='/data/elsevier/output_entitlement/')
run(output_folder_name=output_folder_name)
