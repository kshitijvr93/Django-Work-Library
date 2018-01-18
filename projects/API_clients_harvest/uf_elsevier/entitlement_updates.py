'''
Initial functionality here: just provide a method to create a
database table to contain Elsevier entitlement responses so far.

Todo:  conduct the elsevier entitlment requests and fill the table to
analyze UF-open access stats, eg to show the N of 'open access' articles in UFDC.
Ie, the N that would be accessible.
This data can also be used in UFDC sobek applicaiton processing to avoid
or speed up some processing of the  entitlement api because the open access
nature will not depend on the identity or VPN of the IP of the requestor.
Open access means open to all.

Python 3.6 program entitlement_updates.py, which accepts an input engine and
table_name for which to insert retrieve Elevier PII values.

STEPS:

(1) A method is included here to create the table into which the Elsevier
entitlement info will be depositied.

(2) That table will need some rows, initally each just with
a pii value. The caller may have used any means to populate the table.
EG, if the same database (as in the marshal db) has table (mysql syntax):

insert into elsevier_entitlement_uf(pii)
    select h.pii
    from uf_elsevier_harvest h;

This may contain
a superset of UFDC Items with piis, as usually some may yet need to be loaded
into Sobek-UFDC.

(3) This program will (a) use the pii in each row of the table to find the
Elsevier entitlement info for that pii and for the IP address from which
this program is run, and (b) for each row in the table, all columns except
PII will be overwritten with the response data from the Elsevier Entitlment API.

Once the subject/related  table elsevier_api_entitlement is updated, it may
(no reason to wait) immediately be used to update the open access info in
other marshal tables and any sobekdb ufdc table with open access info.

This program retrieves entitlement information for each PII value.
Also given is an output engine and table name keyed by pii, which
this program will update with entitlement info.

NB: this code also contains a method that creates the
elsevier api uf entitlement table in a target database.

NB: The part of the code that queries the Elsevier Entitlment API
should be run ONLY from the UF vpn, as it stores a value uf_entitlement
for each PII, to indicate whether a user on the UF VPN would be entitled.
At some point, I should add code to raise an exception if this program is
accidentally NOT run from the UF vpn.

Standalone OS-level execution that processes CLI parameters
may be easily added later, if needed.

'''
import sys, os, os.path, platform

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

import datetime
from collections import OrderedDict
import etl

from lxml import etree
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
from sqlalchemy.sql import ( select, and_, or_, not_,)
import sqlalchemy.sql.sqltypes

# Import slate of databases that podengo can use
from sqlalchemy_tools.podengo_db_engine_by_name import get_db_engine_by_name

print("Sys.path={}".format(sys.path))
sys.stdout.flush()

import time
import urllib.parse
import urllib, urllib.parse
import json
import pprint
from io import StringIO, BytesIO
import shutil
from lxml import etree
import xml.etree.ElementTree as ET
from pathlib import Path
import pytz
import urllib.request


''' method create_table_elsevier_api_entitlement_uf

<summary> In given engine with given (or default) table_name, create a
table designed to contain rows of entitlement results from elsevier.
</summary>

<param name='engine'>
This is an sql_alchemy engine that in which the 'elsevier_entitlement_uf'
table will be created.
If multiple developers need such a table for independent manipulations/testing
in the same engine, then they should give different table names, of course.
</param>

'''
def create_table_elsevier_entitlement_uf(
    engine=None, table_name='elsevier_entitlement_uf'
    ):

    me = 'create_table_elsevier_entitlement_uf'
    table_name = table_name
    metadata = MetaData(engine)

    new_table = Table(table_name, metadata,
      Column('{}_id'.format(table_name), Integer, primary_key=True),

      Column('pii', String(30),
             comment="Normalized pii value (no fluff)"),

      # Note: v1.2 sqlalchemy: UniqueConstraint does not use list datatype
      UniqueConstraint('pii',
        name='uq_{}_pii_account'.format(table_name)),

      # Note: for UF purposes, a unique PII is paramount. Though other ids are
      # claimed to be unique, do not ruin loading of unique piis if they have
      # duplicates. Create normal indexes on some others to speed up queries.

      Column('entitled_uf', String(30),
             comment="Elsevier entitled value for UF vpn. Values evolving."),

      Column('eid', String(30), index=True,
             comment="EID, electronic identity code, article ID used by "
                     "Elsevier, maybe others like Crossref others"),

      Column('upconf_dt', DateTime(6), default=datetime.datetime.utcnow,
             comment="DateTime of last update or confirmation of this row"),

      Column('scopus_id', String(30), index=True,
             comment="Another article ID used by Elsevier Publishers"
                     "and maybe others"),

      Column('pubmed_id', String(25), index = True,
             comment='Article ID used by Elsevier, maybe other medical publishers.'),

      Column('doi', String(150), index=True,
             comment='Digital Object ID known to all big publishers'),


      Column('doi_url', String(250),index=True,
             comment='Digital Object ID known to all big publishers'),

      ) # end call to Table('article_item'...)
    conn_write = engine.connect()
    engine_table = new_table.create(engine, checkfirst=True)
    conn_write.close()
    return engine_table

