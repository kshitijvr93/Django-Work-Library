'''
e_bibvid_marshal.py'

Use sqlalchemy methods to select sobek database item info for Elsvier items
for use by marshaling applications.

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
  Boolean, create_engine,
  CheckConstraint, Column, Date, DateTime,
  Float, FLOAT, ForeignKeyConstraint,
  Integer,
  MetaData, Sequence, String,
  Table, Text, UniqueConstraint,
  )
from sqlalchemy.inspection import inspect as inspect
from sqlalchemy.schema import CreateTable
from sqlalchemy.sql import select, and_, or_, not_
import sqlalchemy.sql.sqltypes

# Import slate of databases that this user can use
from sqlalchemy_tools.podengo_db_engine_by_name import get_db_engine_by_name
import sys

import inspect

'''
'''
def sa_core_elsevier_bibinfo():
  return None


'''
<summary name='get_rows_elsevier_bibinfo'>

Return value is a list of rows, where each row is a rowdict with key of column
name and value of the column value from the sobekdb production db.

Use sql alchemy 'core' expression language to get SobekCM production info about
Elsevier bib items (one vid per bib, as a bib is a journal article)'
Use sqlalchemy ORM to execute  SobekCM 4.10+  production query to return
of a tables in a SobekCM 4.10+ database; to retrieve information

This code uses basic sqlalchemy 'core' expresion language  of 20180101
for sqlalchemy version 1.2, as discussed in:

http://docs.sqlalchemy.org/en/latest/core/tutorial.html#sqlexpression-text

'''
def get_rows_elsevier_bibinfo(engine=None, conn=None,table_name=None,verbosity=1):
    me = 'get_rows_elsevier_bibinfo'
    if verbosity > 0:
        print("{}: Starting".format(me))

    if conn is None:
      conn = engine.connect()
    if verbosity > 0:
        print("{}: Got conn {}".format(me,repr(conn)))

    m = MetaData(engine)
    if verbosity > 0:
        print("{}: Got metadata = {}".format(me,repr(m)))

    group = Table('SobekCM_Item_Group', m, autoload=True, autoload_with=engine)
    item  = Table('SobekCM_Item', m, autoload=True, autoload_with=engine)

    select_elsevier_info = ( select([
          group.c.BibID, item.c.VID, item.c.GroupID, item.c.Link ])
          .where( and_ (
          item.c.GroupID == group.c.GroupID,
          group.c.BibID.like('%LS%'),
          item.c.Deleted != 1 , ) )
          #.columns(bibid=String, vid=Integer, groupid=Integer, link=String)
        )
    if verbosity > 0:
      compiled = select_elsevier_info.compile()
      print("{}:compiled select={}".format(me,compiled))
    #
    # calculate rows from the select_columns- but only works with session.execute()
    result = conn.execute(select_elsevier_info)
    return result.fetchall()

'''
<summary>
For given engine and table_name, return all of its rows
by result.fetchall(), which is via an sqlalchemy result object.

</summary>
<param name='engine table_name'>
Parameter 'engine' is the sqlalchemy engine object whose persistent
existing database has a table named in the paramater 'table_name'
</param>
'''
def get_table_name_rows(engine=None, table_name=None,verbosity=1):
    me = 'get_table_name_rows'
    conn = engine.connect()
    metadata = MetaData(engine)
    if verbosity > 0:
        print("{}: For conn={},engine={},table_name={}, getting rows"
            .format(me,repr(conn),repr(engine),table_name))

    table  = Table(table_name, metadata, autoload=True, autoload_with=engine)
    select_info = ( select([table]) )
    result = conn.execute(select_info)

    return result.fetchall()
#
# NOTE: The selected columns and column order are relied upon by caller,
# so do not change them.

'''
<summary>
Given a connection to SobekCM database, select the elsevier info and
parse out the pii values, if any, in the link column's string value.

