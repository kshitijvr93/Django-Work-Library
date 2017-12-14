import sys
from lxml import etree
import os
import datetime
import pytz
import sys
from pathlib import Path


# CONNECT TO DB, RUN QUERY, BUILD RESULTS TO DICT, OUTPUT SOME RESULTS - SAMPLE
import os
import csv

#speedup to set large field_size_limit?
csv.field_size_limit(256789)
#import xlrd
import inspect
# import xlwt
from collections import OrderedDict

#import pypyodbc
import pyodbc
#For MySQLdb to import you must first pip in196Gstall 196Gmysqlclient
import MySQLdb
import datetime

'''
Uses installed python packages for database connectors to connect to different
databases.
DBConnection Might be superseded later by sqlalchemy methods, if they are apt.
'''
class DBConnection():
    # sample connection strings:
    # ("DRIVER={MySQL ODBC 3.51 Driver};SERVER=localhost;DATABASE=marshal1;""
    # "user=podengo;password=20MY18sql!;OPTION=3;")
    def __init__(self, connection_name=None):
        me = 'DBConnection.__init__()'
        self.verbosity = 1
        self.d_connections = {
            # Now using mysqlclient package
            # Note a different python package/driver needed OPTION=3.
            'hp8570-psql_mydb' : {
                # Note this will only connect from UF vpn
                'driver' : 'mysqlclient',
                'db_system':'mysql',
                'user':'archivesspace', 'password':'L1b-sp4c3',
                'host': '10.241.33.139','database': 'aspace'
                #'host': 'lib-archcoll','database': 'aspace'
            },
            'lib-archcoll_aspace' : {
                # Note this will only connect from UF vpn
                'driver' : 'mysqlclient',
                'db_system':'mysql',
                'user':'archivesspace', 'password':'L1b-sp4c3',
                'host': '10.241.33.139','database': 'aspace'
                #'host': 'lib-archcoll','database': 'aspace'
            },
            # It also needed 127.0.0.1:3306 (with port suffix)
            # Maybe needed here too?
            'local_mysql_marshal1' : {
                'driver' : 'mysqlclient',
                'db_system':'mysql',
                'user':'podengo', 'password':'20MY18sql!',
                'host': '127.0.0.1','database': 'marshal1'
            },
            #NOTE: from RVP Desk must FIRST TURN off cisco mobile client to reach this.
            'production_sobekdb' : {
                'db_system': 'SQL SERVER',
                'driver': 'SQL SERVER',
                'server': r'lib-sobekdb\SobekCM',
                'database': 'SobekDB',
            },
            'local_silodb' : {
                'db_system': 'SQL SERVER',
                'driver': 'SQL SERVER',
                'server': r'localhost\SQLExpress',
                'database': 'silodb',
            },
            'integration_sobekdb': {
                'db_system': 'SQL SERVER',
                'driver': 'SQL SERVER',
                'server': r'lib-ufdc-cache\\ufdcprod,49352',
                'database': 'SobekTest',

            },
        } # end d_connections

        if connection_name not in self.d_connections.keys():
            msg = ("{}: Invalid connection name {} given. Try one of:{}"
                .format(me, connection_name, repr(d_connections.keys())))
            raise ValueError(msg)

        d_connect = self.d_connections[connection_name]

        # Supported db systems and drivers.
        d_sys_drivers = {
            'mysql': ['mysqlclient'],
            'SQL SERVER': ['SQL SERVER']
        }
        self.db_system =  d_connect['db_system']
        self.field_delimiter = d_connect.get('field_delimiter','\t')

        if self.db_system not in d_sys_drivers.keys():
            raise ValueError("db_system = '{}' not supported"
                .format(self.db_system))

        self.driver = d_connect['driver']

        if self.driver not in d_sys_drivers[self.db_system]:
            raise ValueError("For db_system {}, driver {} not supported"
              .format(self.db_system,self.driver))

        self.d_connect = d_connect
        self.db_system = d_connect['db_system']
        #self.db = d_connect['database']
        self.database = d_connect['database']

        if d_connect['db_system'] == 'mysql':
            if self.driver == 'mysqlclient':
                # Use custom package mysqlclient/module MySQLdb driver
                # methods to open and return a connection.
                #See https://github.com/methane/mysql-driver-benchmarks/blob/master/bench2_world.py
                # Extract only needed keys for MySQLdb.connect(), else it chokes.
                d_mc = {k:d_connect[k] for k in [
                  'user','host','database','password']}
                self.connection = MySQLdb.connect(**d_mc)
            else:
                raise ValueError('Bad driver {}'.format(driver))

        else: # assume an sql server connection

            self.server = d_connect['server']
            # NOTE: also some of these drivers might be tested later...
            # but SQL Server works OK for my UF office pc in 2017
            drivers = ['SQL Server'
                      ,'SQL Server Native Client 9.0'
                      ,'SQL Server Native Client 10.0'
                      ,'SQL Server Native Client 11.0'
                      ]
            try:
                # NOTE: correct this later... now only SQL Server driver works
                #but NEED the literal {} wrapper.
                #https://social.msdn.microsoft.com/Forums/en-US/1e6b9ddb-ffb3-44ff-b06d-104178cc4bfe/connect-to-sql-server-express-2012-from-python-34?forum=sqlexpress

                # this part works... "DRIVER=\{SQL Server\};SERVER=;"
                self.cxs = (
                  "DRIVER={{{}}};SERVER={};dataBASE={};Trusted_connection=yes"
                  .format(self.driver,self.server, self.database))

                print("---\n{}: Trying pyodbc connect with self.cxs='{}'\n---"
                  .format(me,self.cxs))

                sys.stdout.flush()
                # Open the connection for the primary cursor
                self.connection = pyodbc.connect(self.cxs)

            except Exception as e:
                print(
                  "Connection attempt FAILED with connection string:\n'{}'"
                  ",\ngot exception:\n'{}'" .format(self.cxs,repr(e)))
                raise ValueError(
                  "{}: Error. Cannot open connection."
                  .format(repr(self)))

            if self.connection is None:
                raise ValueError(
                  "Cannot connect using pyodbc connect string='{}'"
                  .format(self.cxs))
            self.cursor = self.connection.cursor()
            if self.cursor is None:
                raise ValueError(
                  "{}: ERROR - Cannot open cursor.".format(repr(self)))
        # end sql server connection
    # end  class DBConnection.__init__()

    def query(self, query=''):
        cur = self.cursor.execute(query)
        header = ''
        for i, field_info in enumerate(cur.description):
            header += self.field_delimiter if i > 0 else ''
            header += field_info[0]

        results = []
        for row in cur.fetchall():
            result = ''
            for (i, field_value) in enumerate(row):
                result += self.field_delimiter if i > 0 else ''
                result += str(field_value)
            results.append(result)
        return header, results

#end class DBConnection()

def test_connect(connection_name=None):
    me = 'test_connect'

    #print('{}: Starting with connection_name={}'.format(connection_name)))

    try:
        print("Using connection_name='{}'".format(repr(connection_name)))
        connection = DBConnection(connection_name=connection_name)

    except Exception as e:
        msg=("Failed database connection={}:\nwith exception:\n{}"
            .format(connection_name,repr(e)))

        raise ValueError(msg)
    return connection
# end test)connect

# Test connection
connection_name = 'local_mysql_marshal1'
connection_name = 'local_silodb'
connection_name = 'integration_sobekdb'
connection_name = 'production_sobekdb'
connection_name = 'local_silodb'
connection_name = 'lib-archcoll_aspace'
connection_name = 'hp8570-psql_mydb'

print("Starting:calling test_connection")

conn=test_connect(connection_name=connection_name)

print("Got conn={}: ".format(repr(conn)))

#Insert code to do something with connection...

print("calling conn.connection.close()")

conn.connection.close()

print("Done")
