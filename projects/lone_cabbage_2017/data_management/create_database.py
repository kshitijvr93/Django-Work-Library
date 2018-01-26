'''
python 3.6 code to create the lone cabbage oyster project database tables
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

import sqlalchemy.sql.sqltypes

#
from pathlib import Path
from sqlalchemy.dialects.postgresql import ARRAY

'''
<summary name='table_project_create'>
Create or forcibly drop and re-create table project.
And insert stock rows into it.

</summary>'
'''
def table_project_create(engine=None):
    table_name = 'project'
    me = '{}_create'.format(table_name)

    metadata = MetaData(engine)

    # Create SA relation 'table object', and later we will use
    # it to create a 'd__engine_table' in a databse engine
    table_object =  Table(table_name, metadata,
      Column('{}_id'.format(table_name), Integer,
          # NOTE do NOT use Sequence here for mysql?
          Sequence('{}_id_seq'.format(table_name)),
          primary_key=True,
          comment='Automatically incremented row id.'),
      Column('name', String(200), primary_key=True,
             comment='Project name.'),
      Column('start_date', DateTime),
      )

    # Drop table if skip_extant
    conn = engine.raw_connection()
    cursor = conn.cursor()
    command = "drop table if exists {};".format(table_name)
    cursor.execute(command)
    conn.commit()
    cursor.close()
    # Create db_table in the db engine
    db_engine_table = table_object.create(engine, checkfirst=True)

    l_rows = [
        {
          'project_id': 1,
          'name':'Lone Cabbage Oyster',
          'start_date':'2017/08/11',
          'status':'GO',
          'primary_investigator':'Dr. Bill Pine'
        },
        {
          'project_id': 2,
          'name':'Lone Cabbage Oyster',
          'name':'Lone Cabbage Fish 1',
          'start_date':'2018/01/01',
          'status':'GO',
          'primary_investigator':'TBD'
        },
        {
          'project_id': 3,
          'name':'Lone Cabbage Oyster',
          'name':'Lone Cabbage Fish 2',
          'start_date':'2018/01/01',
          'status':'GO',
          'primary_investigator':'TBD'
        },
    ]

    #insert the l_rows
    for row in l_rows:
        engine.execute(table_object.insert(), row)

    return
#end def table_project_create

'''table_sensor_create():

Depends on execution of table_project_create()

