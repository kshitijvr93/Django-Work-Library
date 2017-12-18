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
from sqlalchemy_tools.podengo_db_engine_by_name import get_db_engine_by_name

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
from dataset.dataset_code import SheetDictReader, BookSheetFilter

def table_configure(metadata=None, table_name=None, column_names=None):
    me = 'table_configure'
    columns = [Column(
        '{}_id'.format(table_name), Integer,
        Sequence('{}_id_seq'.format(table_name)), primary_key=True,)]

    for c in column_names:
        print("Column name={}",c)
        columns.append(Column('{}'.format(c),Text))

    table = Table(table_name, MetaData(),*columns);
    print("{}: configured table {}".format(me,table.name))
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

def workbook_columns(workbook_path=None,sqlalchemy_columns=None):
    #initialize database connections for writing/inserting
    workbook = xlrd.open_workbook(workbook_path)
    first_sheet = workbook.sheet_by_index(0)
    if first_sheet is None:
      raise ValueError("Sheet is None")
    # output
    #reader = SheetDictReader(book=workbook,
    reader = BookSheetFilter(book=workbook,
      sheet=first_sheet, row_count_header=1, row_count_values_start=2,
      sqlalchemy_columns=sqlalchemy_columns,verbosity=0)

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

def spreadsheet_to_table(
  workbook_path=None, table=None, engine=None, d_ss_table=None):

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
      book=workbook,sheet=first_sheet, row_count_header=1, row_count_values_start=2)

    #Normalize spreadsheet column names

    #Read each spreadsheet row and insert table row
    i = 0
    for row in reader:
        i += 1
        print("reading row {}".format(i))

        #Check if any column in the row is a date and if so change its value
        # to a string

        #engine.execute(table.insert(), row)
        d_col_val = {d_ss_table[sscol]:value for sscol,value in row.items() }

        for c,v in d_col_val.items():
            msg = ("row={}, col={}, len={},val={}".format(i,c,len(v),v))
            # Try to avoid windows msg: UnicodeEncodeError...
            # on prints to windows console, encode in utf-8
            # It works FINE!
            print(msg.encode('utf-8'))
            #print(msg)
            sys.stdout.flush()

        engine.execute(table.insert(), d_col_val)

        if i % 100 == 0:
           print(i)

#end spreadsheet_to_table(workbook_path=None, table=None, engine=None):
'''
Test linux using postgresql example
Required:
A workbook has been deposited at workbook_path and has at least one excel-known
date column

And the posgresql database engine is up and running and the test table does
not exist (just drop that table before running this)

'''
def test_linux(nick_name=None):
    me = 'test_linux_postgres'

    workbook_path = ('/home/robert/Downloads/'
        'lone_cabbage_data_janapr_2017.xlsx')

    table_name = "test_table2"
    # Nick name is used by podengo_db_engine_by_bame() to get
    # the desired engine in which to create the table and insert rows.
    # todo: make it drop the table first, or give option to add new
    # rows if table already extant in the engine/database.

    #engine_nick_name = 'local-silodb'
    #engine_nick_name = 'mysql-marshal1'

    engine_nick_name = nick_name

    print("Calling workbook_columns()....")
    ss_columns = workbook_columns(workbook_path=workbook_path)

    #normalize spreadsheet column names to db table column names
    # Consider moving this 'replace' stuff into SheetDictReader code
    # maybe as a dictionary param or  even hard-coded there .
    # But just do it explicitly here for now
    d_ss_column__table_column = {}
    for ss_column in ss_columns:
        table_column = (
          ss_column.replace('/','_').replace('-','_')
          .replace('(','_').replace(')','')
          .replace(u'\u00B5','u') #micro sign
          .replace(u'\u03BC','u') #greek mu
          .replace(u'\u0040','') # commercial at
          .replace(u'\uFF20','') # fullwidth commercial at
          .replace(u'\uFE6B','') # small commercial at
          .replace(u'\u00B0','') # degrees symbol
          )
        #Todo: consider to have this replacement code detect a previous
        # underbar andin that case do not emit a second underbar as part of
        # the new column name
        d_ss_column__table_column[ss_column] = table_column

    print(
      "{}: using d_ss_column__table_column={}"
      .format(me,repr(d_ss_column__table_column)))

    metadata = MetaData()
    table=table_configure(metadata=metadata, table_name=table_name,
        column_names=d_ss_column__table_column.values(), )

    # select a db engine
    # get_db_engine_by_name is a custom function per user who runs this
    # test for now, with that users creds on linux or windows if windows
    # authentication is not being used on the windows database
    my_db_engine = get_db_engine_by_name(engine_nick_name)

    tables = [table]
    # todo:Change to arg of single table instead of list tables
    # create the table if not extand
    creates_run(metadata=metadata,engine=my_db_engine,tables=tables)

    #Add rows to the table from the spreadsheet
    spreadsheet_to_table(workbook_path=workbook_path, table=table,
       engine=my_db_engine,d_ss_table=d_ss_column__table_column)

    return
