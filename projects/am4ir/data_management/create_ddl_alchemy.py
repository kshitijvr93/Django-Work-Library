'''
Read the output file of ebibvid, which has the ufdc item info...
--
'''
from sqlalchemy import (
  Table, Column, Integer, String, MetaData, ForeignKey, create_engine)
from sqlalchemy.schema import CreateTable

from sqlalchemy.dialects.postgresql import ARRAY

def tables_create():
    metadata = MetaData()
    tables = []
    #
    table =  Table('publisher', metadata,
      Column('publisher_id', Integer, primary_key=True, comment='abc' ),
      Column('publisher_name', String(250)),
      )
    tables.append(table)

    table = Table('article_item', metadata,
      Column('article_item_id', Integer, primary_key=True),
      Column('publisher_name', String(250)),
      )
    tables.append(table)


    # sqlalchemy engines
    d_ename_extension = {
      'mysql+pyodbc://./MyDb': {'extension': '_mssql.sql'},
      'sqlite:///:memory:': {'extension': '_sqlite.sql'},
      'postgresql://': {'extension':'_postgresql.sql'},
      'oracle+cx_oracle://': {'extension':'_oracle.sql'},
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
# end def tables_create()

tables_create()
