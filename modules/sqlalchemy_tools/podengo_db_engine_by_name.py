'''
SENSITIVE DATA ALERT: This code has UF podengo credentials hard-coded, so
this file should not be shared.

'''
#### Sqlalechemy
import datetime
from sqlalchemy import (
  Boolean, create_engine,
  CheckConstraint, Column, Date, DateTime, ForeignKeyConstraint,
  inspect, Integer,
  MetaData, String, Table, UniqueConstraint,
  )

from sqlalchemy.schema import CreateTable
import MySQLdb

'''
Get sqlalchemy engine by name

'''
def get_db_engine_by_name(name=None,verbosity=1):
    me = 'get_db_engine_by_name'
    d_name__engine_db_specs = {
        'uf_local_mysql_marshal1': {
            # Note driver mysqldb requires "include mysqlclient"
            'dialect': 'mysql',
            'driver': 'mysqldb',
            'user': 'podengo',
            'password': '20MY18sql!',
            'host': '127.0.0.1',
            'port': '3306',
            'dbname' : 'marshal1',
            # NOTE: MUST SET utf8 on connections!
            'charset': 'utf8',
            'format' : (
              '{dialect}+{driver}://{user}:{password}@'
              '{host}:{port}/{dbname}?charset={charset}'),
        },
        'lib-archcoll_aspace': {
            # Note driver mysqldb requires "include mysqlclient"
            'dialect': 'mysql',
            # had had mysqlclient as driver?
            'driver': 'mysqldb',
            'user': 'archivesspace',
            'password': 'L1b-sp4c3!',
            'host': '10.241.33.139',
            'port': '3306',
            'dbname' : 'aspace',
            'format' : (
              '{dialect}+{driver}://{user}:{password}@'
              '{host}:{port}/{dbname}'),
        },
        'integration_sobekdb': {
            'driver': 'mssql+pyodbc',
            # odbc_driver see: https://stackoverflow.com/questions/40332319/no-driver-name-specified-writing-pandas-data-frame-into-sql-server-table
            'odbc_driver': 'SQL+Server+Native+Client+11.0',
            'server' : r'lib-ufdc-cache\\ufdcprod:49352',
            'dbname': 'SobekTest',
            # This db uses windows authentication, so no user/password
            # but it must be accessed from UF windows vpn
            #'user': 'podengo',
            #'password': '20MY18sql!',
            'format' : '{driver}://{server}/{dbname}?driver={odbc_driver}',
        },
        'production_sobekdb': {
            'driver': 'mssql+pyodbc',
            # odbc_driver see: https://stackoverflow.com/questions/40332319/no-driver-name-specified-writing-pandas-data-frame-into-sql-server-table
            'odbc_driver': 'SQL+Server+Native+Client+11.0',
            'server' : r'lib-sobekdb\SobekCM',
            'dbname': 'SobekDB',
            'format' : '{driver}://{server}/{dbname}?driver={odbc_driver}',
        },

        'uf_local_silodb': {
             # Using windows authentication here so do not need user,password
             # I did not specify driver pyodbc here, so sqlalchemy
             # uses a working default.
            'dialect' :  'mssql',
            'server_host': 'localhost',
            'server_instance': 'SQLEXPRESS',
            'dbname' : 'silodb',
            'format' : (
              '{dialect}://{server_host}\\{server_instance}/{dbname}'
              '?driver=SQL+Server&trusted_connection=yes')
        },
        'hp_psql': {
             # hp postgresql installation
            'dialect' : 'postgresql',
            'driver' : 'psycopg2',
            'user': 'robert',
            'password' : 'Gon82sal!',
            'host': 'localhost',
            'dbname': 'mydb',
            'format' : (
              '{dialect}+{driver}://{user}:{password}@{host}/{dbname}')
        },
    }

    try:
        d_param_value = d_name__engine_db_specs[name]
    except:
        msg = ("Got name='{}'.Name must be in: {}"
               .format(name,repr(d_name__engine_db_specs.keys())))
        raise ValueError(msg)

    engine_spec = (d_param_value['format'].format(**d_param_value))
    if verbosity > 0:
        print("{}:Using engine_spec={}".format(me,engine_spec))

    engine = create_engine(engine_spec, echo=True)

    return(engine)
#end get_db_engine_by_name()

def test_run(name=None):
    engine = get_db_engine_by_name(name)
    print("test_run:Got engine.name = '{}'".format(repr(engine)))

#end test_run
testme=1
env = 'linux'
env = 'windows'

if testme == 1:
    if env == 'windows':
        engine = test_run(name='uf_local_mysql_marshal1')
        engine = test_run(name='integration_sobekdb')
        engine = test_run(name='production_sobekdb')
        engine = test_run(name='uf_local_silodb')
        engine = test_run(name='lib-archcoll_aspace')
    else:
        engine = test_run(name='hp_psql')
