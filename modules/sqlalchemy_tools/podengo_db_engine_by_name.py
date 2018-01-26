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

import MySQLdb

'''
Get sqlalchemy engine by name

NOTE: these engine database 'nick names' are many podengo creds across networks.
EG, some work OK on the UF gator network, some on my home network, some on the www.

I may categorize them later.

This is included by code that may run to affect various databases for which
I have creds (or a similar file would exist for another user).

Due to 12-factor website issues, I'll have to move this file out of this
repo before sharing the repo with other developers.

TODO: also add some sqllite databases to test with or for programs that only
need temporary tables.
'''
def get_db_engine_by_name(name=None,verbosity=0):
    me = 'get_db_engine_by_name'
    d_name__engine_db_specs = {
        'uf_local_mysql_lcroyster1': {
            # Note driver mysqldb requires "include mysqlclient"
            'dialect': 'mysql',
            'driver': 'mysqldb',
            'user': 'podengo',
            'password': '20MY18sql!',
            'host': '127.0.0.1',
            'port': '3306',
            'dbname' : 'lcroyster1',
            # NOTE: MUST SET utf8 on connections!
            'charset': 'utf8',
            'format' : (
              '{dialect}+{driver}://{user}:{password}@'
              '{host}:{port}/{dbname}?charset={charset}'),
        },
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
        'lib_archcoll_aspace': {
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
        'lib_ill_at': {
            # UF Archivists toolkit database limping along for scavenging
            # data for manual updates to aspace in early 2018...
            'driver': 'mssql+pyodbc',
            # odbc_driver see: https://stackoverflow.com/questions/40332319/no-driver-name-specified-writing-pandas-data-frame-into-sql-server-table
            'odbc_driver': 'SQL+Server+Native+Client+11.0',
            'server' : r'lib-ill\\ariel',
            'dbname': 'archiviststoolkit',
            # This db uses windows authentication, so no user/password
            # but it must be accessed from UF windows vpn
            # by login with credentials
            #'user': 'podengo',
            #'password': '20MY18sql!',
            'format' : '{driver}://{server}/{dbname}?driver={odbc_driver}',
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
        'hp_mysql': {
            # Note driver mysqldb requires "include mysqlclient"
            'dialect': 'mysql',
            'driver': 'mysqldb',
            'user': 'robert',
            'password': 'Lep71rev!',
            'host': '127.0.0.1',
            'port': '3306',
            'dbname' : 'marshal1',
            # NOTE: MUST SET utf8 on connections!
            'charset': 'utf8',
            'format' : (
              '{dialect}+{driver}://{user}:{password}@'
              '{host}:{port}/{dbname}?charset={charset}'),
        },
    }
    if name is None:
        msg=( "{}: Valid names are: {}"
          .format(me,d_name_engine_db_specs.keys()) )
        raise(ValueError, msg)

    try:
        d_param_value = d_name__engine_db_specs[name]
    except:
        msg = ("Got name='{}'.Name must be in: {}"
               .format(name,repr(d_name__engine_db_specs.keys())))
        raise ValueError(msg)

    engine_spec = (d_param_value['format'].format(**d_param_value))
    if verbosity > 0:
        print("{}:Using engine_spec={}".format(me,engine_spec))

    # Set echo FALSE else get a lot of output here.
    echo = True if verbosity > 0 else False
    engine = create_engine(engine_spec, echo=echo)

    return(engine)
#end get_db_engine_by_name()

def test_run(name=None,verbosity=1):
    engine = get_db_engine_by_name(name)
    print("test_run:Got engine.name = '{}'".format(repr(engine)))

#end test_run
testme=0
env = 'linux'
env = 'windows'

if testme == 1:
    if env == 'windows':
        engine = test_run(name='uf_local_mysql_marshal1')
        engine = test_run(name='integration_sobekdb')
        engine = test_run(name='production_sobekdb')
        engine = test_run(name='uf_local_silodb')
        engine = test_run(name='lib_archcoll_aspace')
        engine = test_run(name='lib_ill_archiviststoolkit')
    else:
        engine = test_run(name='hp_psql')
