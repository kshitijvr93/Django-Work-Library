'''
Python 3.6 program entitlement_updates.py, which accepts an input engine and
table_name from which to retrieve Elevier PII values.

A marshal table name elsevier_api_entitlement may be best, a table dedicated to
maintaining the entitlement info garnered/update through this sole API.
SQL can use this to update the pii values loaded in ufdc. This may contain
a superset of UFDC Piis as usually some may need to be loaded into Sobek-UFDC.
The update date from the exeuction of this specific program may be kept in this
table or any other data to not confound it with other related data.


Once the subject/related  table elsevier_api_entitlement is updated, it may
(no reason to wait) immediately be used to update the open access info in
other marshal tables and any sobekdb ufdc table with open access info.

This program retrieves entitlement information for each PII value.
Also given is an output engine and table name keyed by pii, which
this program will update with entitlement info.

Standalone OS-level execution that processes CLI parameters
may be easily added later, if needed.

NB: this code also contains the method create_eap() that creates the
elsevier api entitlement table in a target database.

'''
import sys, os, os.path, platform
import datetime
from collections import OrderedDict
def register_modules():
    platform_name = platform.system().lower()
    if platform_name == 'linux':
        modules_root = '/home/robert/'
        #raise ValueError("MISSING: Enter code here to define modules_root")
    else:
        # assume rvp office pc running windows
        modules_root="C:\\rvp\\"
    sys.path.append('{}git/citrus/modules'.format(modules_root))
    return
register_modules()
print("Using sys.path={}".format(repr(sys.path)))
from collections import OrderedDict
import datetime
import etl
from lxml import etree
import os
from pathlib import Path
import pytz
from sqlalchemy import (
  bindparam, Boolean, create_engine,
  CheckConstraint, Column, Date, DateTime,
  exists,
  Float, FLOAT, ForeignKeyConstraint,
  Integer,
  literal_column,
  MetaData, Sequence, String,
  Table, Text, tuple_, UniqueConstraint,
  )
from sqlalchemy.sql.expression import literal, literal_column
from sqlalchemy.inspection import inspect as inspect
from sqlalchemy.schema import CreateTable
from sqlalchemy.sql import select, and_, or_, not_
import sqlalchemy.sql.sqltypes
# Import slate of databases that this user can use
from sqlalchemy_tools.podengo_db_engine_by_name import get_db_engine_by_name
import sys

print("Sys.path={}".format(sys.path))
sys.stdout.flush()

import time
import urllib.parse
import urllib, urllib.parse
import json
import pprint
from io import StringIO, BytesIO
import shutil
from datetime import datetime
from lxml import etree
import xml.etree.ElementTree as ET
from pathlib import Path
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

    # UF's api key, api_key
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
input_file_name: name of an input file of utf8 encoding, where each line is a set
of fields.
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
#old_run(output_folder_name=output_folder_name)
env = 'uf'
if env == 'uf':
    input_nick_name = 'uf_local_mysql_marshal1'
    input_table = uf_elsevier_harvest
    input_engine = get_db_engine_by_name(name=input_nick_name)
    pass
else:
    pass

test_run( input_engine=input_engine, input_table = input_table,
  output_engine=output_engine, output_table=output_table)

  return
