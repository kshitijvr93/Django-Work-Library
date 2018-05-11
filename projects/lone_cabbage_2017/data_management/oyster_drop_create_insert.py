'''
Python 3.6 code to create the lone cabbage oyster project 'main'
database table lcroyster_buoy_observations
to hold fixed sensor observations (from Diver and Star
sensor types so far) at the reef buoys.

Code is removed from this project that drops and creates other Lcroyster
tables, to make sure ONLY buouy sensor data is ever dropped
--

s to hold project, sensors, locations, info that will not
often change, and is easily initialized via hard coding to
facilitate set up of other applications.
as of January 2018 or so...

As of April 2018, also see Django project UF Lib MAW, application Lcroyster
manages creation and also manual editing of oyster project tables, and
UF may deprecate or retire this code in favor of using that
MAW Application.

See also utility import_sensor_data.py - it will be modified in two phases:
First phase it will delete all rows of imported tables and in phase two it
will not delete any rows, but rther honor a paramater of minimum date of
water observation rows to insert when it seeks files/observations to import.
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
    s = os.sep
    sys.path.append('{}git{}citrus{}modules'.format(modules_root,s,s))
    return platform_name
platform_name = register_modules()
import my_secrets
import etl

'''
    sys.path.append('{}'.format(modules_root))
from my_secrets.sa_engine_by_name import get_sa_engine_by_name
'''

print("Using sys.path={}".format(repr(sys.path)))

import datetime
from collections import OrderedDict
# Import slate of databases that user can use
from my_secrets.settings_sqlalchemy import get_engine_spec_by_name

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
'''
def salinity_by_temp_c__conductivity_mS_cm():

    return 0.0

'''
As of sqlalchemy 1.2.2, scanning google searches, it seems this is the best if
not only apparent way I could find to check if a table exists and then to drop
that table generically for engines psql and MySQL and possible others engines.
'''
def drop_if_exists(engine=None,table_name=None):

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
          'name':'Lone Cabbage Fish 1',
          'start_date':'2018/01/01',
          'status':'GO',
          'primary_investigator':'TBD'
        },
        {
           #'project_id': 3,
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
          primary_key=True, autoincrement=False,
          comment='tbd'),
      Column('tile_id', Integer),
      Column('latitude', Float(precision=20)),
      Column('longitude', Float(precision=20)),
      Column('name', String(200),
             comment='Location name, eg LC_WQ1, LC_WQ2. Shorter for reports.'),
      UniqueConstraint('name'.format(table_name),
          name='uq_name1_{}'.format(table_name) ),
      Column('alias1', String(200),
             comment='Possibly other name designation of the location.'),
      UniqueConstraint('alias1'.format(table_name),
          name='uq_alias1_{}'.format(table_name) ),
      Column('alias2', String(200),
             comment='Possibly other name designation of the location.'),
      UniqueConstraint('alias2'.format(table_name),
          name='uq_alias2_{}'.format(table_name) ),
      Column('notes', Text(),
          comment='Notes about the location'),
      )
    return table_object
#end def table_location_create

