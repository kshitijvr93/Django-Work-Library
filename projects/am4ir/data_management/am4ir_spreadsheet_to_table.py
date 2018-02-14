'''
NB - I may want to use the newer module sqlalchemy/core method spreadsheet_to_table
     if am ever tempted to modify this method

(1) Read excel am4ir spreadsheet from elsevier.
    These are usually sent in emails by letitia mukherjee to UF Elsevier Pilot
    mailing list in 2017-2018

(2) and insert the colums of interest into rows of a table,
    for example,  to default output table named am4ir_item

by  selecting row based on pii value and based on existence either insert or
update a row, with the column values:

 (a) embargo_end_date,
 (b) set flag is_am4ir to true,
 (c) update_dt value (this column update should be automatic in the db, though)

(3) and also use elevier entitlement for each row (depending on a runtime flag)
    and from that, update values of: api based on the
    article_item.publisher_item_id (pii) value to:

  (a) doi,  eid, scopus_id, is_publisher_open_access

NOTE: can make a separate program later to get/update oaidoi open access info
per row by using the row's doi value to use with the oaidoi API to update the
row's oaidoi.org open access value.. oai_doi_open_access
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

#### SqlAlechemy stuff
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

<summary name='am4ir_spreadsheet_to_am4ir_item'>

Param workbook path identifies a spreadsheet file.
Read the spreadsheet file and copy its rows
to rows of table am4ir_item in the given database engine.

See create_am4ir_table.py which should have already created the table in
the given database.
</param>

<param name='workbook_path'>
File path to an excel workbook to open, and use the first sheet as the
data source.
</param>

<param name='engine'>
The SqlAlchemy, SA, database engine to contain the output table.
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
        for tname in inspector.get_table_names():
            print("Got table_name={}".format(tname))
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
    i = 0
    for row in reader:
        i += 1
        print("i={}:ssrow={}".format(i,row))
        # engine.execute(am4ir_item.insert(),
        #  itempii='somepiivalue{}'.format(i + 10000), )
        # Remove 'fluff' characters from itempii value
        row['itempii'] = (row['itempii'].replace('-','')
          .replace('(','')
          .replace(')','')
          )

        # Insert a row into the output table
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
    # end for row in spreadsheet reader
    return
#end  am4ir_spreadsheet_to_am4ir_item()

'''
Copy the workbook on the given path (with all columns depended-upon in this code)
to the given output database engine and table.
'''

def test_run(workbook_path=None, output_engine=None, table_name=None):
    me='test_run'

    engine = output_engine
    am4ir_spreadsheet_to_am4ir_item(
      workbook_path=workbook_path, engine=engine )

#end test_run()

print("Starting")

table_name = 'am4ir_item'
if env == 'uf':
    engine_name = 'local-silodb'
    engine_name = 'mysql-marshal1'

    workbook_path = (
        'C:\\rvp\\git\\citrus\\projects\\am4ir\\data\\inventory_am4ir\\'
        '20171101_from_elsevier_letitia_am4ir_masterlist.xlsx')
else:
    workbook_path = (
        '{}projects\\am4ir\\data\\inventory_am4ir\\'
        '20171101_from_elsevier_letitia_am4ir_masterlist.xlsx'.format(repo_root))
    engine_name = 'hp-psql'

engine = get_engine_by_name(name=engine_name)

test_run(workbook_path=workbook_path,
    engine=output_engine,table_name=table_name)

print("Done!")
