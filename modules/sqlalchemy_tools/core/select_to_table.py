'''
Select from a source table in one engine/database to create and insert rows
into table in an output engine/database (possibly different
database/engine than source table's).

Basic docs for sqlalchemy column, select expression, and more:
http://docs.sqlalchemy.org/en/latest/core/tutorial.html
  See Section on selecting...
http://docs.sqlalchemy.org/en/latest/core/sqlelement.html
http://docs.sqlalchemy.org/en/latest/core/selectable.html
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

import etl
# Import slate of databases that podengo can use
from sqlalchemy_tools.podengo_db_engine_by_name import get_db_engine_by_name

#### Sqlalchemy
import datetime
from sqlalchemy import (
  Boolean, create_engine,
  CheckConstraint, Column, Date, DateTime,Float, FLOAT, ForeignKeyConstraint,
  inspect, Integer,
  MetaData, Sequence, String, Table, Text, UniqueConstraint,
  )
from sqlalchemy.schema import CreateTable

import sqlalchemy.sql.sqltypes
import sqlalchemy.sql.expression

''' example:
>>> from sqlalchemy.sql import select
>>> s = select([users])
>>> result = conn.execute(s)
SELECT users.id, users.name, users.fullname
FROM users
()
'''

from sqlalchemy.sql import select, and_, or_, not_