</summary>
'''
def translate_elsevier_bibinfo(engine_read=None,engine_write=None,verbosity=1):
    me = 'translate_elsevier_bibinfo'
    # Create a table to write to in the engine_write database
    emd = MetaData(engine_write)
    # Table item_elsevier_ufdc should hold all Elsevier items that have
    # been loaded into UFDC
    table_name_out = 'item_elsevier_ufdc'
    table_core_output = Table(table_name_out, emd,
        Column('{}_id'.format(table_name_out), Integer,
             Sequence('{}_id_seq'.format(table_name_out)), primary_key=True),
        Column('bibvid', String(30)),
        UniqueConstraint('bibvid', name='{}_uix1'.format(table_name_out)),
        Column('pii', String(30)),
        Column('is_oac', String(20)),
        Column('bibid', String(20)),
        Column('vid', Integer),
    )

    # May put checkfirst as an argument to this method later.
    try:
        table_core_output.drop(engine_write)
    except sqlalchemy.exc.OperationalError:
        pass
    engine_table_out = table_core_output.create(engine_write, checkfirst=True)

    l_d_col_val = []
    fetchall = get_rows_elsevier_bibinfo(engine=engine_read)
    for i,row in enumerate(fetchall,start=1):
        d_col_val = {}
        l_d_col_val.append(d_col_val)

        bibid= row['BibID']
        vid_str = row['VID']
        vid = int(vid_str)
        bibvid='{}_{}'.format(bibid, vid_str)

        d_col_val['bibid'] = bibid
        d_col_val['vid'] = vid
        d_col_val['bibvid'] = bibvid

        link = row['Link']
        # pii is after last slash, but before a ?, if any
        part_qs = link.split('?')
        is_oac = False
        if len(part_qs) > 1:
            part_sides = part_qs[1].split('=')
            is_oac = False
            if len(part_sides) > 1 and part_sides[1] == 't':
                is_oac = True
                if verbosity > 0:
                  print("row {} bibvid {}, open access is True"
                    .format(i,bibvid))

        d_col_val['is_oac'] = is_oac

        # link has pii value as last slash-delimited field before q mark.
        pii = part_qs[0].split('/')[-1]
        d_col_val['pii'] = pii

        if verbosity > 0 and (i - 1) % 1000 == 0:
            print("{}:row {}: d_col_val={}"
              .format(me,i,repr(d_col_val)))

    # Now insert all the original and derived values into the output
    # engine's table
    conn_write = engine_write.connect()
    #print("{}: l_d_col_val...")
    #for i,d in enumerate(l_d_col_val,start=1):
    #    print("Insert row {}={}".format(i,repr(d)))
    #    conn_write.execute(table_core_output.insert(),d)

    conn_write.execute(table_core_output.insert(), l_d_col_val)

    return

'''
now replacing below with above
'''
def old_select_elsevier_bibvid_piis(conn, ntop=3):
    l_messages=[]
    l_messages.append("Building d_bibvid dictionary of bibvids for Elsevier...")
    # Get ntop rows from db connection with a query herein.
    # Return messages, a dictionary d_bibvid of results.
    # Later we will time the task of retrieving entitlement for each PII/article.
    # NOTE: the %LS005% condition is a capitulation to the sad state that
    # lower bib values that are BAD elsevier records haunt the SobekCM v4.9
    # database since january 2016 since there is not a clean and quick way to
    # delete old records yet. Maybe in v4.10.
    #
    top = "top({})".format(ntop) if ntop else ""
    query = '''
             select g.bibid, i.vid, i.itemid, i.groupid, i.link
             from sobekcm_item i, sobekcm_item_group g
             where
               i.groupid = g.groupid and g.bibid like '%LS005%'
               and i.deleted != 1
             order by i.link
             '''.format(top)

    header, results = conn.query(query)

    l_messages.append("Query='{}':\n returned PII values in {} result rows\n"
          .format(query, len(results)))

    rows = [] # result rows

    d_bibvid = {}
    d_piis = {}
    for row in results:
        #print(row)$G
        fields = row.split('\t')
        bibvid='{}_{}'.format(fields[0],fields[1])
        item_id = fields[2]
        group_id = fields[3]
        link_index=4
        link = fields[link_index]
        # pii is after last slash, but before a ?, if any
        part_qs = link.split('?')
        is_oac = False
        if len(part_qs) > 1:
            part_sides = part_qs[1].split('=')
            if len(part_sides) > 1:
                # 20160707- if ? is in link suffix, then it may have oac=x at the end, where x is true or false
                is_oac = True if part_sides[1] == 't' else False

        # link has pii value as last slash-delimited field before q mark.
        pii = part_qs[0].split('/')[-1]

        #overwrite link result field with just the is_oac value
        fields[link_index] = repr(is_oac)

        rows.append(fields)

        rows.append(repr(is_oac))

        d_bibvid[bibvid] = fields[2:]

        obibvid = d_piis.get(pii,None)

        if obibvid is not None:
            # This is an inconsistency within UFDC itself that will need to be
            # corrected:
            l_messages.append(
                "WARNING:UFDC PII '{}' has dup bibids: first row has {}."
                " A dup row={}"
                .format(pii, obibvid, repr(row)))
        else:
            d_piis[pii] = fields[:]

    return l_messages,d_bibvid, query, d_piis
# end def ls_select_bibvid

def elsevier_mets_validate(d_bibvid, resources_folder):
    all_ok = False
    l_messages = []
    l_messages.append("Starting...")
    l_messages.append("Done. all_ok={}".format(repr(all_ok)))
    return l_messages, all_ok

#end elsevier_mets_validate

# TEST RUN ON PRODUCTION - EBIBVID ---
# DO the select
def test_connect(connection_name=None):
    me = 'test_connect'

    #print('{}: Starting with connection_name={}'.format(connection_name)))
    d_connections = {
        # Now using mysqlclient package
        # Note a different python package/driver needed OPTION=3.
        # It also needed 127.0.0.1:3306 (with port suffix)
        # Maybe needed here too?
        'mysql_marshal1' : {
            'driver' : 'mysqlclient',
            'db_system':'mysql',
            'user':'podengo', 'password':'20MY18sql!',
            'host': '127.0.0.1','database': 'marshal1'
        },
        #NOTE: from RVP Desk must FIRST TURN off cisco mobile client to reach this.
        'production_sobekdb' : {
            'db_system': 'SQL SERVER',
            'driver': 'SQL SERVER',
            'server': r'lib-sobekdb\SobekCM',
            'database': 'SobekDB',
        },
        'silodb' : {
            'db_system': 'SQL SERVER',
            'driver': 'SQL SERVER',
            'server': r'localhost\SQLExpress',
            'database': 'silodb',
        },
        'integration_sobekdb': {
            'db_system': 'SQL SERVER',
            'driver': 'SQL SERVER',
            'server': r'lib-ufdc-cache\\ufdcprod,49352',
            'database': 'SobekTest',

        },
    } # end d_connections

    if connection_name not in d_connections.keys():
        msg = ("{}: Invalid connection name {} given. Try one of:"
            .format(me, repr(connection_name)))
        for name in d_connections.keys():
            msg += name
            msg += ', '
        raise ValueError(msg)

    d_connect = d_connections[connection_name]

    try:
        print("Using connection='{}'".format(repr(d_connect)))
        connection = DBConnection(d_connect=d_connect)

    except Exception as e:
        msg=("Failed database connection={}:\nwith exception:\n{}"
            .format(repr(d_connect),repr(e)))

        raise ValueError(msg)
    return connection
# end test_connect

def get_bibvid_piis(conn=None):

    d_log = {}
    d_params = {}
    d_log['params'] = d_params

    # We also use secsz_start as part of a filename, but windows chokes on ':'
    # in a filename, so use all hyphens for delimiters
    utc_now = datetime.datetime.utcnow()
    secsz_begin = utc_now.strftime("%Y-%m-%dT%H-%M-%SZ")

    # elsevier_base
    elsevier_base = ('c:/rvp/data/elsevier')
    app = 'ebibvid/'
    app_run = '{}/{}'.format(app,secsz_begin)

    #20160624 testing.. now use app not apprun to save space
    #output_folder = '{}/output_test/{}'.format(elsevier_base, app_run)
    output_folder = '{}/output_test/{}'.format(elsevier_base, app)
    log_filename = '{}/logfile.xml'.format(output_folder)

    output_dict_pii_filename = (
        "{}/dictionary_pii_bibvid_out_smathers.txt".format(output_folder))

    d_params['d_connect'] = repr(conn.d_connect)
    d_params['output-folder'] = output_folder
    os.makedirs(output_folder, exist_ok=True)

    d_params['secsz-begin'] = secsz_begin

    ## DATABASE - MAIN WORK --  Query the UFDC Database and Create the dictionaries

    l_messages,d_bibvid,query,d_pii = select_elsevier_bibvid_piis(
      conn, ntop=0)

    d_log['step-001-select_ls_bibvids_piis'] = l_messages

    ##################
    # Save d_pii dictionary to csv file for use by eatxml, other utilities
    # RESUME...

    od_pii = OrderedDict(d_pii)

    d_log['output-dict-pii-filename'] = output_dict_pii_filename
    print("printing to output_dict_pii_filename={}"
      .format(output_dict_pii_filename))

    # WRITE THE PII BIBVID OUPUT FILE
    with open(output_dict_pii_filename, 'w') as outfile:
        for i,(key,value) in enumerate(od_pii.items()):
            if i % 1000 == 0:
                print("{}, key={}, value[]={}".format(i, repr(key), repr(value)))
            # combine bib with vid with intervening underbar for primary user, program extmets
            print("{},{}_{},{},{},{}".format(key,value[0],value[1],value[2]
                ,value[3], value[4]) ,file=outfile)

    # TODO: visit resources directories of LS bibvid named METS files and
    # validate pii value.
    # TODO: also modify to validate pii and hash values for limited set of LS
    # bibvids.
    # todo: add support to give option to visit ALL resource LS mets files and
    # report any that exist for which we do not have a d_bibvid entry.

    # Set resources folder: may need to double-up on backslashes, just test it
    # first.
    # PRODUCTION: resources_folder = '\\flvc.fs.osg.ufl.edu\flvc-ufdc\resources'

    # TEST SYSTEM RESOURCES FOLDER:
    #resources_folder = (
    # '\\\\osg-prod.cns-fs04.osg.ufl.edu\\uflibfs01\\DeptData\\IT\\WebDigitalUnit'
    # '\\testufdc_elsevier\\resources\\')
    #
    # TODO: Or move this to its own utility that reads the d_bibvid dictionary file.
    # Validate that all bibvid-prefixed mets files in resource folder have the pii
    # that we got from sobekcm database query as part of the SobekCM_Item
    # table's 'link' column value.
    # l_messages, all_ok = elsevier_mets_validate(d_bibvid, resources_folder)
    # d_log['step-002-ls-mets-validate'] = l_messages

    # Final Log Output
    utc_now = datetime.datetime.utcnow()

    secsz_end = utc_now.strftime("%Y-%m-%dT%H-%M-%SZ")
    d_params['secsz_end'] = secsz_end

    e_root = etree.Element("uf-ebibvid")
    #add_subelements_from_dict(e_root, d_log)
    add_subelements(e_root, d_log)
    # WRITE LOGIFLE
    with open(log_filename, 'wb') as outfile:
        outfile.write(etree.tostring(e_root, pretty_print=True))

    rv="See output log file name='{}'".format(log_filename)
    print(rv)

#end def get_bibvid_piis

# This method can run from my uf office test of basic table select
def run_test_select(engine=None,engine_nick_name=None, table_name=None):
    me = 'run_test_select'

    if engine is not None:
      # Get engine from local engine_nick_name known to get_db_engine_by_name()
      engine = get_db_engine_by_name(name=engine_nick_name)
      print("{}: Using engine_nick_name={}, table named {}"
        .format(me, engine_nick_name, table_name))

    rows = get_table_name_rows(engine=engine, table_name=table_name)

    for i, row in enumerate(rows, start=1):
      #print("{}: '{}'".format(i,row.items()))
      od_row = OrderedDict(row.items())
      print("{}: '{}'".format(i,od_row))
    return

def test_translate(engine_nick_name=None,engine_write_nickname=None,verbosity=1):
    me = 'test_translate'
    if verbosity > 1:
      print("{}: Using engine_nick_name={}, engine_write_nickname={}"
          .format(me, engine_nick_name, engine_write_nickname))

    engine_read = get_db_engine_by_name(name=engine_nick_name)
    engine_write = get_db_engine_by_name(name=engine_write_nickname)

    if verbosity > 1:
      print("{}: getting rows from engine_read={}, writing to db engine {}"
          .format(me, repr(engine_read, engine_write)))

    rows = translate_elsevier_bibinfo(
      engine_read=engine_read, engine_write=engine_write)

    if verbosity > 1:
      print("{}: Got {} rows from engine={}"
          .format(me, len(rows), repr(engine)))
    return

def test_elsevier_bibinfo(engine_nick_name=None,verbosity=1):
    me = 'test_elsevier_bibinfo'
    print("{}: Using engine_nick_name={}"
          .format(me, engine_nick_name))
    engine = get_db_engine_by_name(name=engine_nick_name)
    print("{}: getting rows from engine={}"
          .format(me, repr(engine)))

    rows = get_rows_elsevier_bibinfo(engine=engine)

    print("{}: Got {} rows from engine={}"
          .format(me, len(rows), repr(engine)))

    for i, row in enumerate(rows, start=1):
      #print("{}: '{}'".format(i,row.items()))
      od_row = OrderedDict(row.items())
      print("{}: '{}'".format(i,od_row))
    return

# MAIN CODE

#uf office test of basic table select
#run_test_select(engine_nick_name='uf_local_silodb', table_name='test_table2')

#test_elsevier_bibinfo(engine_nick_name='production_sobekdb')
engine_write_nickname = 'uf_local_mysql_marshal1'

test_translate(engine_nick_name='production_sobekdb',
   engine_write_nickname=engine_write_nickname)

print("Done")
