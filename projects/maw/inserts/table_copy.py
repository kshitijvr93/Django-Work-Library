'''
Given a source engine and table, expect the table to exist in the engine,
collect its columns and indexes (not foreign keys), create the table to an output
table name in a given destination engine, and copy all the rows from the a_source
table and insert them into the destination table
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
import etl

print("Using sys.path={}".format(repr(sys.path)))

import datetime
from collections import OrderedDict
# Import slate of databases that podengo can use
from sqlalchemy_tools.podengo_db_engine_by_name import get_db_engine_by_name

#### Sqlalchemy
from sqlalchemy import (
  Boolean, create_engine,
  CheckConstraint, Column,
  Date, DateTime,Float, FLOAT, ForeignKeyConstraint,
  inspect, Integer,
  MetaData, Sequence, String, Table, Text, UniqueConstraint,
  )

from sqlalchemy.schema import CreateTable

from sqlalchemy.sql import select, and_, or_, not_
import sqlalchemy.sql.sqltypes
from sqlalchemy.dialects.postgresql import ARRAY

#
from pathlib import Path


def create_engine_table_dest(engine_source=None, table_name_source=None,
   engine_dest=None, table_name_dest=None, verbosity=0):

   meta_source = MetaData(engine_source)
   table_source = Table(
     table_name_source, meta_source, autoload=True, autoload_with=engine_source)

   # create the same table layout in the destination engine
   columns_dest = [ column.copy() for column in table_source.columns]

   meta_dest = MetaData(engine_dest)

   table_dest_core = Table(table_name_dest, meta_dest, *columns_dest )

   # Create persistent database dable in engine destination
   # But use checkFirst=True to require that it not already exist there.
   engine_table_dest = table_dest_core.create(engine_dest, checkfirst=True)

   return engine_table_dest

# MAIN

if 1 == 1:
    env = 'uf'

    table_name_source = 'item_elsevier_ufdc'
    table_name_dest = 'item_ufdc2'

    if env == 'uf':
      engine_nick_name_source = 'uf_local_mysql_marshal1'
      engine_nick_name_dest = 'uf_local_mysql_marshal1'

      engine_source = get_db_engine_by_name(engine_nick_name_source)
      engine_dest = get_db_engine_by_name(engine_nick_name_dest)

    #
    meta_source = MetaData(engine_source)
    table_source = Table(
      table_name_source, meta_source, autoload=True, autoload_with=engine_source)

    # Create destination engine table to receive the copied rows
    engine_table_dest = create_engine_table_dest(
      engine_source=engine_source, table_name_source=table_name_source,
      engine_dest = engine_dest, table_name_dest=table_name_dest, verbosity=1)

    # Gather the rows in a dictionary - use fetchmany until a need arises for
    # fetch of one at a time..
    conn = engine_source.connect()
    source_rows = conn.execute(select([table_source])).fetchall()
    l = len(source_rows)

    #print("Ending with source_rows={}".format(repr(source_rows)),flush=True)

    print("Got {} source rows, first is: {}!".format(l,source_rows[0]))
