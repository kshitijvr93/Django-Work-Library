# This code is created to dump sql server tables to plain txt
# files. Other more db-agnostic code may be included in this repo too.
# Applications include dumping archivists toolkit tables, also cross_ref TABLES
# or others that are not plagued by SSMS 'save results' output file issues within
# subfields being written on separate output lines.
#
import os,sys
import csv
#speedup to set large field_size_limit?
csv.field_size_limit(256789)
#import xlrd
import inspect
# import xlwt
from collections import OrderedDict

import pypyodbc
import datetime

# Note: this is JUST for SQL server databases

class DBConnection():
    def __init__(self, out_delim='\t',d_params=None,
        server='lib-sobekdb\\sobekcm',db='SobekDB',verbosity=1):
        if d_params is not None:
            self.server = d_params['server']
            self.db = d_params['db']
        else:
            self.server = server
            self.db = db

        self.verbosity = verbosity
        self.out_delim = out_delim
        if out_delim is None:
            # silly clause, but just in case a caller sets this to None
            self.out_delim = '|'

        self.cxs = ("DRIVER={SQL Server};SERVER=%s;"
              "dataBASE=%s;Trusted_connection=yes"
              % (self.server, self.db))
        try:
            # Open the primary cursor for this connection.
            self.conn = pypyodbc.connect(self.cxs)
        except Exception as e:
            print(
              "Connection attempt FAILED for:\n'{}',\n"
              "Got exception:=====\n'{}'\n====="
              .format(self.cxs,repr(e)))
            raise ValueError("{}: Error. Cannot open connection."
                .format(repr(self)))

        if self.conn is None:
            raise ValueError(
              "Cannot connect using pyodbc connect string='%s'"
              % (self.cxs) )
        self.cursor = self.conn.cursor()
        if self.cursor is None:
            raise ValueError(
              "%s: ERROR - Cannot open cursor." % repr(self))

    # query(): given query string, return a tuple of
    # [0] - header string of column names, [1] list of result rows, separated by
    # self.out_delim
    def query(self, query=''):
        cur = self.cursor.execute(query)
        header = ''
        for i, field_info in enumerate(cur.description):
            header += self.out_delim if i > 0 else ''
            header += field_info[0]

        results = []
        for row in cur.fetchall():
            result = ''
            for (i, field_value) in enumerate(row):
                result += self.out_delim if i > 0 else ''
                result += str(field_value)
            results.append(result)
        return header, results

    def select(self, query=''):
        return self.query(query)


def select_ls_link_piis(conn, ntop=3):

    # Get ntop valid elsevier(ls) item 'link' values from db connection.
    # Later we will time the task of retrieving entitlement for each PII/article.
    top = "top({})".format(ntop) if ntop else ""
    query = '''
             select i.link
             from sobekcm_item i, sobekcm_item_group g
             where
               i.groupid = g.groupid and g.bibid like '%LS005%'
             order by i.link
             '''.format(top)

    header, results = conn.query(query)

    print('Tickler results with PII values include {} result rows\n'
          .format(len(results)))

    links = []
    piis = []
    for row in results:
        #print(row)
        fields = row.split('|')
        link = fields[0]
        # pii is after last slash, but before a ?, if any
        pii = link.split('?')[0].split('/')[-1]
        piis.append(pii.strip())

    return piis, query

def select_ls_item_piis(conn, ntop=3):

    # Get ntop valid elsevier PII values from db connection.
    # Later we will time the task of retrieving entitlement for each PII/article.
    top = "top({})".format(ntop) if ntop else ""
    query = '''
            select {} i.itemid, i.link
             from sobekcm_item i, sobekcm_item_group_g
             where
               i.groupid = g.groupid and g.bibid like '%LS005%'
             order by i.itemid
             '''.format(top)

    header, results = conn.query(query)

    print('The link-value derived PII values total {} values.\n'
          .format(len(results)))

    piis = []
    for row in results:
        #print(row)
        fields = row.split('|')
        piis.append(fields[len(fields)-1].strip())


    return piis, query


############################ START CONNECTION ##########################
def connect(dbname=None):
    if dbname is None:
        raise ValueError("dbname parameter is missing")


    dbname = dbname
    d_params = d_dbname_params[dbname]
    print('###### START CONNECTION for {} #####'.format(d_params))

    prod_conn = DBConnection(d_params=d_params)

    print("Succeeded: prod_conn is {}. prod_conn.server={}, conn.db={}, cxs='{}'. Done."
      .format(repr(prod_conn), prod_conn.server, prod_conn.db, prod_conn.cxs))

    print("Got connection OK.")
    return prod_conn

# Run
d_dbname_params = {
  'sobek_production': {
      'server':'lib-sobekdb\\SobekCM', 'db'    :'sobekdb'},

  'archivists_toolkit': {
      'server': 'lib-ill\\ariel', 'db'    :'ArchivistsToolkit'},

  'sobek_rvp_local' : {
      'server':'localhost\\SQLExpress', 'db'    :'rvp_test_sobekdb'},

  'silo' : {
      'server':'localhost\\SQLExpress', 'db'    :'silodb'},

  'sobek_integration_test' : {
      'server': 'lib-ufdc-cache\\ufdcprod,49352', 'db'    :'SobekTest'},
}

dbname='sobek_production'
dbname='sobek_integration_test'
dbname='sobek_rvp_local'
dbname = 'silo'
dbname='archivists_toolkit'

def test_at():
    dbname='archivists_toolkit'
    connect(dbname=dbname)

def silo_table_dump(table_name=None):
    if table_name is None:
        raise ValueError("table_name arg is missing")
    dbname = 'silo'
    cn = connect(dbname=dbname)
    print("For dbname  {}, got connection=={}"
        .format(dbname,repr(cn)))
    return cn.query('select * from {}'.format(table_name))

def dbname_query(dbname=None, query=None):
    cn = connect(dbname=dbname)
    print("Successful connection string={}")
    return cn.query(query)

dbname = 'archivists_toolkit'
query =  'select * from accessions'
# these 2 work ok 20171129
dbname = 'silo'
query = 'select * from ccila_record'

dbname = 'archivists_toolkit'
query =  'select * from accessions'

header, results = dbname_query(dbname=dbname, query=query)

print("Got header={}".format(repr(header)))
print("Got {} rows".format(len(results)))

print ("Done!")
sys.stdout.flush()
