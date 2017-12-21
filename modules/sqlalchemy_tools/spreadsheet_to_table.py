'''
(1) For a given excel spreadsheet print the header column names.
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

print("Using sys.path={}".format(repr(sys.path)))

import etl
# Import slate of databases that podengo can use
from sqlalchemy_tools.podengo_db_engine_by_name import get_db_engine_by_name

#### Sqlalchemy
import datetime
from sqlalchemy import (
  Boolean, create_engine,
  CheckConstraint, Column, Date, DateTime,Float, FLOAT, ForeignKeyConstraint,
  inspect, Integer,
  MetaData, Sequence, String, Table, Text, UniqueConstraint,
  )
from sqlalchemy.schema import CreateTable

import sqlalchemy.sql.sqltypes

#
from pathlib import Path
from etl import html_escape, has_digit, has_upper, make_home_relative_folder
import xlrd, xlwt
from xlwt import easyxf
from xlrd import open_workbook
#
from dataset.dataset_code import SheetDictReader, BookSheetFilter

'''
<summary name='sqlalchemy_core_table'>
Given a table name and metadata, create a table configuration with:

If given argument 'columns':
The list must be of sqlalchemy returned "Column()" objects.
Ignore the argument given for 'column_names', if any.
Generate:
(1) a primary key column  generated by this method, named by
    "{}_id".format(table_name) and with an automatic sequence
(2) the list of remaining table columns is the given list of columns

Else, consult given argument column_names and create a Text column for
each one named.

Create the sqlalchemy core table.
Note that it is just an sqlalchemy core table definition.
It is not represented yet in any database/engine).
Return the core table.
</summary>

'''
def sqlalchemy_core_table(
  metadata=None, table_name=None, columns=None, column_names=None,
  verbosity=0,):
    me = 'sqlalchemy_core_table'

    # create primary key column
    table_columns = [Column(
     '{}_id'.format(table_name), Integer,
      Sequence('{}_id_seq'.format(table_name)), primary_key=True,)]

    if columns is None:
        # Create simple text columns from the list of column_names
        for dc in column_names:
            print("Using Data Column name={}",c)
            table_columns.append(Column('{}'.format(c),Text))
    else: #just use columns arg
        table_columns.extend(columns)

    core_table = Table(table_name, MetaData(), *table_columns);
    if verbosity > 0:
        print("{}: returning core table {}".format(me,core_table.name))
    return core_table

'''
<summary>Create the given table_core in the engine as a persistent table
and return an sqlalchemy object representing it.
</summary>
'''
def engine_table_create (
  metadata=None, table_core=None, engine=None, verbosity=0):

    me = "engine_table_create"
    if table_core is None:
      raise ValueError("{}:Got a table_core value of None".format(me))

    if verbosity > 0:
        print('\n{}:USING--------------TABLE {}----------------------------\n'
          .format(me,table_core.name))
        print('{}:USING-----------------ENGINE {}--------------------------\n'
          .format(me,engine.name))

    if verbosity > 0:
        # print the ddl to create the table
        print('====== Start CreateTable(table_core.compile(engine) output ===')
        #print(CreateTable(table_core).compile(engine))
        print('====== End CreateTable(table_core.compile(engine) output =====')

    # Create this table in the engine.
    # If extant, do not re-create (so set arg checkFirst=True)
    engine_table = table_core.create(engine, checkfirst=True)
    return engine_table

# end engine_table_create

'''
<summary name='workbook_table_columns'
Read the workbook and sheet of the given arguments and create a BookSheetFilter
object with the given sheet_index.

Simply query the sheet column names, and simply normalized each column name
by stripping whitespace and changinge spaces to underbars, and return the
list of column names.

TODO: instead  use ss_column_name_normalize to normalize each column name and
put centralized toolbag of normalization techniques in that method.

Using this method could be a bit wasteful, as the workbook is only opened
to get out its column names.
The user may want to consider a possible workflow to only opened
the workbook sheet once.

This may be helpful to 'automatically' generate tabe column names with legal
name characters (within a database table) that a
human can easily/visibly associate to the original spreadsheet column names.

</summary>

