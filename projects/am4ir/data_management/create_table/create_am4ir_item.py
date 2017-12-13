'''
Create Marshaling Application Website (MAW) tables 'am4ir' for
feature am4ir.
Optional here or in separate program:
Read the elsevier am4ir spreadsheet item info,
and insert it into  database table am4ir.
'''
import datetime
from sqlalchemy import (
  Boolean, create_engine,
  CheckConstraint, Column, Date, DateTime, ForeignKeyConstraint, Integer,
  MetaData, String, Table, UniqueConstraint,
  )
from sqlalchemy.schema import CreateTable

from sqlalchemy.dialects.postgresql import ARRAY

def tables_create():
    metadata = MetaData()
    tables = []

    table_name = 'am4ir_item'
    table = Table(table_name, metadata,
      Column('{}_id'.format(table_name), Integer, primary_key=True),

      Column('account', String(30),
             comment="Florida or Qatar"),

      Column('itempii', String(50),
             comment='Publisher-asserted unique id for this article'),

      Column('doi', String(150),
             comment='Digital Object ID known to all big publishers'),

      Column('itemonline', Date,
             comment="DateTime item went online"),

      Column('itemvoronline', Date,
             comment="DateTime item vor? online"),

      Column('embperiod', Integer,
             comment="Number of MONTHS in embargo period"),

      Column('embdate', Date,
             comment="Date embargo ENDS"),

      Column('itemsubtype', String(10),
             comment='Elsevier subtype of some sort.'),

      Column('issn', String(20),
             comment="issn of containing journal"),
      # NOTE: ignoring spreadsheet columns: volumestart, volumeend,issuestart
      #issueend,supplement,coverdatestart,coverdateend,firstpage,lastpage
      #itemnumber(empty anyway), date of upload (has doi anyway),
      #status (95% say 'Uploaded', 5% "No S0 and S5 in EW/VTW" or
      #"Handled in Chorus Phases")

      Column('update_dt', DateTime(6), default=datetime.datetime.utcnow,
             comment="DateTime of last update to this row"),
      # Note: v1.2 sqlalchemy: UniqueConstraint does not use list datatype
      UniqueConstraint('itempii','account',
        name='uq_{}_itempii_account'.format(table_name)),
      UniqueConstraint('doi' , 'account',
        name='uq_{}_doi_account'.format(table_name)),
      comment=(
        'Table adopts column names of source spreadsheet to simplify programs.'
        'Normalize pii before loading, and load only account Florida'),
      ) # end call to Table('article_item'...)
    tables.append(table)

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
          engine_name, strategy='mock', executor=lambda sql, *multiparams,
          **params:print(sql.compile(dialect=engine.dialect)))
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
# end def tables_create()

tables_create()
