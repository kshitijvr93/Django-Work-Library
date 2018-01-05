'''
am4ir_update_item.py

Read data from an input table that represents an am4ir spreadsheet,
and use its pii value to match to rows in the output table,
whose columns will be updated with matching input table columns

NB: 20180105 - I also researched various SO pages and then found
the most promising looking solution used the tuple_ feature and
self_group.
https://stackoverflow.com/questions/43518991/update-multiple-columns-from-a-subquery

The SA-compiled statement looked good, probably would
work OK in postgres and other dbs, but was a syntax error in
MySQL 5.7, so the below works OK for now.
Maybe revisit a way to do a multi-column correlated update (in one
statement) later. For now, for MySQL, we use the common-denominator
(among current popular databases) method of doing one statement
per destination column to update.

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

def am4ir_update_by_pii(engine=None, table_name_am4ir=None,
    table_name_ufdc=None, verbosity=1):
  me = 'am4ir_update_by_pii'

  # NOTE this table must exist with expected columns
  ermd = MetaData(engine)
  table_am4ir_item = Table(
    table_name_am4ir, ermd, autoload=True, autoload_with=engine)
  table_item_elsevier_ufdc = Table(
    table_name_ufdc, ermd, autoload=True, autoload_with=engine)
  conn = engine.connect()

  a = table_am4ir_item
  u = table_item_elsevier_ufdc

  d_colname_source = {
      'doi': a.c.doi,
      'doi_source':literal("am4ir"),
      'is_am4ir':literal(1),
      'embargo_off_date':a.c.embdate,
      'embargo_months':a.c.embperiod,
      'issn': a.c.issn,
      }
  src_key = a.c.itempii
  dest_key = u.c.pii

  for colname, colsource in d_colname_source.items():
      # For each pair, generate and execute a separate update statement
      # Sqlalchemy 1.2 generates good multi column update stmts for some dbs,
      # but not all in v1.2, i.e, not mysql, so we do it this way now...
      a_source = ( select([colsource])
        .where(and_(src_key == dest_key, a.c.account == 'Florida')).limit(1)
        )
      if verbosity > 0:
        print("COMPILED sub-select='{}'".format(a_source.compile(bind=engine)))
      ux = u.update().values({colname:a_source}).where(exists(a_source))
      if verbosity > 0:
        print("\nCOMPILED UPDATE ux='{}'".format(ux.compile(bind=engine)))
      # Execute update for this column
      conn.execute(ux)
  return
#end am4ir_update_by_pii

# MAIN PROGRAM
engine_nick_name = 'uf_local_mysql_marshal1'
engine = get_db_engine_by_name(name=engine_nick_name)

table_name_am4ir = 'am4ir_item'
table_name_ufdc = 'item_elsevier_ufdc'
am4ir_update_by_pii(engine=engine, table_name_am4ir=table_name_am4ir,
   table_name_ufdc=table_name_ufdc)
