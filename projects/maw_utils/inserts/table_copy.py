'''
Given a source engine and table, expect the table to exist in the engine,
collect its columns and indexes (not foreign keys), create the table to an output
table name in a given destination engine, and copy all the rows from the a_source
table and insert them into the destination table

First application - copy a table to put into sobekdb production_sobekdb
warning -- a hack was made for this specific table with a where() condition.
TODO: back it out and move back to a more general utility to eventually put
under ...modules/sqlalchemy_tools folder.

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

    sys.path.append('{}'.format(modules_root))
    sys.path.append('{}git/citrus/modules'.format(modules_root))
    return
register_modules()
import etl

print("Using sys.path={}".format(repr(sys.path)))
# Import slate of databases that user can use
# from my_secrets.sa_engine_by_name import get_sa_engine_by_name

import datetime
from collections import OrderedDict

# Import slate of databases that user can use
from my_secrets.sa_engine_by_name import get_sa_engine_by_name

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


'''
    # Consider rename: create_table_dest_by_table_source() and alter
    #params to: table_name_dest, table_source, verbosity
'''

def create_table_dest_core(engine_source=None, table_name_source=None,
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

   table_dest_core.create(engine_dest, checkfirst=True)

   return table_dest_core

# MAIN

if 1 == 1:
    env = 'uf'

    table_name_source = 'item_elsevier_ufdc'
    table_name_dest = 'elsevier_item'

    if env == 'uf':

      engine_nick_name_source = 'uf_local_mysql_marshal1'

      engine_nick_name_dest = 'uf_local_mysql_marshal1'
      engine_nick_name_dest = 'uf_local_rvp_test_sobekdb'

      engine_source = get_sa_engine_by_name(engine_nick_name_source)
      engine_dest = get_sa_engine_by_name(engine_nick_name_dest)

    #
    meta_source = MetaData(engine_source)
    table_source = Table(
      table_name_source, meta_source, autoload=True, autoload_with=engine_source)

    # Create destination engine table to receive the copied rows
    # Consider rename: create_table_dest_by_table_source() and alter
    #params to: table_name_dest, table_source, verbosity
    table_dest_core = create_table_dest_core(
      engine_source=engine_source, table_name_source=table_name_source,
      engine_dest=engine_dest, table_name_dest=table_name_dest, verbosity=1)

    # Gather the rows in a dictionary - use fetchmany until a need arises for
    # fetch of one at a time..
    conn = engine_source.connect()
    s = table_source
    source_rows = conn.execute(
        select([s]).where(s.c.ufdc_deleted == 0)
        ).fetchall()

    for row in source_rows:
        engine_dest.execute(table_dest_core.insert(),row)

    l = len(source_rows)
    print("Got {} source rows, first is: {}!".format(l,source_rows[0]))
