import os
import csv
#speedup to set large field_size_limit?
csv.field_size_limit(256789)
#import xlrd
import inspect
# import xlwt
from collections import OrderedDict

import pypyodbc
import datetime

class DBConnection():
    def __init__(self, server='lib-sobekdb\\sobekcm',db='SobekDB'):
        self.verbosity = 1
        self.server = server
        self.db = db
        self.outdelim = '|'
        self.cxs = ("DRIVER={SQL Server};SERVER=%s;"
              "dataBASE=%s;Trusted_connection=yes"
              % (self.server, self.db))
        try:
            # Open the primary cursor for this connection.
            self.conn = pypyodbc.connect(self.cxs)
        except Exception as e:
            print("Connection attempt FAILED with connection string:\n'{}',\ngot exception:\n'{}'"
                 .format(self.cxs,repr(e)))
            raise ValueError("{}: Error. Cannot open connection.".format(repr(self)))

        if self.conn is None:
            raise ValueError(
              "Cannot connect using pyodbc connect string='%s'"
              % (self.cxs) )
        self.cursor = self.conn.cursor()
        if self.cursor is None:
            raise ValueError(
              "%s: ERROR - Cannot open cursor." % repr(self))

    # query(): given query string, return a tuple of
    # [0] - header string of column names, [1] list of result rows, separated by self.outdelim
    def query(self, query=''):
        cur = self.cursor.execute(query)
        header = ''
        for i, field_info in enumerate(cur.description):
            header += self.outdelim if i > 0 else ''
            header += field_info[0]

        results = []
        for row in cur.fetchall():
            result = ''
            for (i, field_value) in enumerate(row):
                result += self.outdelim if i > 0 else ''
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
print('############################ START CONNECTION ##########################')
cn = 'prod'
if cn == 'prod':
    prod_conn = DBConnection(server='lib-sobekdb\\sobekCM',db='SobekDB')

    print("Succeded: prod_conn is {}. prod_conn.server={}, conn.db={}, cxs='{}'. Done."
          .format(repr(prod_conn), prod_conn.server, prod_conn.db, prod_conn.cxs))

elif cn== 'test':
    #test_conn = DBConnection(server='lib-ufdc-cache\ufdcprod,49352',db='SobekTest')
    test_conn = DBConnection(server='lib-ufdc-cache\\ufdcprod,49352', db= 'SobekTest')

    print("Succeded: test_conn is {}. .server={}, db={}, cxs='{}'. Done."
          .format(repr(test_conn), test_conn.server, test_conn.db, test_conn.cxs))
elif cn == 'dev':
    dev_conn = DBConnection(server="UFLIBSHS3TC42", db='SobekCM')
    print ("Succeeded with dev_conn, and connection string: {}".format(dev_conn.cxs))
else:
    raise ValueError("Error: no connection is registered for cn={}".format(cn))

print("Got connection OK.")