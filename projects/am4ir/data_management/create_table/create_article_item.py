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

    table_name = 'article_item'
    table = Table(table_name, metadata,
      Column('article_item_id', Integer, primary_key=True),
      Column('digest_sha1_mets', String(150),
             comment='Hash for mets file for this item. See exoldmets.py'),
      Column('doi', String(150),
             comment='Digital Object ID known to all big publishers'),
      Column('eid', String(30),
             comment="eid yet another article id"),
      Column('is_am4ir', Boolean,
             comment='whether publisher provides accepted manuscript IR view'),
      Column('oadoi_open_access', String(16),
             comment='oadoi.org-asserted open_access status for doi'),
      Column('api_create_dt', DateTime, default=datetime.datetime.utcnow,
        comment=('DateTime this item was created at source api. Elsevier calls'
        ' it orig_load_date, Crossref api calls it deposit_date, etc'),
      ),
      Column('publisher_id', Integer,
             comment='Has foreign key to publisher.publisher_id'),
      Column('publisher_item_id', String(50),
             comment='Publisher-asserted unique id for this article'),
      Column('publisher_open_access', String(16)),
      Column('scopus_id', String(20),
             comment="scopus_id owned by Elsevier as of year 2017 "),
      Column('ufdc_bibid', String(10),
             comment="2-digit prefix followed by 8-digit integer"),
      Column('ufdc_group_id', Integer,
             comment="UFDC database sobekcm_group.group_id"),
      Column('ufdc_item_id', Integer,
             comment="Ufdc database sobekcm_item.item_id"),
      Column('ufdc_vid', Integer,
             comment="usually a 5-digit integer"),
      Column('embargo_end_dt', DateTime,
             comment="DateTime public embargo ended, per publisher"),
      Column('update_dt', DateTime, default=datetime.datetime.utcnow,
             comment="DateTime of last update to this row"),
      CheckConstraint(sqltext='ufdc_item_id = 1  or ufdc_item_id is null',
        name='ck_{}_ufdc_item'.format(table_name) ),
      ForeignKeyConstraint(
        ['publisher_id'], ['publisher.publisher_id'],
        name='fk_{}_publisher_id'.format(table_name)),
      # Note: v1.2 sqlalchemy: UniqueConstraint does not use list datatype
      UniqueConstraint('ufdc_item_id','ufdc_group_id',
        name='uq_{}_uitem_ugroup'.format(table_name)),
      UniqueConstraint('doi' ,name='uq_{}_doi'.format(table_name)),
      UniqueConstraint('eid' ,name='uq_{}_eid'.format(table_name)),
      UniqueConstraint('scopus_id',
         name='uq_{}_scopus_id'.format(table_name)),
      UniqueConstraint('digest_sha1_mets',
         name='uq_{}_mets'.format(table_name)),
      # Table-level comment
      comment=(
        'Table should have only article_items that are not deleted in UFDC'),
      ) # end call to Table('article_item'...)
    tables.append(table)

    # sqlalchemy engines
    d_ename_extension = {
      'mysql+pyodbc://./MyDb': {'extension': '_mssql.sql'},
      # comment out some for now to declutter
      #'sqlite:///:memory:': {'extension': '_sqlite.sql'},
      'postgresql://': {'extension':'_postgresql.sql'},
      #'oracle+cx_oracle://': {'extension':'_oracle.sql'},
      #'mssql+pyodbc://': {'extension':'_mssql.sql'},
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
