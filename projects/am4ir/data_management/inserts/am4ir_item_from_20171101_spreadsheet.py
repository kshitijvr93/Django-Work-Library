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

def am4ir_spreadsheet_to_am4ir_item(workbook_path=None):

    #initialize database connections for writing/inserting
    user='podengo'
    pw='20MY18sql!'
    dbname = 'marshal1'

    cxs = ('mysql+mysqldb://{}:{}@127.0.0.1:3306/{}'
          .format(user,pw,dbname))

    print("Using cxs={}".format(cxs))
    engine = create_engine(cxs, echo=True)
    metadata = MetaData(engine)
    inspector = inspect(engine)
    for table_name in inspector.get_table_names():
        print("Got table_name={}".format(table_name))

    print('Connecting')
    conn = engine.connect()
    print('Connected with conn={}'
      .format(repr(conn)))
    tables = metadata.tables
    print('Connected with conn={} to database with {} tables'
      .format(repr(conn),len(tables)))
    sys.stdout.flush()
    am4ir_item = tables['am4ir_item']
    #print('Found table am4ir_item...')


    #initialize reader
    workbook = xlrd.open_workbook(workbook_path)
    first_sheet = workbook.sheet_by_index(0)
    reader = SheetDictReader(first_sheet)
    for i,row in enumerate(reader):
        engine.execute(am4ir_item.insert(),
          itempii='somepiivalue{}'.format(i + 10000), )
        print(i)

    #Read the spreadsheet row by row
    pass

def run():
    workbook_path = ('C:\\rvp\\git\\citrus\\projects\\am4ir\\data\\inventory_am4ir\\'
        '20171101_from_elsevier_letitia_am4ir_masterlist.xlsx')
    am4ir_spreadsheet_to_am4ir_item(workbook_path=workbook_path)
    return

print("Starting")
run()
print("Done!")
