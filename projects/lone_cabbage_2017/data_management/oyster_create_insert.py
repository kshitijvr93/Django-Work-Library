'''
python 3.6 code to create the lone cabbage oyster project 'main'
database tables to hold project, sensors, locations, info that will not
often change, and is easily initialized via hard coding to
facilitate set up of other applications.
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
    return platform_name
platform_name = register_modules()
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
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy_tools.core.utils import drop_if_exists

#
from pathlib import Path

'''
As of sqlalchemy 1.2.2, scanning google searches, it seems this is the best if
not only apparent way I could find to check if a table exists and then to drop
that table generically for engines psql and MySQL and possible others engines.
'''
def drop_if_existsw(engine=None,table_name=None):

    required_params = ['engine','table_name']
    if not all(required_params):
        msg=("Did not get all required params '{}'".format(required_params))
        raise ValueError(msg)
        # Drop table if it exists
    if engine.dialect.has_table(engine, table_name):
        conn = engine.raw_connection()
        cursor = conn.cursor()
        command = "drop table if exists {};".format(table_name)
        try:
            cursor.execute(command)
            conn.commit()
        except Exception as ex:
            msg = ("Table_name={}, drop statement exception='{}'"
                .format(table_name,ex))
            raise ValueError(msg)

        cursor.close()

'''
<summary name='table_project_create'>
Create or forcibly drop and re-create table project.
And insert stock rows into it.

</summary>'
'''
def table_project_create(metadata=None,engine=None):
    table_name = 'project'
    me = '{}_create'.format(table_name)

    # Create SA relation 'table object', and later we will use
    # it to create a 'd__engine_table' in a databse engine
    table_object =  Table(table_name, metadata,
      Column('{}_id'.format(table_name), Integer,
          # NOTE do NOT use Sequence here for mysql?
          #Sequence('{}_id_seq'.format(table_name), metadata=metadata),
          primary_key=True, autoincrement=True,
          comment='Automatically incremented row id.'),
      UniqueConstraint('{}_id'.format(table_name),
          name='uq1_{}'.format(table_name) ),
      Column('name', String(200), primary_key=True,
          comment='Project name.'),
      Column('start_date', DateTime),
      )
    return table_object
#end def table_project_create

def table_project_populate(engine=None,table_object=None):
    l_rows = [
        {
          # 'project_id': 1,
          'name':'Lone Cabbage Oyster',
          'start_date':'2017/08/11',
          'status':'GO',
          'primary_investigator':'Dr. Bill Pine'
        },
        {
           #'project_id': 2,
          'name':'Lone Cabbage Oyster',
          'name':'Lone Cabbage Fish 1',
          'start_date':'2018/01/01',
          'status':'GO',
          'primary_investigator':'TBD'
        },
        {
           #'project_id': 3,
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
#end def table_project_populate

'''
<summary name='table_location_create'>
Create or forcibly drop and re-create table location.
And insert stock rows into it.

