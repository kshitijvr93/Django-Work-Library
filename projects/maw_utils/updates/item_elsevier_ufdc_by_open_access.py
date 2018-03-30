'''
item_elsevier_ufdc_by_open_access.py

Using marshal1 db source table e2017_doc (make table name or other params
into a cli arg later), update the item_elsevier_ufdc table column oac_elsevier.

Do a correlated update using SA, similar to how am4ir updates its columns in
item_elsevier_ufdc.

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

def open_access_update_by_pii(engine=None, table_name_source=None,
    table_name_dest=None, verbosity=1):
  me = 'am4ir_update_by_pii'

  # NOTE this table must exist with expected columns
  ermd = MetaData(engine)
  table_item_source = Table(
    table_name_source, ermd, autoload=True, autoload_with=engine)

  table_item_dest = Table(
    table_name_dest, ermd, autoload=True, autoload_with=engine)

  conn = engine.connect()

  s = table_item_source
  d = table_item_dest

  # dest table column will be updated wtih value in source column
  d_destname_source = {
      'oac_elsevier': s.c.open_access,
      }
  # State the source and dest key column names to 'correlate'
  src_key = s.c.pii
  dest_key = d.c.pii

  for destname, colsource in d_destname_source.items():
      # For each pair, generate and execute a separate update statement
      # Sqlalchemy 1.2 generates good multi column update stmts for some dbs,
      # but not all in v1.2, i.e, not mysql, so we do it this way now...
      s_source = select([colsource]).where(src_key == dest_key).limit(1)
      if verbosity > 0:
        print("COMPILED sub-select='{}'".format(s_source.compile(bind=engine)))
      ux = d.update().values({destname:s_source}).where(exists(s_source))
      if verbosity > 0:
        print("\nCOMPILED UPDATE ux='{}'".format(ux.compile(bind=engine)))
      # Execute update for this column
      conn.execute(ux)
  return
#end open_access_update_by_pii

# MAIN PROGRAM
engine_nick_name = 'uf_local_mysql_marshal1'
engine_write = get_db_engine_by_name(name=engine_nick_name)
table_name_source = 'e2017_doc'
table_name_dest = 'item_elsevier_ufdc_test'
#table_name_dest = 'item_elsevier_ufdc'

print("WARNING: First alter the source correlated pii to have char(30),\n"
      "and put an index on it, and refresh the db, else this will timeout.")

'''
NB: do this one time after xml2rdb creates e2017_doc:

alter table e2017_doc modify pii char(30);
ALTER TABLE `marshal1`.`e2017_doc`
ADD UNIQUE INDEX `ux_e2017_doc_pii` (`pii` ASC);

'''

open_access_update_by_pii(engine=engine_write, table_name_source=table_name_source,
   table_name_dest=table_name_dest, verbosity=1)

#Done
print("Done!")

#