def table_location_populate(engine=None, table_object=None):
    l_rows = [

        {
          'location_id': 1,
          'name':'LCR Buoy One',
          'alias1': 'WQ1',
          #WQ1|29.267726987600327|-83.098221989348531|
          'latitude': 29.267726987600327,
          'longitude': -83.098221989348531,
        },

        {
          'location_id': 2,
          'name':'LCR Buoy Two',
          'alias1': 'WQ2',
          #WQ2|29.257425041869283|-83.080270970240235|
          'latitude': 29.257425041869283,
          'longitude': -83.080270970240235,
        },

        {
          'location_id': 3,
          'name':'LCR Buoy Three',
          'alias1': 'WQ3',
          #WQ3|29.232152011245489|-83.082710020244122|
          'latitude': 29.232152011245489,
          'longitude': -83.082710020244122,
        },

        {
          'location_id': 4,
          'name':'LCR Buoy Four',
          'alias1': 'WQ4',
          #WQ4|29.266459979116917|-83.115749973803759|
          'latitude': 29.266459979116917,
          'longitude': -83.115749973803759,
        },

        {
          'location_id': 5,
          'name':'LCR Buoy Five',
          'alias1': 'WQ5',
          #WQ5|29.24560303799808|-83.095912020653486|
          'latitude': 29.24560303799808,
          'longitude': -83.095912020653486,
        },

        {
          'location_id': 6,
          'name':'LCR Buoy Six',
          'alias1': 'WQ6',
          #WQ6|29.231049958616495|-83.090120041742921|
          'latitude': 29.231049958616495,
          'longitude': -83.090120041742921,
        },
        {
          'location_id': 7,
          'name':'LCR Buoy Seven',
          'alias1': 'WQ7',
          #WQ7|29.230171032249928|-83.092115018516779|
          'latitude': 29.230171032249928,
          'longitude': -83.092115018516779,
        },
        {
          'location_id': 8,
          'name':'LCR Buoy Eight',
          'alias1': 'WQ8',
          #WQ8|29.246092038229108|-83.101499984040856|
          'latitude': 29.246092038229108,
          'longitude': -83.101499984040856,
        },
        {
          'location_id': 9,
          'name':'LCR Buoy Nine',
          'alias1': 'WQ9',
          #WQ9|29.265770986676216|-83.118119034916162|
          'latitude': 29.265770986676216,
          'longitude': -83.118119034916162,
        },

        {
          'location_id': 0,
          'name':'Unknown',
          'alias1': '???',
          #'latitude': None,
          #'longitude': None,
        },

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
      Column('project_id', Integer,
         comment="Main or owner project of this sensor"),
      Column('location_id', Integer,
          comment="The most recent deployed location of this sensor. "
            + "Maintaining this automatically by some method when "
            + "table sensor_deployment is updated may be convenient."
      # is updated.
          "),
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
    #1 : ['..02-V5602  317.', 'diver'],
    #3 : ['..00-V6916  317.', 'diver'],
    1 : ['V5602', 'diver'],
    3 : ['V6916', 'diver'],
    2 : ['8814', 'star'],
    4 : ['9058', 'star'],
    5 : ['9060', 'star'],
    6 : ['9061', 'star'],
    7 : ['9035', 'star'],
    8 : ['9062', 'star'],
    9 : ['9036', 'star'],
    10 : ['9059', 'star'],
    }
    l_rows=[]
    for i in range (1,11):
        d_row = {}
        l_rows.append(d_row)
        d_row['project_id'] = 1
        d_row['sensor_id'] = i
        d_row['location_id'] = i
        #20180312 adjusment before implementing sensor location history fully
        if i == 10:
            d_row['location_id'] = 2
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

def table_sensor_deploy_create(metadata=None):

    table_name = "sensor_deploy"
    # Create SA relation 'table object', and later we will use
    table_object = Table('{}'.format(table_name), metadata,
      Column('{}_id'.format(table_name), Integer,
             primary_key=True, autoincrement=True,
             comment='Automatically incremented row id.'),
      UniqueConstraint('{}_id'.format(table_name),
          name='uq1_{}'.format(table_name) ),
      Column('sensor_id', Integer, nullable=False),
      Column('deploy_datetime', DateTime, nullable=False),
      Column('location_id', Integer, nullable=False,
          comment="Location id where sensor is deployed as of the "
              "deploy_datetime, but where location 0 means not in service"),
      Column('notes', Text(),
          comment='Notes about the deployment (or undeployment to location 0)'),
      # constraints
      ForeignKeyConstraint(
        ['sensor_id'], ['sensor.sensor_id'],
        name='fk_{}_sensor_id'.format(table_name)),
      ForeignKeyConstraint(
        ['location_id'], ['location.location_id'],
        name='fk_{}_location_id'.format(table_name)),
      )
    return table_object
#def table_sensor_deploy_create

def get_d_sensor_deployments():

    l_rows = [
        { 'sensor_id':1, 'location_id':1,
            'event_date': '2017-08-16 00:00:00' },
        { 'sensor_id':2, 'location_id':2,
            'event_date': '2017-08-16 00:00:00'  },
        { 'sensor_id':2, 'location_id':0,
            'event_date': '2017-12-01 10:20:01'  },

        { 'sensor_id':3, 'location_id':3,
            'event_date': '2017-08-16 00:00:00' },

        { 'sensor_id':4, 'location_id':4,
            'event_date': '2017-10-06 00:00:00' },
        { 'sensor_id':5, 'location_id':5,
            'event_date': '2017-08-27 00:00:00' },
        { 'sensor_id':6, 'location_id':6,
            'event_date':  '2017-08-27 00:00:00' },
        { 'sensor_id':7, 'location_id':7,
            'event_date':  '2017-11-08 00:00:00' },
        { 'sensor_id':8, 'location_id':8,
            'event_date':  '2017-11-08 00:00:00' },
        { 'sensor_id':9, 'location_id':9,
            'event_date':  '2017-11-08 00:00:00' },
        { 'sensor_id':10, 'location_id':2,
            'event_date':  '2017-12-01 11:00:00' },
    ]
    # Key is sensor, value is dict keyed by unique dates,
    # each with a location id (deployment location) value.
    d_sensor_deployment = {}
    for d_row in l_rows:
        print("Using d_row='{}'".format(d_row))
        sensor_id = d_row['sensor_id']
        if d_sensor_deployment.get(sensor_id, None) is None:
            d_sensor_deployment[sensor_id] = dict()
        d_date_loc = d_sensor_deployment[sensor_id];

        dt = datetime.datetime.strptime(d_row['event_date'],"%Y-%m-%d %H:%M:%S")
        if dt in d_date_loc.keys():
            raise ValueError(
             "Sensor {} has duplicate sensor datetime {}"
             .format(sensor_id, repr(dt)))

        d_date_loc[dt] = d_row['location_id']

    #insert the l_rows
    #for row in l_rows:
    #    engine.execute(table_object.insert(), row)
    # Replace each d_date_loc with an orderedDict to
    # support faster downstream processes

    for sensor_id, d_date_loc in d_sensor_deployment.items():
        # Sort each sensor_deployment dict by date keys
        d_sensor_deployment[sensor_id] = OrderedDict(
          { key:d_date_loc[key] for key in sorted(d_date_loc.keys()) })

    print("Got final d_sensor_deployments = {}"
        .format(repr(d_sensor_deployment)))

    return d_sensor_deployment

'''
Table sensor_observation is a narrower table version than table water observation.
Table sensor_observation is updated by fixed sensors types of diver and star.

Deprecated: just will use a view

-- raw sensor readings measurements:

-- create view for sensor observation

drop view sob ;
select water_observation_id as sensor_observation_id,
    observation_datetime, in_service, location_id, sensor_id,
    conductivity_mS_cm, pressure_cm, salinity_psu, temperature_c,
    sound_velocity_m_sec
from water_observation;


'''

def table_water_observation_create(prefix='lcroyster',metadata=None):
    table_name = '{}_water_observation'.format(prefix)
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
      #
      Column('in_service', Integer),
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
<summary name="tables_drop_create">
</summary>

'''
def tables_drop_create(engine=None, metadata=None, prefix='lcroyster'):
    #metadata = MetaData()
    d_name_table = {}

    # Drop more dependent tables first
    drop_if_exists(engine=engine,
        table_name='{}_sensor_observation'.format(prefix))
    drop_if_exists(engine=engine,
        table_name='{}_water_observation'.format(prefix))
    drop_if_exists(engine=engine,
        table_name='{}_sensor_deploy'.format(prefix))
    drop_if_exists(engine=engine,
        table_name='{}_sensor'.format(prefix))
    drop_if_exists(engine=engine,
        table_name='{}_location'.format(prefix))
    drop_if_exists(engine=engine,
        table_name='{}_project'.format(prefix))

    # Create most independent tables first
    tproject = '{}_project'.format(prefix)
    d_name_table[tproject] = table_project_create(metadata=metadata)

    ptable = d_name_table[tproject]
    mtable = metadata.tables[tproject]
    if ptable != mtable:
        raise("table mismatch!")

    d_name_table['location'] = table_location_create(metadata=metadata)
    d_name_table['sensor'] = table_sensor_create(metadata=metadata)
    d_name_table['sensor_deploy'] = table_sensor_deploy_create(
        metadata=metadata)
    d_name_table['water_observation'] = table_water_observation_create(
        metadata=metadata)
    #d_name_table['sensor_observation'] = table_sensor_observation_create(
    #    metadata=metadata)

    metadata.create_all(engine, checkfirst=False)
    return d_name_table
#end def tables_drop_create

def tables_populate(engine=None, metadata=None,d_name_table=None,prefix=prefix):
    #print("Got metadata.tables={}".format(repr(metadata.tables)))
    print("Got d_name_table={}".format(repr(d_name_table)))

    table_project_populate(engine=engine,
        table_object=d_name_table['project'])
    table_location_populate(engine=engine,
        table_object=d_name_table['location'])
    table_sensor_populate(engine=engine)
    #table_sensor_deploy_populate(engine=engine,
    #    table_object=d_name_table['sensor_deploy'])
    # No need to initialize water_observtion table, as an import
    # program is now working
    d = get_d_sensor_deployments()

    return

#end def tables_populate

# MAIN CODE
def run(env=None,prefix='lcroyster'):
    me="run (oyster_tables_drop_create)"
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

    sa_engine_spec = get_engine_spec_by_name(name=engine_nick_name)
    engine = create_engine(sa_engine_spec)

    metadata = MetaData()

    # RETIRE THIS... too dangerous
    #d_name_table = tables_drop_create(engine=engine,metadata=metadata,
    #    prefix=prefix)

    # Populate only certain constant hard-coded table data
    tables_populate(engine=engine,metadata=metadata,
        d_name_table=d_name_table,prefix=prefix)

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
