'''
    # NB - may want to use the newer module method spreadsheet_to_table
    # If ever need to modify this method

(1) Read excel am4ir spreadsheet from elsevier
(2) and insert the colums of interest into rows of a table,
    for example,  to default mysql table am4ir_item
by  selecting row based on pii value and based on existence either insert or
update a row, with the column values:
 (a) embargo_end_date,
 (b) set flag is_am4ir to true,
 (c) update_dt value (this column update should be automatic in the db, though)

(3) and also use elevier entitlement for each row (depending on a runtime flag)
    and from that, update values of: api based on the
    article_item.publisher_item_id (pii) value to:
  (a) doi,  eid, scopus_id, is_publisher_open_access

NOTE: make separate program later to get oaidoi open access info
(4) use the doi value to use the oaidoi API update the
oaidoi.org open access value.. oai_doi_open_access
'''
#
import sys, os, os.path, platform
import datetime

def register_modules():
    platform_name = platform.system().lower()
    if platform_name == 'linux':
        repo_root = '/home/robert/git/citrus/'
        #raise ValueError("MISSING: Enter code here to define modules_root")
    else:
        # assume rvp office pc running windows
        repo_root = "C:\\rvp\\git\\citrus\\"

    repo_modules = '{}modules/'.format(repo_root)
    print("repo_modules = {}".format(repo_modules))
    sys.path.append(repo_modules)
    return repo_root


repo_root=register_modules()
print ("Using repo_root={}".format(repo_root))

print("sys.path={}".format(repr(sys.path)))

import etl
# Import slate of databases that podengo can use
from podengo_db_engine_by_name import get_db_engine_by_name

#### Sqlalechemy
import datetime
from sqlalchemy import (
  Boolean, create_engine,
  CheckConstraint, Column, Date, DateTime, ForeignKeyConstraint,
  inspect, Integer,
  MetaData, String, Table, UniqueConstraint,
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

'''
Method am4ir_spreadsheet_to_am4ir_item():

Read the given spreadhseet file and insert its rows
to the given database, specifically to the table am4ir_item.
See create_am4ir_table.py which should have created the table already in
the given database.

<param name='workbook_path'>
File path to an excel workbook to open, and use the first sheet as the
data source.
</param>

<param name='engine'>
The SqlAlchemy, SA, engine to contain the output table.
</param>

<param name='table_name'>
The name of the output table to contain the spreadsheet rows.
NB - the table column names are NOT to be changed, as other utilities
depend upon them.
</param>

'''
def am4ir_spreadsheet_to_am4ir_item(
  workbook_path=None, engine=None, table_name='am4ir_item', verbosity=1):

    #initialize database connections for writing/inserting

    metadata = MetaData(engine)
    inspector = inspect(engine)

    if verbosity > 1:
        for table_name in inspector.get_table_names():
            print("Got table_name={}".format(table_name))
        print('Connecting')

    conn = engine.connect()
    if verbosity > 1:
        print('Connected with conn={}'
          .format(repr(conn)))

    metadata.reflect(engine)
    tables = metadata.tables
    if verbosity > 1:
        print('Connected with conn={} to database with {} tables'
          .format(repr(conn),len(tables)))

    sys.stdout.flush()
    am4ir_item = tables[table_name]

    #initialize spreadsheet reader
    workbook = xlrd.open_workbook(workbook_path)
    first_sheet = workbook.sheet_by_index(0)
    reader = SheetDictReader(
      sheet_index=0, row_count_header=1, row_count_values_start=2)

    #Read spreadsheet row and insert table row
    i=0
    for row in reader:
        i += 1
        print("i={}:ssrow={}".format(i,row))
        #engine.execute(am4ir_item.insert(),
        #  itempii='somepiivalue{}'.format(i + 10000), )
        row['itempii'] = (row['itempii'].replace('-','')
          .replace('(','')
          .replace(')','')
          )
        engine.execute(am4ir_item.insert(), {
          'account' : row['account'],
          'itempii' : row['itempii'],
          'doi' : row['doi'],
          'itemonline' : row['itemonline'],
          'itemvoronline' : row['itemvoronline'],
          'embperiod' : row['embperiod'],
          'embdate' : row['embdate'],
          'itemsubtype' : row['itemsubtype'],
          'issn' : row['issn'],
          'update_dt' :
            datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            #Eg if column type goes to microseconds (6 dec places)
            #datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f"),
         } )
        if i % 100 == 0:
           print(i)

    pass
#end  am4ir_spreadsheet_to_am4ir_item()

'''
Copy the workbook on the given path (with all columns depended-upon in this code)
to the given output databae engine and table

'''
def test_run(workbook_path=None, output_engine=None,table_name=None):
    me='test_run'

    engine = output_engine
    am4ir_spreadsheet_to_am4ir_item(
      workbook_path=workbook_path, engine=engine )

def xxrun():
    workbook_path = ('C:\\rvp\\git\\citrus\\projects\\am4ir\\data\\inventory_am4ir\\'
        '20171101_from_elsevier_letitia_am4ir_masterlist.xlsx')
    environment = 'mysql'
    #environment = 'mssql'

    if environment == 'mysql':
        engine_spec_format = (
          'mysql+mysqldb://{user}:{password}@127.0.0.1:3306/{dbname}'
          )
        d_format_params = {}
        d_format_params['user'] = 'podengo'
        d_format_params['password'] = '20MY18sql!'
        d_format_params['dbname'] = 'marshal1'
    else: #assume we are using mssql aka sql_server
        # See https://stackoverflow.com/questions/24085352/how-do-i-connect-to-sql-server-via-sqlalchemy-using-windows-authentication
        # Note: using windows authentication as we specify trusted connection
        # Note: also had to add url-type param of driver=SQL+Server
        engine_spec_format = (
          'mssql://{server_name}\\SQLEXPRESS/{database_name}'
          '?driver=SQL+Server'
          '&trusted_connection=yes')
        d_format_params = {}
        d_format_params['server_name'] = 'localhost'
        d_format_params['database_name'] = 'silodb'

    engine_spec = (engine_spec_format.format(**d_format_params))
    print("Using engine_spec={}".format(engine_spec))
    engine = create_engine(engine_spec, echo=True)

    print("Calling am4ir_spreadsheet_to_am4ir_item()....")
    am4ir_spreadsheet_to_am4ir_item(
      workbook_path=workbook_path, engine=engine )
    return#
#end

print("Starting")

table_name = 'am4ir_item'
if env == 'uf':
    engine_name = 'local-silodb'
    engine_name = 'mysql-marshal1'

    workbook_path = ('C:\\rvp\\git\\citrus\\projects\\am4ir\\data\\inventory_am4ir\\'
        '20171101_from_elsevier_letitia_am4ir_masterlist.xlsx')
else:
    workbook_path = ('{}projects\\am4ir\\data\\inventory_am4ir\\'
        '20171101_from_elsevier_letitia_am4ir_masterlist.xlsx'.format(repo_root))
    engine_name = 'hp-psql'

engine = get_engine_by_name(name=engine_name)

test_run(workbook_path=workbook_path,
    engine=output_engine,table_name=table_name)

print("Done!")
