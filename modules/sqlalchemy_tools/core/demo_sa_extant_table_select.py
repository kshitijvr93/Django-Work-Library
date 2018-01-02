'''
demo_sa_extant_table.py'

Use sqlalchemy methods to select rows from an extant table.

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

def get_rows_test(conn=None, table=None):
    select_info = ( select([table])
        )
    #
    # calculate rows from the select_columns- but only works with session.execute()
    result = conn.execute(select_info)
    return result.fetchall()

def run_test2(engine_nick_name=None, table_name=None):
    engine = get_db_engine_by_name(name=engine_nick_name)
    print('Connecting to nick_name {}'.format(engine_nick_name))

    conn = engine.connect()
    print('Got conn {}, now getting MetaData'.format(repr(conn)))
    ############
    metadata = MetaData(engine)
    print('Got metadata = {}'.format(repr(metadata)))
    print("Getting table named {}".format(table_name))
    table  = Table(table_name, metadata, autoload=True, autoload_with=engine)
    print("Got table named {}".format(table_name))

    # Note if print repr(table) it is 50 or so lines of output...

    rows = get_rows_test(conn=conn, table=table)

    print("run_test2: got rows:")
    for i, row in enumerate(rows, start=1):
      #print("{}: '{}'".format(i,row.items()))
      od_row = OrderedDict(row.items())
      print("{}: '{}'".format(i,od_row))
    return

# MAIN CODE

#home test
#run_test2(engine_nick_name='hp_psql', table_name='at_name')
#uf office test
run_test2(engine_nick_name='uf_local_silodb', table_name='test_table2')

print("Done")
