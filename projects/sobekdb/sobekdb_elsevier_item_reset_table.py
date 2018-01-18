'''
sobekdb_elsevier_item_reset_table.py'

Use sqlalchemy methods to select SobekCM database item info for Elsvier items.
DROP the output table in the output/write engine and recreate it with the
SobekCM/selected information for use by marshaling applications, for example, to
manage UFDC bib ids in use, or assign new ones to new items to load
into SobekCM.


NOTE: Since this program starts by dropping the output table, we may
change it to name the output table as a parameter, for example:
table_output_name = 'x_ufdc_production_elsevier_item'
where the x indicates that this table is programmatically created/destroyed
by an external process. So do not assume one could try to add data columns
to it and populate them or add rows and expect they will persist in that table.
Will add a special network of 'user accounts' with their own permissions
on such tables later. But the x prefix maybe a a good feature to keep to speed
up ad hoc queries and informal analysis, prevent some head-scratchings.
This is off-the-cuff speculation -- add some more thought later as needed.

Having an output table name parameter, this program can run meaningfully in
various sobedb production, integration test and local test systems.

So only THIS program should/would add columns or rows to this output table.
The comments here  should also probably list below the external applications
that rely upon the output table's data format, content, and update timings.

On the output database's, side, as needed, other projects/processes can
create new tables in that database with extra info and only use this output
table in other processes to update those new/other tables as needed.


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
import inspect
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

Return a tuple of:

all fetched rows,
item table object (so can refer to its columns in the fetched rows)
group table object (so can refer to its columns in the fetched rows)

'''
def get_elsevier_bibinfo(engine=None, conn=None,table_name=None,verbosity=1):
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
    basic = Table('SobekCM_Metadata_Basic_Search_Table'
                  , m, autoload=True, autoload_with=engine)

    select_elsevier_info = ( select([
          item.c.ItemID, group.c.BibID, item.c.VID, item.c.GroupID,
          item.c.Deleted, item.c.Link, basic.c.Tickler ])
          .where( and_ (
          item.c.ItemID == basic.c.ItemID,
          item.c.GroupID == group.c.GroupID,
          group.c.BibID.like('%LS%'),
          ) )
        )
    if verbosity > 0:
      compiled = select_elsevier_info.compile()
      print("{}:compiled select={}".format(me,compiled))
    #
    # calculate rows from the select_columns- but only works with session.execute()
    result = conn.execute(select_elsevier_info)
    return result.fetchall(), item, group
#end get_elsevier_bibinfo()

'''
<summary>
Given a connection to SobekCM database, select the elsevier info and
parse out the pii values, if any, in the link column's string value.

Output the translated rows to the engine_write engine,
into table item_elsevier_ufdc.

Drop the table first (checkfirst=True)
</summary>
'''
def translate_elsevier_bibinfo(engine_read=None,engine_write=None
    ,table_name_out=None,verbosity=1):

    me = 'translate_elsevier_bibinfo'
    # Create a table to write to in the engine_write database
    ewmd = MetaData(engine_write)
    # Table item_elsevier_ufdc should hold all Elsevier items that have
    # been loaded into UFDC
    table_core_output = Table(table_name_out, ewmd,
        Column('{}_id'.format(table_name_out), Integer,
             Sequence('{}_id_seq'.format(table_name_out)), primary_key=True),
        Column('ufdc_item_id', Integer),
        Column('ufdc_group_id', Integer),
        Column('ufdc_deleted', Integer),
        Column('bibvid', String(30)),
        UniqueConstraint('bibvid', name='{}_uix1'.format(table_name_out)),
        Column('pii', String(300), index=True),
        Column('oac_elsevier', String(20)),
        Column('oac_oadoi',String(20)),
        Column('tickler',Text),
        Column('bibid', String(20)),
        Column('vid', Integer),
        Column('is_am4ir', String(20)),
        Column('embargo_off_date', String(30)),
        Column('doi', String(4096)), #max key for index is 3072 bytes, exceeded
        Column('doi_source', String(16)), #Eg, elsevier_api or am4ir_ss
        Column('issn', String(32)),
        Column('embargo_months', Integer),
    )

    # Dangerous to drop this table here.
    drop_table = 1
    # Instead, require 'by hand' hard code setting of drop_table above.
    if (drop_table == 1):
        try:
            table_core_output.drop(engine_write)
        except sqlalchemy.exc.OperationalError:
            # For this app/program attempt to drop is OK if table did not exist.
            pass

    engine_table_out = table_core_output.create(engine_write, checkfirst=True)

    l_d_col_val = []
    fetchall, item, group = get_elsevier_bibinfo(engine=engine_read)
    for i,row in enumerate(fetchall,start=1):
        d_col_val = {}
        l_d_col_val.append(d_col_val)

        ufdc_item_id = row[item.c.ItemID]
        d_col_val['ufdc_item_id'] = ufdc_item_id

        ufdc_group_id = row[item.c.GroupID]
        d_col_val['ufdc_group_id'] = ufdc_group_id

        ufdc_deleted = row['Deleted']
        d_col_val['ufdc_deleted'] = ufdc_deleted

        bibid= row['BibID']
        d_col_val['bibid'] = bibid

        vid_str = row['VID']
        vid = int(vid_str)
        d_col_val['vid'] = vid

        bibvid='{}_{}'.format(bibid, vid_str)
        d_col_val['bibvid'] = bibvid

        tickler = row['Tickler']
        d_col_val['tickler'] = tickler

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

        d_col_val['oac_elsevier'] = is_oac

        # We only get the pii fron non-deleted rows.
        # Besides, the delete ones do not have the expected type of
        # formatted data from which to derive the pii value.
        if int(ufdc_deleted) != 1:
            # link has pii value as last slash-delimited field before q mark.
            pii = part_qs[0].split('/')[-1]
        else:
            pii = ''

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
# end def translate_elsevier_bibinfo()

def test_translate(
  engine_nick_name=None, engine_write_nickname=None,
  table_name_out=None, verbosity=1):
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
      engine_read=engine_read, engine_write=engine_write,
      table_name_out = table_name_out)

    if verbosity > 1:
      print("{}: Got {} rows from engine={}"
          .format(me, len(rows), repr(engine)))
    return
#end test_translate()

# MAIN CODE
engine_write_nickname = 'uf_local_mysql_marshal1'
table_name_out = 'x_ufdc_production_elsevier_item'

test_translate(engine_nick_name='production_sobekdb',
   engine_write_nickname=engine_write_nickname,
   table_name_out=table_name_out)

print("Done")