</summary>'
'''
def table_location_create(metadata=None):
    table_name = 'location'
    me = '{}_create'.format(table_name)

    # Create SA relation 'table object', and later we will use
    # it to create a 'd__engine_table' in a databse engine
    table_object =  Table(table_name, metadata,
      Column('{}_id'.format(table_name), Integer,
          # NOTE do NOT use Sequence here for mysql?
          #Sequence('{}_id_seq'.format(table_name), metadata=metadata),
          primary_key=True, autoincrement=True,
          comment='Automatically incremented row id.'),
      UniqueConstraint('{}_id'.format(table_name),
          name='uq1_{}'.format(table_name) ),
      Column('tile_id', Integer),
      Column('latitude', Float),
      Column('longitude', Float),
      Column('name', String(200), primary_key=True,
             comment='Location name, eg LC_WQ1, LC_WQ2. Shorter for reports.'),
      Column('alias1', String(200),
             comment='Possibly other name designation of the location.'),
      Column('alias2', String(200),
             comment='Possibly other name designation of the location.'),
      )
    return table_object
#end def table_location_create

def table_location_populate(engine=None, table_object=None):
    l_rows = [
        { 'name':'LCR Buoy One', },
        { 'name':'LCR Buoy Two', },
        { 'name':'LCR Buoy Three', },
        { 'name':'LCR Buoy Four', },
        { 'name':'LCR Buoy Five', },
        { 'name':'LCR Buoy Six', },
        { 'name':'LCR Buoy Seven', },
        { 'name':'LCR Buoy Eight', },
        { 'name':'LCR Buoy Nine', },
        { 'name':'Unknown', },

    ]

    #insert the l_rows
    for row in l_rows:
        engine.execute(table_object.insert(), row)

    return
# end def table_location_populate

def table_sensor_create(metadata=None):

    table_name = "sensor"
    # Create SA relation 'table object', and later we will use
    table_object =  Table('{}'.format(table_name), metadata,
      Column('{}_id'.format(table_name), Integer,
          #Sequence('{}_id_seq'.format(table_name), metadata=metadata),
          primary_key=True, autoincrement=True,
          comment='Automatically incremented row id.'),
      UniqueConstraint('{}_id'.format(table_name),
          name='uq1_{}'.format(table_name) ),
      Column('project_id', Integer),
      Column('location_id', Integer),
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
      # constraints
      ForeignKeyConstraint(
        ['project_id'], ['project.project_id'],
        name='fk_{}_project_id'.format(table_name)),
      ForeignKeyConstraint(
        ['location_id'], ['location.location_id'],
        name='fk_{}_location_id'.format(table_name)),
      )
    return table_object
#def table_sensor_create

def table_sensor_populate(engine=None,verbosity=1):
    sa_metadata = MetaData()
    table_object = Table('sensor',
            sa_metadata, autoload=True, autoload_with=engine)

    d_sensor_serial_manufacturer = {
    1 : ['..02-V5602  317.', 'diver'],
    3 : ['..00-V6916  317.', 'diver'],
    2 : ['8814', 'star'],
    4 : ['9058', 'star'],
    5 : ['9060', 'star'],
    6 : ['9061', 'star'],
    7 : ['9035', 'star'],
    8 : ['9062', 'star'],
    9 : ['9036', 'star'],
    }
    l_rows=[]
    for i in range (1,10):
        d_row = {}
        l_rows.append(d_row)
        d_row['project_id'] = 1
        d_row['sensor_id'] = i
        d_row['location_id'] = i
        d_row['observation_unit'] = 'minute'
        d_row['observation_count'] = 60
        d_row['serial_number'] = d_sensor_serial_manufacturer[i][0]
        d_row['manufacturer'] = d_sensor_serial_manufacturer[i][1]

    #insert the l_rows
    row_count = 0
    for row in l_rows:
        row_count += 1
        if verbosity > 0:
            print("Inserting row {}= {}".format(row_count,row))
        engine.execute(table_object.insert(), row)

    return
#end def table_sensor_populate

def table_sensor_history_create(metadata=None):

    table_name = "sensor_history"
    # Create SA relation 'table object', and later we will use
    table_object = Table('{}'.format(table_name), metadata,
      Column('{}_id'.format(table_name), Integer,
             primary_key=True, autoincrement=True,
             comment='Automatically incremented row id.'),
      UniqueConstraint('{}_id'.format(table_name),
          name='uq1_{}'.format(table_name) ),
      Column('sensor_id', Integer),
      Column('location_id', Integer),
      Column('event_type', String(150)), #Empty string means PLACEMENT
      Column('event_date', DateTime),
      # constraints
      ForeignKeyConstraint(
        ['sensor_id'], ['sensor.sensor_id'],
        name='fk_{}_sensor_id'.format(table_name)),
      ForeignKeyConstraint(
        ['location_id'], ['location.location_id'],
        name='fk_{}_location_id'.format(table_name)),
      )
    return table_object
#def table_sensor_create

def table_sensor_history_populate(engine=None,table_object=None):
    sa_metadata = MetaData()
    table_object = Table('sensor_history',
            sa_metadata, autoload=True, autoload_with=engine)

    l_rows = [
        { 'sensor_id':1, 'location_id':1, 'event_type': 'placement' },
        { 'sensor_id':2, 'location_id':2, 'event_type': 'placement'  },
        { 'sensor_id':3, 'location_id':3, 'event_type': 'placement'  },
        { 'sensor_id':4, 'location_id':4, 'event_type': 'placement'  },
        { 'sensor_id':5, 'location_id':5, 'event_type': 'placement'  },
        { 'sensor_id':6, 'location_id':6, 'event_type': 'placement'  },
        { 'sensor_id':7, 'location_id':7, 'event_type': 'placement'  },
        { 'sensor_id':8, 'location_id':8, 'event_type': 'placement'  },
        { 'sensor_id':9, 'location_id':9, 'event_type': 'placement'  },
    ]

    #insert the l_rows
    for row in l_rows:
        engine.execute(table_object.insert(), row)

    return

'''
Table sensor_observation is a narrower table version than table water observation.
Table sensor_observation is updated by fixed sensors types of diver and star.
'''

def table_sensor_observation_create(metadata=None):
    table_name = 'sensor_observation'
    me = '{}_create'.format(table_name)

    # NOTE: we break from convention and use observation_id
    table_object =  Table(table_name, metadata,
      Column('{}_id'.format(table_name), Integer,
          # NOTE do NOT use Sequence here for mysql?
          #Sequence('{}_id_seq'.format(table_name), metadata=metadata),
          primary_key=True, autoincrement=True,
          comment='Automatically incremented row id.'),
      UniqueConstraint('{}_id'.format(table_name),
          name='uq1_{}'.format(table_name) ),
      Column('sensor_id', Integer),
      Column('observation_datetime', DateTime),
      Column('location_id', Integer, default=1),
      UniqueConstraint('sensor_id','observation_datetime',
          name='uq2_{}'.format(table_name) ),
      # location_id can be derived, maybe no need to populate via imports?
      Column('conductivity_mS_cm', Float),
      Column('pressure_cm', Float),
      Column('salinity_psu', Float),
      Column('temperature_c', Float),
      Column('sound_velocity_m_sec', Float),
      ForeignKeyConstraint(
        ['sensor_id'], ['sensor.sensor_id'],
        name='fk_{}_sensor_id'.format(table_name)),
      ForeignKeyConstraint(
        ['location_id'], ['location.location_id'],
        name='fk_{}_location_id'.format(table_name)),
      )

    return table_object

def table_water_observation_create(metadata=None):
    table_name = 'water_observation'
    me = '{}_create'.format(table_name)

    # NOTE: we break from convention and use observation_id
    table_object =  Table(table_name, metadata,
      Column('{}_id'.format(table_name), Integer,
          # NOTE do NOT use Sequence here for mysql?
          #Sequence('{}_id_seq'.format(table_name), metadata=metadata),
          primary_key=True, autoincrement=True,
          comment='Automatically incremented row id.'),
      UniqueConstraint('{}_id'.format(table_name),
          name='uq1_{}'.format(table_name) ),
      Column('sensor_id', Integer),
      Column('observation_datetime', DateTime),
      UniqueConstraint('sensor_id','observation_datetime',
          name='uq2_{}'.format(table_name) ),
      # location_id can be derived, maybe no need to populate via imports?
      Column('location_id', Integer, default=1),
      Column('phosphorus_ug', Float),
      Column('nitrogen_ug', Float),
      Column('chlorophyll_ug', Float),
      Column('secchi_ft', Float),
      Column('color_pt_co', Float),
      Column('specific_conductance_us_cm_25c', Float),
      Column('specific_conductance_ms_cm_25c', Float),
      Column('salinity_g_kg', Float),
      Column('salinity_psu', Float),
      Column('temperature_c', Float),
      Column('pressure_psi', Float),
      Column('pressure_cm', Float),
      Column('conductivity_mS_cm', Float),
      Column('sound_velocity_m_sec', Float),
      Column('note', String(20),
             comment='Short note on observation'),
      ForeignKeyConstraint(
        ['sensor_id'], ['sensor.sensor_id'],
        name='fk_{}_sensor_id'.format(table_name)),
      ForeignKeyConstraint(
        ['location_id'], ['location.location_id'],
        name='fk_{}_location_id'.format(table_name)),
      )

    return table_object
#end def table_water_observation_create

'''
<summary name="tables_create">
</summary>

