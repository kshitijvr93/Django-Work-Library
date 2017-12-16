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

#### Sqlalechemy
import datetime
from sqlalchemy import (
  Boolean, create_engine,
  CheckConstraint, Column, Date, DateTime, ForeignKeyConstraint,
  inspect, Integer,
  MetaData, String, Table, Text, UniqueConstraint,
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

def table_creates(table_name=None, column_names=None):
    metadata = MetaData()
    columns = []

    for c in column_names:
        columns.append(Column('{}'.format(c),Text))

    table = Table(table_name, metadata,*columns);
    tables = [table]

    # sqlalchemy engines
    d_ename_extension = {
      'mysql+pyodbc://./MyDb': {'extension': '_mssql.sql'},
      # comment out some for now to declutter
      #'sqlite:///:memory:': {'extension': '_sqlite.sql'},
      #'postgresql://': {'extension':'_postgresql.sql'},
      #'oracle+cx_oracle://': {'extension':'_oracle.sql'},
      'mssql+pyodbc://': {'extension':'_mssql.sql'},
    }
    engines = []
    for engine_name, extension in d_ename_extension.items():
        # https://stackoverflow.com/questions/870925/how-to-generate-a-file-with-ddl-in-the-engines-sql-dialect-in-sqlalchemy
        engine = create_engine(
          engine_name, strategy='mock',
           executor= lambda sql, *multiparams, **params:print(sql.compile(dialect=engine.dialect)))
        engines.append(engine)

    for table in tables:
        print('\n-----------------TABLE {}----------------------------\n'
              .format(table.name))

        for i,(engine_name,extension) in enumerate(d_ename_extension.items()):
            engine = engines[i]
            print('-----------------ENGINE {}--------------------------\n'
              .format(engine_name))
            #print (sql.compile(dialect=engine.dialect)))
            print(CreateTable(table).compile(engine))

    print('======================================')

    return

def workbook_columns(workbook_path=None):
    #initialize database connections for writing/inserting
    workbook = xlrd.open_workbook(workbook_path)
    first_sheet = workbook.sheet_by_index(0)
    reader = SheetDictReader(
      first_sheet, row_count_header=1, row_count_values_start=2)

    for column_name in reader.column_names:
        column_name = column_name.strip().lower().replace(' ', '_')
        print("{}".format(repr(column_name)))

    return reader.column_names

def run():
    workbook_path = ('C:\\rvp\\download\\'
        'at_accessions_rvp_20171130.xlsx')
    # hp machine
    workbook_path = ('/home/robert/Downloads/'
        'lone_cabbage_data_janapr_2017.xlsx')

    print("Calling workbook_columns()....")
    columns = workbook_columns(workbook_path=workbook_path)
    table_creates(table_name='oyster_janapr',
        column_names=columns, )
    return

print("Starting")

run()

print("Done!")
