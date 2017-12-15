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

def get_db_engine_by_name(name=None,verbosity=1):
    me = 'get_db_engine_by_name'
    d_name__engine_db_specs = {
        'mysql-marshal1': {
            'user': 'podengo',
            'password': '20MY18sql!',
            'db' : 'marshal1',
            'driver': 'mysql+mysqldb://',
            'format' : '{driver}{user}:{password}@127.0.0.1:3306/{db}',
        },
        'local-silodb': {
             # Using windows authentication here so do not need user,password
            'server_name': 'localhost',
            'db' : 'silodb',
            'driver' :  'mssql://',
            'format' : ('{driver}{server_name}\\SQLEXPRESS/{db}'
                       '?driver=SQL+Server&trusted_connection=yes')
        },
        'hp-psql': {
             # hp8570w laptop - postgresql installation
            'user': 'robert',
            'password' : 'Gon82sal!',
            'db': 'mydb',
            'driver' : 'postgresql+psycopg2://',
            'format' : (
              '{driver}{user}:{password}@localhost/{db}')
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

if testme == 1:
    if env == 'windows':
        engine = test_run(name='local-silodb')
        engine = test_run(name='mysql-marshal1')
    else:
        engine = test_run(name='hp-psql')
