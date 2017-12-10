'''
Read the output file of ebibvid, which has the ufdc item info...
--
'''
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.schema import CreateTable
def tables_create():
    metadata = MetaData()
    #
    publisher = Table('publisher', metadata,
      Column('publisher_id', Integer, primary_key=True)
      )

    print(CreateTable(publisher))

    return
# end def tables_create()

tables_create()
