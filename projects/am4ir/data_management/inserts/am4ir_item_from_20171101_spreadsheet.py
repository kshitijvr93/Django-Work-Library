'''
(1) Read excel am4ir spreadsheet from elsevier
(2) and modify local mysql table article_item
by  selecting row based on pii value and based on existence either insert or
update a row, with the column values:
 (a) embargo_end_date,
 (b) set flag is_am4ir to true,
 (c) update_dt value (this column update should be automatic in the db, though)

(3) and also use elevier entitlement for each row (depending on a runtime flag)
     and from that, update values of: api based on the article_item.publisher_item_id (pii) value to:
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

'''

def dbconnect():
    pass

'''
Connect to a database and insert spreadsheet rows to table am4ir_item

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
def am4ir_spreadsheet_to_am4ir_item(
  workbook_path=None, engine=None):

    #initialize database connections for writing/inserting

    metadata = MetaData(engine)
    inspector = inspect(engine)

    for table_name in inspector.get_table_names():
        print("Got table_name={}".format(table_name))

    print('Connecting')
    conn = engine.connect()
    print('Connected with conn={}'
      .format(repr(conn)))
    metadata.reflect(engine)
    tables = metadata.tables
    print('Connected with conn={} to database with {} tables'
      .format(repr(conn),len(tables)))
    sys.stdout.flush()
    am4ir_item = tables['am4ir_item']
    #print('Found table am4ir_item...')

    #initialize reader
    workbook = xlrd.open_workbook(workbook_path)
    first_sheet = workbook.sheet_by_index(0)
    reader = SheetDictReader(
      sheet_index=0, row_count_header=1, row_count_values_start=2)

    #Read the each spreadsheet row and insert table row
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

def run2(repo_root=None):
    me='run2'
    workbook_path = ('C:\\rvp\\git\\citrus\\projects\\am4ir\\data\\inventory_am4ir\\'
        '20171101_from_elsevier_letitia_am4ir_masterlist.xlsx')
    workbook_path = ('{}projects\\am4ir\\data\\inventory_am4ir\\'
        '20171101_from_elsevier_letitia_am4ir_masterlist.xlsx'.format(repo_root))

    name = 'hp-psql'
    name = 'mysql-marshal1'
    name = 'local-silodb'
    engine = get_engine_by_name(name=name)

    am4ir_spreadsheet_to_am4ir_item(
      workbook_path=workbook_path, engine=engine )

def run():
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
    return

print("Starting")
run2(repo_root=repo_root)
print("Done!")