'''

def worksheet_table_column(
  workbook_path=None,sheet_index=0,sqlalchemy_columns=None,verbosity=0 ):
    #initialize database connections for writing/inserting
    workbook = xlrd.open_workbook(workbook_path)
    sheet = workbook.sheet_by_index(sheet_index)

    # output
    #reader = SheetDictReader(book=workbook,
    reader = BookSheetFilter(book=workbook,
      sheet=sheet, row_count_header=1, row_count_values_start=2,
      sqlalchemy_columns=sqlalchemy_columns,verbosity=0)

    for column_name in reader.column_names:
        column_name = column_name.strip().lower().replace(' ', '_')
        print("{}".format(repr(column_name)))

    return reader.column_names

'''
Connect to a database and insert spreadsheet rows to table

<param names='workbook_path sheet_index'>
File path to an excel workbook to open, and use the sheet of the given index
as the data source.
</param>

<param name="od_index_column">
ordered dict where key is a row-index into a spreadsheet row,
starting at row 0, and value is a sqlalchemy Column() to use to name and store
its sqlalchemy-typed value.
</param>

<param name='engine_table'>
An sqlalchemy engine persistent database table object
</param>

<param name='engine'>
An sqlalchemy database engine/backend object.
</param>

<param name='row_count_header'>
The row count (starting at 1) in the spreadsheet with the header column names
</param>

<param name='row_count_values_start'>
The row count (starting at 1) in the spreadsheet with the row with values to
read/use. From there to the end of the spreadsheet, values will be taken
from every row for insertion into the persistent database table.
</param>

<note>
Used to use next default, but keep here for reference
  cxs_format='mysql+mysqldb://{user}:{password}@127.0.0.1:3306/{dbname}',
 </note>
'''

def spreadsheet_to_engine_table(
  workbook_path=None, sheet_index=0,
  od_index_column=None,
  table_core=None, engine_table=None,
  engine=None,
  row_count_header=1, row_count_values_start=2, verbosity=0):

    me = 'spreadsheet_to_engine_table'
    required_args = [
      'workbook_path', 'table_core', 'engine', 'od_index_column' ]

    if not all(required_args):
      msg = "Missing some required args in {}".format(repr(required_args))
      raise ValueError(msg)

    #initialize database connections for writing/inserting

    if verbosity > 1:
        # Might experiment with these later... maybe move this to a test file.
        print("+++++++++++= Experiment:Calling Metadata(engine)")
        metadata = MetaData(engine)
        print("+++++++++++= Experiment:Calling inspect(engine)")
        inspector = inspect(engine)
        print("+++++++++++= Experiment:engine.connect(engine)")
        conn = engine.connect()
        print('Connected with conn={} to database to insert into table {}'
          .format(repr(conn),table.name))
        # Warning: this causes hundreds of lines of output in a 5-table database
        print("+++++++++++= Calling metadata.reflect(engine)")
        metadata.reflect(engine)
        print("+++++++++++= Returned from metadata.reflect(engine)")
        sys.stdout.flush()

    #workbook
    workbook = xlrd.open_workbook(workbook_path)
    # initialize sheet reader for the workbook

    reader = SheetDictReader(
      book=workbook,sheet_index=sheet_index, row_count_header=row_count_header,
      row_count_values_start=row_count_values_start)

    first_sheet = workbook.sheet_by_index(reader.sheet_index)
    print("{}: SheetDictReader with sheet_index {} has column_names={}"
        .format(me, reader.sheet_index, repr(reader.column_names)))
    sys.stdout.flush()

    #Read each spreadsheet row and insert table row
    #based on od_index_column information

    i = 0
    for row in reader:
        i += 1
        if (verbosity > 0 or 1 == 1):
            msg = ("{}:reading ss row {}={}".format(me,i,repr(row)))
            print(msg.encode('utf-8'))

        od_table_column__value = {}

        # Filter out the interesting table_column value pairs for insertion
        # into the table
        for index, column in od_index_column.items():
            # Create entry in filtered dict with key of each interesting
            # output column name paired with its  row's value
            value = row[reader.column_names[index]]

            #Insert logic here -- if the column is FLOAT, and the
            #value is empty string, then insert None (for db value NULL)
            print(
              "Output:index={}, col name={}, col.type={}, type(column.type)={}"
              .format(index, column.name, column.type, type(column.type)))

            if ( type(column.type) == sqlalchemy.sql.sqltypes.Float
               or type(column.type) == sqlalchemy.sql.sqltypes.Integer
               # Add types here as needed later if db row insertion of '' fails
               # in this or that db engine of interest
               ):
                #NOTE: In postgres, do not need this replacement for integer
                # field,  but do for Float and maybe others...
                if value == '':
                    value = None
                    od_table_column__value[column.name] = value
                else:
                    value = float(value)
                    od_table_column__value[column.name] = value
                #print("Got a FLOAT set value={}".format(value))
            elif type(column.type) == sqlalchemy.sql.sqltypes.Integer:
                if value == '':
                    value = None
                    od_table_column__value[column.name] = value
                else:
                    value = float(value)
                    od_table_column__value[column.name] = value
            else:
                od_table_column__value[column.name] = value

            msg = ("index={}, column_name={}, value={}"
              .format(i,index,column.name, value))

            # Try to avoid windows msg: UnicodeEncodeError...
            # on prints to windows console, encode in utf-8
            # It works FINE!
            print(msg.encode('utf-8'))
            #print(msg)
            sys.stdout.flush()

        msg = ("row={}"
          .format(od_table_column__value))
        #engine.execute(engine_table.insert(), od_table_column__value)
        engine.execute(table_core.insert(), od_table_column__value)

        if i % 100 == 0:
           print(i)

#end spreadsheet_to_engine_table(workbook_path=None, table=None, engine=None):

'''
<summary name='spreadsheet_to_table'>
Given od_index_column, create sqlalchemy core table
and a persistent database engine table.

