'''
(1) For a given excel spreadsheet print the header column names.
'''

import sys, os, os.path, platform
import datetime

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

print("sys.path={}".format(repr(sys.path)))

import etl
# Import slate of databases that podengo can use
from podengo_db_engine_by_name import get_db_engine_by_name

#### Sqlalchemy
import datetime
from sqlalchemy import (
  Boolean, create_engine,
  CheckConstraint, Column, Date, DateTime, ForeignKeyConstraint,
  inspect, Integer,
  MetaData, Sequence, String, Table, Text, UniqueConstraint,
  )
from sqlalchemy.schema import CreateTable

#
from pathlib import Path
from etl import html_escape, has_digit, has_upper, make_home_relative_folder
import xlrd, xlwt
from xlwt import easyxf
from xlrd import open_workbook
#
from dataset.dataset_code import SheetDictReader

def table_create(metadata=None, table_name=None, column_names=None):

    columns = [Column(
        '{}_id'.format(table_name), Integer,
        Sequence('{}_id_seq'.format(table_name)), primary_key=True,)]

    for c in column_names:
        columns.append(Column('{}'.format(c),Text))

    table = Table(table_name, MetaData(),*columns);
    print("table_create: made table {}".format(table.name))
    return table

'''
Run the creates for the given tables in the given engine.
'''

def creates_run(metadata=None,tables=None,engine=None,verbosity=1):
    for table in tables:
        if table is None:
            raise ValueError("Got a table value of None")
        print('\n-----------------TABLE {}----------------------------\n'
              .format(table.name))

        if verbosity > 0:
            print('-----------------ENGINE {}--------------------------\n'
            .format(engine.name))

        ##print (sql.compile(dialect=engine.dialect)))
        print(CreateTable(table).compile(engine))
        print('======================================')
        # Create this table in the engine
        #table.__table__.create(engine, checkfirst=True)
        table.create(engine, checkfirst=True)
    return

def workbook_columns(workbook_path=None):
    #initialize database connections for writing/inserting
    workbook = xlrd.open_workbook(workbook_path)
    first_sheet = workbook.sheet_by_index(0)
    reader = SheetDictReader(
      first_sheet, row_count_header=1, row_count_values_start=2,
      verbosity=0)

    for column_name in reader.column_names:
        column_name = column_name.strip().lower().replace(' ', '_')
        print("{}".format(repr(column_name)))

    return reader.column_names

'''
Connect to a database and insert spreadsheet rows to table

<param name='workbook_path'>
File path to an excel workbook to open, and use the first sheet as the
data source.
</param>
<param name='cxs_format'>
A python string format to use to construct the database connection string,
along with other parameter d_format_params.
</param>
<param name='d_format_params'>
Defines the names and values to use to insert into the cxs_format paramater
string, to use to create a database connection.
</param>
<note>
Used to use next default, but keep here for reference
  cxs_format='mysql+mysqldb://{user}:{password}@127.0.0.1:3306/{dbname}',
 </note>
'''

def spreadsheet_to_table(workbook_path=None, table=None, engine=None):
    me = 'spreadsheet_to_table'

    #initialize database connections for writing/inserting

    metadata = MetaData(engine)
    inspector = inspect(engine)

    print('Connecting to engine...')
    conn = engine.connect()
    print('Connected with conn={}'
      .format(repr(conn)))

    metadata.reflect(engine)
    print('Connected with conn={} to database to insert into table {}'
      .format(repr(conn),table.name))

    sys.stdout.flush()

    #initialize reader
    workbook = xlrd.open_workbook(workbook_path)
    first_sheet = workbook.sheet_by_index(0)
    reader = SheetDictReader(
      first_sheet, row_count_header=1, row_count_values_start=2)

    #Read each spreadsheet row and insert table row
    i = 0
    for row in reader:
        i += 1
        print("reading row {}".format(i))
        engine.execute(table.insert(), row)

        if i % 100 == 0:
           print(i)
#end spreadsheet_to_table(workbook_path=None, table=None, engine=None):

def run():

    workbook_path = ('C:\\rvp\\download\\'
        'at_accessions_rvp_20171130.xlsx')
    print("Calling workbook_columns()....")
    columns = workbook_columns(workbook_path=workbook_path)

    metadata = MetaData()
    table=table_create(metadata=metadata, table_name='test_table',
        column_names=columns, )

    # select a db engine
    my_db_engine = get_db_engine_by_name('local-silodb')

    tables = [table]
    creates_run(metadata=metadata,engine=my_db_engine,tables=tables)

    spreadsheet_to_table(workbook_path=workbook_path, table=table,
       engine=my_db_engine)

    #Execute a create statement

    return

print("Starting")

run()

print("Done!")
