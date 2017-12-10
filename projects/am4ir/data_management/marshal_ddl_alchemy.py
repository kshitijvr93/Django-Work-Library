'''
Create Marshaling Application Website (MAW) tables for am4ir.
Read the output file of ebibvid, which has the ufdc item info,
and insert it into Marshaling Application Website database tables.
'''
import datetime
from sqlalchemy import (
  Boolean, create_engine,
  CheckConstraint, Column, DateTime, ForeignKeyConstraint, Integer,
  MetaData, String, Table, UniqueConstraint,
  )
from sqlalchemy.schema import CreateTable

from sqlalchemy.dialects.postgresql import ARRAY

def tables_create():
    metadata = MetaData()
    tables = []
    #
    table =  Table('publisher', metadata,
      Column('publisher_id', Integer, primary_key=True),
      Column('publisher_name', String(250),
             comment="Publisher name in English. Add more languages later."),
      )

    tables.append(table)

    table = Table('article_item', metadata,
      Column('article_item_id', Integer, primary_key=True),
      Column('digest_sha1_mets', String(150),
             comment='Hash for mets file for this item. See exoldmets.py'),
      Column('doi', String(150),
             comment='Digital Object ID known to all big publishers'),
      Column('is_am4ir', Boolean,
             comment='whether publisher provides accepted manuscript IR view'),
      Column('oadoi_open_access', String(16),
             comment='oadoi.org-asserted open_access status for doi'),
      Column('publisher_id', Integer,
        comment='foreign key to publisher'),
      Column('publisher_item_id', String(150),
             comment='Publisher-asserted unique id for this article'),
      Column('publisher_open_access', String(16),
             comment='Publisher-asserted open_access status'),
      Column('ufdc_bibid', String(10),
             comment="2-digit prefix followed by 8-digit integer"),
      Column('ufdc_group_id', Integer,
             comment="UFDC database sobekcm_group.group_id"),
      Column('ufdc_item_id', Integer,
             comment="Ufdc database sobekcm_item.item_id"),
      Column('ufdc_vid', Integer,
             comment="usually a 5-digit integer"),
      Column('update_dt6', DateTime, default=datetime.datetime.utcnow,
             comment="DateTime of last update to this row"),
      CheckConstraint(sqltext='ufdc_item_id = 1  or ufdc_item_id is null',
        name='ck_article_item_ufdc_item',
        comment='All articles must have item id value of 1 in ufdc' ),
      ForeignKeyConstraint(
        ['publisher_id'], ['publisher.publisher_id']),
      #Note: v1.2 sqlalchemy: UniqueConstraint does not use list datatype
      UniqueConstraint( 'ufdc_item_id','ufdc_group_id',
        name='uq_article_item_uitem_ugroup'),
      UniqueConstraint( 'doi' ,name='uq_article_item_doi' ),
      comment='Table should have only article_items that are not deleted in UFDC'
      )
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