'''
def table_sensor_create():
    l_sensor = [
        {1:2},

    ]
    table_sensor =  Table('sensor', metadata,
      Column('sensor_id', Integer, primary_key=True,
             comment='Automatically incremented row id.'),
      Column('project_id', String(250)),
      Column('manufacturer', String(150)),
      Column('serial_number', String(150)),
      Column('model_type', String(150)),
      Column('manufacture_date', DateTime),
      Column('battery_expiration_date', DateTime),
      Column('observation_period_unit', String(50),
           comment="Minute, Hour, Day, etc"),
      Column('observation_period_unit_count', String(50),
           comment="The count of observation_period_units in one period."),
      Column('status_observation', String(150),
          comment="Sensor observed status. Short note."),
      Column('status_observation_date', DateTime),
      Column('meters_above_seafloor', DateTime),
      )
    return

def tables_create():
    metadata = MetaData()
    tables = []
    #


    table_sensor_placement =  Table('sensor_placement', metadata,
      Column('sensor_placement_id', Integer, primary_key=True,
             comment='Automatically incremented row id.'),
      Column('sensor_id', String(250)),
      Column('location_name', String(150)),
      Column('placement_start_date', DateTime),
      Column('placement_end_date', DateTime),
      Column('manufacture_date', DateTime),
      Column('battery_expiration_date', DateTime),
      )


    water_observation =  Table(
      Column('obervation_id', Integer, primary_key=True,
             comment='Automatically incremented row id.'),

      Column('sensor_id', Integer, primary_key=True,
             comment='Automatically incremented row id.'),
     )


    tables.append(table)

    table_name = 'article_item'
    table = Table(table_name, metadata,
      Column('article_item_id', Integer, primary_key=True),
      Column('digest_sha1_mets', String(150),
             comment='Hash for mets file for this item. See exoldmets.py'),
      Column('doi', String(150),
             comment='Digital Object ID known to all big publishers'),
      Column('eid', String(30),
             comment="eid yet another article id"),
      Column('is_am4ir', Boolean,
             comment='whether publisher provides accepted manuscript IR view'),
      Column('oadoi_open_access', String(16),
             comment='oadoi.org-asserted open_access status for doi'),
      Column('api_create_dt', DateTime, default=datetime.datetime.utcnow,
        comment=('DateTime this item was created at source api. Elsevier calls'
        ' it orig_load_date, Crossref api calls it deposit_date, etc'),
      ),
      Column('publisher_id', Integer,
             comment='Has foreign key to publisher.publisher_id'),
      Column('publisher_item_id', String(50),
             comment='Publisher-asserted unique id for this article'),
      Column('publisher_open_access', String(16)),
      Column('scopus_id', String(20),
             comment="scopus_id owned by Elsevier as of year 2017 "),
      Column('ufdc_bibid', String(10),
             comment="2-digit prefix followed by 8-digit integer"),
      Column('ufdc_group_id', Integer,
             comment="UFDC database sobekcm_group.group_id"),
      Column('ufdc_item_id', Integer,
             comment="Ufdc database sobekcm_item.item_id"),
      Column('ufdc_vid', Integer,
             comment="usually a 5-digit integer"),
      Column('embargo_end_dt', DateTime,
             comment="DateTime public embargo ended, per publisher"),
      Column('update_dt', DateTime, default=datetime.datetime.utcnow,
             comment="DateTime of last update to this row"),
      CheckConstraint(sqltext='ufdc_item_id = 1  or ufdc_item_id is null',
        name='ck_{}_ufdc_item'.format(table_name) ),
      ForeignKeyConstraint(
        ['publisher_id'], ['publisher.publisher_id'],
        name='fk_{}_publisher_id'.format(table_name)),
      # Note: v1.2 sqlalchemy: UniqueConstraint does not use list datatype
      UniqueConstraint('ufdc_item_id','ufdc_group_id',
        name='uq_{}_uitem_ugroup'.format(table_name)),
      UniqueConstraint('doi' ,name='uq_{}_doi'.format(table_name)),
      UniqueConstraint('eid' ,name='uq_{}_eid'.format(table_name)),
      UniqueConstraint('scopus_id',
         name='uq_{}_scopus_id'.format(table_name)),
      UniqueConstraint('digest_sha1_mets',
         name='uq_{}_mets'.format(table_name)),
      # Table-level comment
      comment=(
        'Table should have only article_items that are not deleted in UFDC'),
      ) # end call to Table('article_item'...)
    tables.append(table)

    # sqlalchemy engines
    d_ename_extension = {
      'mysql+pyodbc://./MyDb': {'extension': '_mssql.sql'},
      # comment out some for now to declutter
      #'sqlite:///:memory:': {'extension': '_sqlite.sql'},
      'postgresql://': {'extension':'_postgresql.sql'},
      #'oracle+cx_oracle://': {'extension':'_oracle.sql'},
      #'mssql+pyodbc://': {'extension':'_mssql.sql'},
    }
    engines = []
    for engine_name, extension in d_ename_extension.items():
        # https://stackoverflow.com/questions/870925/how-to-generate-a-file-with-ddl-in-the-engines-sql-dialect-in-sqlalchemy
        engine = create_engine(
          engine_name, strategy='mock',
           executor= lambda sql, *multiparams, **params:print(sql.compile(dialect=engine.dialect)))
        engines.append(engine)

    for table in tables:
        print('\n-----------------TABLE {}----------------------------\n'
              .format(table.name))

        for i,(engine_name,extension) in enumerate(d_ename_extension.items()):
            engine = engines[i]
            print('-----------------ENGINE {}--------------------------\n'
              .format(engine_name))
            #print (sql.compile(dialect=engine.dialect)))
            print(CreateTable(table).compile(engine))

    print('======================================')

    return
# end def tables_create()

engine_nick_name = 'uf_local_mysql_marshal1'
engine_nick_name = 'hp_psql'
engine_nick_name = 'hp_mysql'
engine = get_db_engine_by_name(name=engine_nick_name)

table_project_create(engine=engine)
