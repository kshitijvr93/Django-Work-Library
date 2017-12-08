import os
import sys
import sqlalchemy
from sqlalchemy import (
  Column, ForeignKey, Integer,create_engine, String, Table,
  MetaData, ForeignKey, Sequence,)

print("Sqlalechemy version='{}'".format(sqlalchemy.__version__))

engine = create_engine('sqlite:///:memory:', echo=True)
metadata = MetaData()

users = Table('users', metadata,
    Column('id', Integer, Sequence('user_id_seq'), primary_key=True),
    Column('name', String(100)),
    Column('fullname', String(100)),
    Column('password', String(100)),
)
'''
print(Table('users', metadata,
    Column('id', Integer, Sequence('user_id_seq'), primary_key=True),
    Column('name', String(100)),
    Column('fullname', String(100)),
    Column('password', String(100)),
).compile(bind=create_engine('sqlite://')) )
'''

addresses = Table('addresses', metadata,
    Column('id', Integer, Sequence('user_id_seq'), primary_key=True),
    Column('user_id', None, ForeignKey('users.id')),
    Column('email_address', String(100), nullable=False),
)

metadata.create_all(engine)

print("======================================")
print(users.c.name + users.c.fullname)
for e in ['mysql://','sqlite:///:memory:']:
  print("{}:{}".format(e,(users.c.name + users.c.fullname)
    .compile(bind=create_engine(e))))
    
metadata.create_all(engine)
