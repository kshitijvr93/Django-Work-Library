'''

Find all elsevier pii_xxx_.py files loaded from the root directory,
given it has a yyyy/mm/dd hierarcy, and the files are in the dd level.
This is the folder structure populated by the uf ealdxml.py program as it
queries Elsevier APIs for metadata about UF-authored articles.

For every 'pii_' file found, insert a row into the output table,
whose primary key is pii, along with the yyyy,mm,dd of the parent folders
and a date value based on that.
'''
import sys, os, os.path, platform

import datetime
from collections import OrderedDict

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
from collections import OrderedDict
import datetime
import etl
from lxml import etree
import os
from pathlib import Path
import pytz

from sqlalchemy import (
  Boolean, create_engine,
  CheckConstraint, Column, Date, DateTime,
  Float, FLOAT, ForeignKeyConstraint,
  Integer,
  MetaData, Sequence, String,
  Table, Text, UniqueConstraint,
  )

from sqlalchemy.inspection import inspect as inspect
from sqlalchemy.schema import CreateTable
from sqlalchemy.sql import select, and_, or_, not_
import sqlalchemy.sql.sqltypes

# Import slate of databases that this user can use
from sqlalchemy_tools.podengo_db_engine_by_name import get_db_engine_by_name
import sys
import inspect

def test_run(cymd_start=None, cymd_end=None,engine_write=None,
  verbosity=1):

    # Collect all the values to insert
    if cymd_start is None or cymd_end is None:
        raise ValueError("cymd_start and cymd_end must be given")

    l_d_col_val = []
    #Prepare output
    data_elsevier_folder = etl.data_folder(linux='/home/robert/', windows='U:/',
        data_relative_folder='data/elsevier/')

    input_folders = []
    input_folder_base = '{}/output_ealdxml/'.format(data_elsevier_folder)
    days = etl.sequence_days(cymd_start, cymd_end)

    # For every day in the range, collect the pii* file info

    for cymd, dt_cymd in days:
        yyyy, mm, dd = cymd[0:4], cymd[4:6], cymd[6:8]
        subfolder = ('{}/{}/{}/'.format(yyyy, mm, dd))
        if verbosity > 1:
          print("One subfolder is = '{}'".format(subfolder))
        input_folder = '{}{}'.format(input_folder_base,subfolder)
        input_file_paths = list(Path(input_folder).glob('**/pii_*.xml'))
        for count,path in enumerate(input_file_paths,start=1):
            d_col_val = {}
            #Now path.name is a pii_xxx.xml filename, where xxx is the pii
            dparts = path.name.split('.')
            d_col_val['pii'] = dparts[0][4:]
            d_col_val['yyyy'] = yyyy
            d_col_val['mm'] = mm
            d_col_val['dd'] = dd
            d_col_val['load_date'] = '{}-{}-{}'.format(yyyy,mm,dd)
            l_d_col_val.append(d_col_val)
            if verbosity > 0 and dd == '01' and count == 1 and mm == '01':
                print("Row={}".format(repr(d_col_val)))
        #end for count,path in this input_folder
    # end cymd sequence of days

    # Create the core output table
    ewmd = MetaData(engine_write)
    # Table item_elsevier_ufdc should hold all Elsevier items that have
    # been loaded into UFDC

    table_name_out = 'eald_pii'
    table_core_output = Table(table_name_out, ewmd,
        Column('{}_id'.format(table_name_out), Integer,
             Sequence('{}_id_seq'.format(table_name_out)), primary_key=True),
        Column('pii', String(30), index=True),
        UniqueConstraint('pii', name='{}_uix1'.format(table_name_out)),
        Column('yyyy', String(4)),
        Column('mm', String(2)),
        Column('dd', String(2)),
        Column('load_date', Date),
    )
    engine_table_out = table_core_output.create(engine_write, checkfirst=True)

    # inserts
    conn_write = engine_write.connect()
    conn_write.execute(table_core_output.insert(),l_d_col_val)
    return

#end test_run()

# MAIN test code

engine_write_nickname = 'uf_local_mysql_marshal1'
cymd_start = '19990101'
cymd_end = '20180102'
engine_write = get_db_engine_by_name(name=engine_write_nickname)

test_run(cymd_start=cymd_start,cymd_end=cymd_end,
  engine_write=engine_write)

#end test_run()
