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
from sqlalchemy.sql.expression import (
   delete, insert, literal, literal_column, update, )
from sqlalchemy.inspection import inspect as inspect
from sqlalchemy.schema import CreateTable
from sqlalchemy.sql import ( select, and_, or_, not_,)
import sqlalchemy.sql.sqltypes

# Import slate of databases that podengo can use
from sqlalchemy_tools.podengo_db_engine_by_name import get_db_engine_by_name
from api.utilities import get_api_result_by_url

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

    # Now create the actual persistent table in a db engine
    conn_write = engine.connect()
    engine_table = new_table.create(engine, checkfirst=True)
    conn_write.close()
    return engine_table

#end create_table_elsevier_entitlment_uf
'''
fetchall_rows_by_table()
<summary name='fetchall_table_rows'>
Candidate method to adopt in sqlalchemy core tools.
Given an SA table object and return fetchall() of all of its rows.
If conn is given, it is used, else arg engine is used to get a connection.

See also sequence_rows_by_table() which returns a sequence of individual rows.
'''
def fetchall_rows_by_table(conn=None, engine=None, table=None, verbosity=0):
    if not table:
        raise ValueError("Arg table must be given")
    if not any(conn, engine):
        raise ValueError("Either arg conn or engine must be given")

    conn = table.engine.connect();
    return conn.execute(select([table]).fetchall())

def sequence_rows_by_table(conn=None, engine=None, table=None, verbosity=1):
    me = "sequence_rows_by_table"

    if table is None:
        raise ValueError("Arg table must be given")
    if not any([conn, engine]):
        raise ValueError("Either arg conn or engine must be given")

    if verbosity > 0:
        print("{}: generating row sequence for table '{}'"
          .format(me, table.name))

    if conn is None:
        conn = engine.connect()

    results = select([table]).execute()
    while(1):
        result = results.fetchone()
        if verbosity > 0:
            print("{}: got result='{}',pii={},entitled_uf={}"
              .format(me,result,result['pii'], result['entitled_uf']))
        if not result:
            break;
        else:
            yield result
    #end while loop
    return
#end def sequence_rows_by_table