Note that od_index_colum row indices (key values) must refer properly to
the ultimate desired input spreadsheet column ordering (of course).

Next, pass some args down to call spreadsheet_to_engine_table to
read given spreadsheet to copy its values to the peristent database table.

</summary>

Set workbook_path to any workbook path on local drive

Given an engine nick name, a table name and od_index_column.values,
create an sqlalchemy core table.

Proceed to call spreadsheet_to_engine_table to actually read the workbook
spreadsheet and insert the rows into the database engine's table.

NOTE: If the persistent table is not extant in the engine, it will be created.
Otherwise, the rows will be appended/inserted into the extant persistent table
in the database engine.

'''
def spreadsheet_to_table(
  od_index_column=None,
  engine_nick_name=None, table_name=None,
  input_workbook_path=None, sheet_index=0,
  verbosity=0,
  ):
    me = 'spreadsheet_to_table'
    required_args =[
      'input_workbook_path',
      'od_index_column',
      'engine_nick_name',
      'table_name',
    ]
    if not all(required_args):
      msg=("{}:Mising some required args: {}"
           .format(me,repr(required_args)))
      raise ValueError(msg)

    metadata = MetaData()
    my_db_engine = get_db_engine_by_name(name=engine_nick_name)

    #Create the in-memory sqlalchemy table_core object.
    table_core = sqlalchemy_core_table(
      table_name=table_name, columns=od_index_column.values(),
      verbosity=verbosity,)

    # From the table_core, create a true persistent database table object
    engine_table = engine_table_create(
      metadata=metadata, engine=my_db_engine, table_core=table_core,
      verbosity=verbosity,)

    #Add rows to the persistent engine table from the spreadsheet
    spreadsheet_to_engine_table(
       workbook_path=input_workbook_path, sheet_index=sheet_index,
       engine_table=engine_table,
       od_index_column=od_index_column,
       engine=my_db_engine, table_core=table_core,
       verbosity=1,
       )

    return
# end spreadsheet_to_engine_table()

def run(env=None):
    me='run()'

    #NOTE set environment
    print("{}:Starting with env={}".format(me,env))

    #WINDOWS
    nick_name = 'uf_local_silodb'
    nick_name = 'uf_local_mysql_marshal1'
    nick_name = 'integration_sobekdb'

    if env == 'windows':
        engine_nick_name = 'uf_local_mysql_marshal1'
        '''
        workbook_path = ('C:\\rvp\\download\\'
          'at_accessions_rvp_20171130.xlsx')

        # todo add a param to test_spreadsheet_table for ann override type per spreadsheet native(but special chars
        # changed) column name. Use a default type for all others
        table_name = 'test_accessions'
        '''

        input_workbook_path = (
          'U:\\data\\ifas_citations\\2016\\base_info\\'
          'IFAS_citations_2016_inspected_20171218a.xls')
        sheet_index = 0

        od_index_column = OrderedDict({
          0: Column('doi',String(256)),
          1: Column('authors',Text),
          2: Column('pub_year', String(32)),
          3: Column('title', Text),
          4: Column('journal', Text),
          5: Column('volume', String(26)),
          6: Column('issue', String(26)),
          7: Column('page_range', String(26)),
          6: Column('original_line', Text),
        })
        table_name = "test_inspected5"
    elif env == 'windows2':
        engine_nick_name = 'uf_local_mysql_marshal1'

        workbook_path = ('C:\\rvp\\download\\'
          'at_accessions_rvp_20171130.xlsx')
        sheet_index = 0
        table_name = 'test_accessions'

        od_index_column = OrderedDict({
          0: Column('col0',String(256)),
          1: Column('c1',Text),
          2: Column('c2', String(32)),
          3: Column('c3', Text),
          4: Column('c4', Text),
          5: Column('c5', String(26)),
          6: Column('c6', String(26)),
          7: Column('c7', String(26)),
          6: Column('c8', Text),
        })

    elif env == 'linux':
        #Linux
        workbook_path = ('/home/robert/git/citrus/projects/lone_cabbage_2017/data/'
          'lone_cabbage_data_janapr_2017.xlsx')
        sheet_index = 0
        engine_nick_name = 'hp_psql'
        table_name = 'test_janapr'
        # Dont really need an ordered dict now, but keep in mind file dumps
        od_index_column = OrderedDict({
          0: Column('county',String(1005),nullable=True),
          1: Column('lake',String(1003),nullable=True),
          2: Column('obs_date',Date,nullable=True),
          6: Column('station_id',Float,nullable=True),
          7: Column('tp_ug_l',Float,nullable=True),
          8: Column('tn_ug_l',Float,nullable=True),
          9: Column('chl_ug_l',Float,nullable=True),
          10: Column('secchi_ft',Float,nullable=True),
          11: Column('secchi_2',String(30)),
          12: Column('color_pt_co_units',Float,nullable=True),
          13: Column('specific_conductance_us_cm_25_c',Float,nullable=True),
          14: Column('specific_conductance_ms_cm_25_c',Float,nullable=True),
        })
    elif env == 'linux3':
        engine_nick_name = 'hp_psql'

        workbook_path = ('/home/robert/git/citrus/projects/archives/data/'
          'at_names_rvp_20171130.xlsx')
        sheet_index = 0
        # This table is 'names' from ArchivistsToolkit AT ==> at_name
        table_name = 'at_name'

        od_index_column = OrderedDict({
          0: Column('nameid',Integer),
          2: Column('last_updated',Date),
          4: Column('last_updated_by', String(32)),
          6: Column('name_type', Text),
          7: Column('sort_name', Text),
          18: Column('personal_date_range_string', String(26)),
          19: Column('personal_fuller_form', String(26)),
          20: Column('personal_title', Text),
          21: Column('family_name', Text),
          24: Column('name_source', Text),
          29: Column('salutation', Text),
        })


    print(
      "{}:Using env={},\n"
      "workbook_path={},sheet_index={},\n"
      "od_index_column={},\n"
      "engine_nick_name={},table_name={}"
      .format(me,env,workbook_path,sheet_index,
        od_index_column,engine_nick_name,table_name))

    spreadsheet_to_table(
      # Identify the workbook pathname of the input workbook
      input_workbook_path=workbook_path,
      sheet_index=sheet_index,
      # Map the input workbook first spreadsheet's row's column
      # indices to the output table's sqlalchemy columns
      od_index_column=od_index_column,
      #Set the desired output engine/table_name
      engine_nick_name=engine_nick_name,table_name=table_name,
      verbosity=1,
      )

    print("Done!")
    return
#end run()

env = 'windows'
env = 'linux'
env = 'linux2' #implement soon

env = 'linux'
env = 'linux3'

run(env=env)