'''
def tables_create(engine=None, metadata=None):
    #metadata = MetaData()
    d_name_table = {}

    # Drop more dependent tables first
    drop_if_exists(engine=engine, table_name='sensor_observation')
    drop_if_exists(engine=engine, table_name='water_observation')
    drop_if_exists(engine=engine, table_name='sensor_history')
    drop_if_exists(engine=engine, table_name='sensor')
    drop_if_exists(engine=engine, table_name='location')
    drop_if_exists(engine=engine, table_name='project')

    # Create most independent tables first
    d_name_table['project'] = table_project_create(metadata=metadata)

    ptable = d_name_table['project']
    mtable = metadata.tables['project']
    if ptable != mtable:
        raise("table mismatch!")

    d_name_table['location'] = table_location_create(metadata=metadata)
    d_name_table['sensor'] = table_sensor_create(metadata=metadata)
    d_name_table['sensor_history'] = table_sensor_history_create(
        metadata=metadata)
    d_name_table['water_observation'] = table_water_observation_create(
        metadata=metadata)
    d_name_table['sensor_observation'] = table_sensor_observation_create(
        metadata=metadata)

    metadata.create_all(engine, checkfirst=False)
    return d_name_table
#end def tables_create

def tables_populate(engine=None, metadata=None,d_name_table=None):
    #print("Got metadata.tables={}".format(repr(metadata.tables)))
    print("Got d_name_table={}".format(repr(d_name_table)))

    table_project_populate(engine=engine,
        table_object=d_name_table['project'])
    table_location_populate(engine=engine,
        table_object=d_name_table['location'])
    table_sensor_populate(engine=engine)
    table_sensor_history_populate(engine=engine,
        table_object=d_name_table['sensor_history'])
    # No need to initialize water_observtion table, as an import
    # program is now working

    return

#end def tables_populate

# MAIN CODE
def run(env=None):
    me="run (oyster_tables_create)"
    print("STARTING: {}: starting".format(me))
    if env == 'uf':
        #something all messet up.. THIS works for UF! using env of uf...
        engine_nick_name = 'uf_local_mysql_marshal1'
        engine_nick_name = 'uf_local_mysql_lcroyster1'
        # sqlite FAIL: "SQLite does not support autoincrement for
        #   composite primary keys"
        # engine_nick_name = 'uf_local_sqlite_lcroyster1'
    else:
        engine_nick_name = 'hp_mysql_lcroyster1'
        engine_nick_name = 'hp_psql_lcroyster1'
        engine_nick_name = 'hp_mysql_lcroyster1'

    engine = get_db_engine_by_name(name=engine_nick_name)
    metadata = MetaData()

    d_name_table = tables_create(engine=engine,metadata=metadata)
    tables_populate(engine=engine,metadata=metadata,d_name_table=d_name_table)

    print("ENDING: {}: ending".format(me))
    return
#end def run

#
test = 1

if test == 1 :
    if platform_name == 'linux':
        env = 'home'
    else:
        env = 'uf'

    run(env=env)