# end test_linux

'''
Set workbook_path to any workbook path on local drive

Required: the test workbook is at workbook_path, defined below.
'''
def test_windows(nick_name=None):
    me = 'test_windows'
    # Workbook for matthew kruse AT accessions data
    workbook_path = ('C:\\rvp\\download\\'
        'at_accessions_rvp_20171130.xlsx')

    # workbook for Suzanne Stapleton ifas citations spreadhseet
    #
    workbook_path = (
      'U:\\data\\ifas_citations\\2016\\base_info\\'
      'IFAS_citations_2016_inspected_20171218a.xls')
    table_name = "test_inspected"

    sql_alchemy_columns = {


    }
    # Nick name is used by podengo_db_engine_by_bame() to get
    # the desired engine in which to create the table and insert rows.
    # todo: make it drop the table first, or give option to add new
    # rows if table alread extant in the engine/database.

    engine_nick_name = nick_name
    #engine_nick_name = 'hp_psql'

    print("Calling workbook_columns()....")
    ss_columns = workbook_columns(workbook_path=workbook_path)

    #normalize spreadsheet column names to db table column names
    d_ss_column__table_column = {}
    for ss_column in ss_columns:
        table_column = (
          ss_column.replace('/','_').replace('-','_')
          .replace('(','_').replace(')','')
          .replace(u'\u00B5','u') #micro sign
          .replace(u'\u03BC','u') #greek mu
          .replace(u'\u0040','') # commercial at
          .replace(u'\uFF20','') # fullwidth commercial at
          .replace(u'\uFE6B','') # small commercial at
          .replace(u'\u00B0','') # degrees symbol
          )
        d_ss_column__table_column[ss_column] = table_column
    print(
      "{}: using d_ss_column__table_column={}"
      .format(me,repr(d_ss_column__table_column)))

    metadata = MetaData()
    table=table_configure(metadata=metadata, table_name=table_name,
        column_names=d_ss_column__table_column.values(), )

    # select a db engine
    my_db_engine = get_db_engine_by_name(engine_nick_name)

    tables = [table]
    # todo:Change to arg of single table instead of list tables
    # create the table if not extand
    creates_run(metadata=metadata,engine=my_db_engine,tables=tables)

    #Add rows to the table from the spreadsheet
    spreadsheet_to_table(workbook_path=workbook_path, table=table,
       engine=my_db_engine,d_ss_table=d_ss_column__table_column)

    return
# end test_windows()

def run(env=None):
    me='run()'
    #NOTE set environment
    print("Starting")

    #LINUX
    nick_name = 'hp_psql'

    #test_linux(nick_name=nick_name)

    #WINDOWS
    nick_name = 'uf_local_silodb'
    nick_name = 'uf_local_mysql_marshal1'
    nick_name = 'integration_sobekdb'

    nick_name = 'uf_local_mysql_marshal1'
    print("{}:Using nick_name={}".format(me,nick_name))
    test_windows(nick_name=nick_name)

    print("Done!")
    return
#end run()

# Test linux or windows or None
env = 'windows'
if env is not None:
    run(env=env)
