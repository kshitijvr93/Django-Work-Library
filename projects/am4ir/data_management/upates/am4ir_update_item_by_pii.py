'''
am4ir_update_item.py

Read data from an input table that represents an am4ir spreadsheet,
and use its pii value to match to rows in the output table,
whose columns will be updated with matching input table columns
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

def am4ir_update_by_pii(engine=None, table_name_am4ir=None,
    table_name_ufdc=None):
  me = 'am4ir_update_by_pii'

  # NOTE this table must exist with expected columns
  ermd = MetaData(engine)
  table_am4ir = Table(table_name_am4ir, ermd, autoload=True, autoload_with=engine)
  table_ufdc = Table(table_name_ufdc, ermd, autoload=True, autoload_with=engine)
  conn = engine.connect()

  a = table_am4ir.alias()
  u = table_ufdc.alias()

  am4ir_by_pii = select(
    [a.c.doi.label('a_doi'),a.c.embperiod.label('a_embperiod'),
     a.c.embdate.label('a_embdate'), a.c.issn.label('a_issn')]).\
    where(a.itempii == u.pii).limit(1)

  conn.execute(u.update().values(
    {'doi':a_doi}
    ))

  return
#end am4ir_update_by_pii


# MAIN PROGRAM
engine_nick_name = 'uf_local_mysql_marshal1'
engine = get_db_engine_by_name(name=engine_nick_name)

table_name_am4ir = 'am4ir_item'
table_name_ufdc = 'item_elsevier_ufdc'
am4ir_update_by_pii(engine=engine, table_name_am4ir=table_name_am4ir,
   table_name_ufdc=table_name_ufdc)
