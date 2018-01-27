'''
python 3.6 code to drop the lone cabbage oyster project database tables
as of January 2018 or so...
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

import sqlalchemy.sql.sqltypes
from sqlalchemy.dialects.postgresql import ARRAY


print("Using sys.path={}".format(repr(sys.path)))


# MAIN CODE
def run(env=None):

    if env == 'uf':
        engine_nick_name = 'uf_local_mysql_marshal1'
    else:
        engine_nick_name = 'hp_mysql_lcroyster1'
        engine_nick_name = 'hp_psql_lcroyster1'

    engine = get_db_engine_by_name(name=engine_nick_name)
    metadata = MetaData(engine)
    metadata.reflect(engine)
    # NOTE, we MUST list these tables in order of most-dependent (on foreign
    # keys) to least dependent, else drops can fail.
    #
    table_names = [
        'water_observation', 'sensor_history', 'sensor', 'location', 'project']

    for table_name in table_names:

        table = metadata.tables.get(table_name,None)
        if table is None:
            print("Table name '{}' already does not exist".format(table_name))
            continue
        print("Dropping table_name='{}' table={}"
            .format(table_name,repr(table)))

        table.drop(engine)

# run
env = 'home'
run(env=env)