''''
<summary name='sequence_entitlements'>
This is a generator method:

Given a sequence of row values:

(1) For each row in the sequence,
    (a) expect/extract the 'pii' value and expect it to be normalized
        i.e., no fluff characters ( '-', '(', ')' )
    (b) Accumulate the pii to a list for a batch of size 100 by default.

(2) For each pii batch, generate a url that is an entitlement request specifying
    each of the piis of the batch,

(3) Receive the Elsevier API entitlement response and parse the xml result

(4) For the result for each specific pii, yield the sequence
    value, which is:  a dictionary keyed
    by column name, which represents a row of entitlement info/results for
    the pii. The caller must expect/know the column names in the row.
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

def sequence_entitlements(sequence_rows=None, max_piis=None,batch_size=100, verbosity=1):
    me = 'sequence_entitlements'

    sys.stdout.flush()
    if verbosity > 0:
        print('{}: STARTING with batch_size={}, generating a sequence of entitlements'
            .format(me, batch_size ))

    if (batch_size < 1) or (batch_size > 100) :
      raise ValueError("Parameter batch_size must be 1-100.")

    url_base = "http://api.elsevier.com/content/article/entitlement/pii/"
    url = url_base
    sep = ''
    index_pii = 0
    for  row in sequence_rows:
        index_pii += 1
        if index_pii is not None and index_pii > max_piis:
            print("{}: piis exceeded max={}. Breaking".format(me,max_piis))
            break
        pii = row['pii']
        if verbosity > 0:
            print("{}: Got row='{}',sep='{}'".format(me,repr(row),sep))
        url += sep + pii
        sep = ","
        if index_pii % batch_size == 0:
            #Make an Elsevier API entitlement request
            # Append the UF Elsevier apiKey
            url += '?httpAccept=application/xml&apiKey=d91051fb976425e3b5f00750cbd33d8b'
            sep = ''
            if verbosity > 0:
                print("{}: sending url='{}'".format(me,url))

            # Loop to retry on timeout/network slowdowns
            tries = 0
            done = 0
            while(done == 0 and tries < 10):
                tries += 1
                try:
                    result = get_api_result_by_url(url=url, verbosity=verbosity)
                    done = 1
                except Exception as e:
                    msg=("{}:url={}, try={}, exception={}"
                        .format(me,url, tries, repr(e)))
                    print(msg)
                    pass
            # end while
            if 1 == 1:
                # Extract xml information expected per the Elsevier Entitlment API.
                # results_tree =
                try:
                    # Note: Per lxml docs, results_tree is an ElementTree object,
                    # and 'root' is an element object.
                    result_tree = etree.parse(url)
                except Exception as e:
                    print("{}: cannot parse results for url='{}. e='{}'"
                       .format(me,url_,repr(e)))
                    continue

                # Parse the result with multiple entitlements, and yield a
                # dictionary 'row' of key-value pairs for each entitlement
                for node_entitlement in result_tree.findall('{*}document-entitlement'):
                    #d_row will be the 'values' argument to update destination
                    # table.
                    # The column names are set below to match the
                    # destination tble
                    d_row = {}

                    node_pii = node_entitlement.find('{*}pii-norm')
                    d_row['pii'] = node_pii.text

                    node_entitled = node_entitlement.find('{*}entitled')
                    d_row['entitled_uf'] = node_entitled.text

                    node_eid = node_entitlement.find('{*}eid')
                    t = node_eid.text if node_eid is not None else ''
                    d_row['eid'] = node_eid.text

                    node_scopus_id = node_entitlement.find('{*}scopus_id')
                    t = node_scopus_id.text if node_scopus_id is not None else ''
                    d_row['scopus_id'] = t

                    node_pubmed_id = node_entitlement.find('{*}pubmed_id')
                    t = node_pubmed_id.text if node_pubmed_id is not None else ''

                    d_row['pubmed_id'] = t

                    node_doi = node_entitlement.find('{*}doi')
                    d_row['doi'] = node_doi.text

                    node_doi_url = node_entitlement.find('{prism}url')
                    text = node_doi_url.text if node_doi_url is not None else ''
                    d_row['doi_url'] = text

                    if verbosity > 0:
                        print("{}: yielding row={}".format(me,d_row))
                    yield d_row
                # for each entitlement, yield a row
            # yield result
            url = url_base
            sep = ''
        # end yields from this batch
    # end loop over rows with piis used for entitlement requests
    return
#end sequence_entitlements

'''
<summary name="sequence_piis">
</summary>
<param name='update_table'>
The sqlalchemy table object that will be used...
</param>
'''
def sequence_piis(update_table, verbosity=''):
    stmt = select()
    return
# end sequence_piis()

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

def run_elsevier_entitlement_updates(env='uf',max_piis=100, max_updates=None,verbosity=1):
    me = 'run_elsevier_entitlement_updates'
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

    if verbosity > 0:
        print("{}: using engine_nick_name='{}', table '{}'"
          .format(me, engine_nick_name, update_table_name))
    # Get engine with extra variables to get table to update
    # TODO: make a module with an derived object 'EngineReflected()',
    # or something to capture all this auxiliary engine info up front,
    # plus an engine.inspector, at init time.
    # It's a bit convoluted to make all these calls, though I guess separation
    # saves some time and space, not usually a win-win for UF Library apps.
    engine = get_db_engine_by_name(name=engine_nick_name)
    metadata = MetaData(engine)
    #Use reflection to get the tables
    metadata.reflect(engine)
    tables = metadata.tables
    update_table = tables[update_table_name]

    # Get the sequence of all piis to request entitlment info
    if verbosity > 0:
        print("Calling sequence_rows")

    if verbosity > 0:
        seq_rows = sequence_rows_by_table(
            engine=engine, table=update_table, verbosity=1);
        print("{}: verbosely showing some seq_rows".format(me))
        index = 0
        for seq_row in seq_rows:
            index += 1
            if index > max_piis:
                print("{}: pii index > {}. Breaking".format(me,max_piis))
                break;
            print("{}:sequence item {} seq_row={}".format(me,index,seq_row))
        # end sample loop

    print("{}: calling sequence_rows_by_table()".format(me))
    # end verbose output

    seq_rows = sequence_rows_by_table(
        engine=engine, table=update_table, verbosity=1);

    if verbosity > 0:
        print("{}: calling sequence_entitlements()".format(me))
    # Get sequence of all entitlement results
    seq_entitlements = sequence_entitlements(
      sequence_rows=seq_rows, max_piis=max_piis, batch_size=10, verbosity=verbosity);

    #For each entitlement, update the database table
    i_entitlement = 0
    for row_entitlement in seq_entitlements:
        i_entitlement += 1
        if verbosity > 0 :
            print('{}: Received entitlement row {}="{}"'
                .format(me,i_entitlement, repr(row_entitlement)))

        if max_updates is not None and i_entitlement > max_updates:
            print(
              "{}: Got i_entitlement={} > max_updates = {}. Breaking out."
              .format(me,i_entitlement, max_updates))
            break

        for colname, value in row_entitlement.items():
            if colname == 'pii':
                print("{}:got pii = {}".format(me,value))

        pii = row_entitlement['pii']
        u = update_table
        if verbosity > 0:
            print("{}: Doing update with values={}".format(me,repr(row_entitlement)))
        ux = u.update().values(row_entitlement).where(u.c.pii == pii)
        if verbosity > 0:
            print("{}: From update got ux={}".format(me,repr(ux)))

        # BREAK FOR TESTING...

    print("{}:run_elsevier_entitlement_updates: returning".format(me))
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

#end def create_elsevier_api_entitlements

# MAIN PROGRAM  - call the main method...

if 1 == 1:
   run_elsevier_entitlement_updates(env='uf', max_piis=20, max_updates=10)
   print("Done!")