#end create_table_elsevier_entitlment_uf

'''
<summary name='sa_sequence_select'>
For given table or select, return generate a python sequence for its table
rows.
</summary>
'''
def sa_sequence_select(engine=engine, table=table):
    me = 'sequence_table_rows'

''''
<summary name='sequence_entitlements'>
This is a generator method:

Given a sequence of pii values:

(1) For each pii in the sequence:
    Accumulate the pii to a list for a batch of size 100 by default.

(2) For each batch, generate a url that is an entitlement request specifying
    each of the piis of the batch,

(3) Receive the Elsevier API entitlement response and parse the xml result

(4) For the result for each specific pii, yield the sequence
    value, which is:  a dictionary keyed
    by column name, which is a row of entitlement info/results for the pii.
</summary>

<param name=sequence_piis>
A sequence of items, each being a pii string value to use to request
an Elsevier entitlement API result.
</param>
<return>
A sequence, where each item is:
A dictionary (key is column name, value is value) API row result.
</return>

'''

def sequence_entitlements(sequence_piis=None, batch_size=100, verbosity=1):

    me = 'sequence_entitlements'

    if verbosity > 0:
        print('{}: With batch_size={}, generating a sequence of entitlements"
            .format(me, batch_size )

    if batch_size < 1:
      raise ValueError("Parameter batch_size must be 1 or greater.")

    url = "http://http://api.elsevier.com/content/article/entitlement/pii/"
    for index_pii, pii in enumerate(sequence_pii, start=1:

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
<summary name='run_elsevier_entitlment_updates'>
Use the given env to select the db engine and update_table_name.

From SA, get the update_table of the given update table name

Step 1:
Call seq_piis = sequence_piis(update_table)

where seq_piis is a sequence of the piis in the update_table for which to retrieve
Elsevier entitlment information from its API.

Step 2:
seq_entitlements = sequence_elsevier_entitlements(seq_piis)

where seq_entitlemetns is a sequece of dictionaries, where each has a key
for a 'pii' and other columns with info about that pii such as open access, doi,
and all the columns that are in the update_table.

Step 3:
result = elsevier_entitlement_updates(seq_entitlments)

Where result has some information about the updated rows in the update table that
elsevier_entitlment_updaes() performed to reflect seq_entitlements.


</summary>
'''

def run_elsevier_entitlement_updates(env='uf'):

    #old_run(output_folder_name=output_folder_name)
    env = 'uf'
    if env == 'uf':
        engine_nick_name = 'uf_local_mysql_marshal1'
        update = get_db_engine_by_name(name=engine_nick_name)
        update_table_name = 'elsevier_entitlement_uf'
        pass
    else:
        raise ValueError("Not implemented")
        pass


    # Get the sequence of all piis to request entitlment info
    seq_piis = sequence_piis(update_table);

    # Get sequence of all entitlement results
    seq_entitlements = sequence_entitlements(seq_piis);

    result = elsevier_entitlement_updates(update_table,seq_entitlements)

    #  output_engine=output_engine, output_table=output_table)
    return


'''
<summary name='create_elsevier_entitlement_uf'>
Create the database table
</summary>
NB: I already "DID" this method in some or all databases of
nterest, so only rerun it when on a database with this table
when ready to overwrite database contents!
'''
def  create_elsevier_entitlement_uf(env=None):
    if env == 'uf':
        #engine_name = 'local-silodb'
        engine_name = 'uf_local_mysql_marshal1'
    else:
        engine_name = 'hp_psql'

    engine = get_db_engine_by_name(name=engine_name)
    create_table_elsevier_entitlement_uf(engine=engine)
    return

'''
<summary name="get_elsevier_api_entitlments">
Select the pii value from the rows of the given table,
and for each pii of a row, get its Elsevier entitlement info for
the requesting IP of the current process.

NOTE: this method should be run from a machine on the UF vpn.

Update each row in the table with the API results.
</summary>
'''

def get_elsevier_api_entitlements(engine=engine, table=table):

    piis = sequence_piis(table);
    return

def get_entitlements():
    engine_name = 'uf_local_mysql_marshal1'
    tables =
    return


#end def get_elsevier_api_entitlements

# MAIN PROGRAM  - call the main method...

run_elsevier_entitlement_updates(env='uf'):
