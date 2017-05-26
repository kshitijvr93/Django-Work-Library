import sys
from lxml import etree
import os
import datetime
import pytz
import sys
from pathlib import Path

# To an lxml tree, add subelements recursively from nested python data structures
# This is useful to register log message traces and to output into xml format at the end of a run.
def add_subelements(element, subelements):
    if isinstance(subelements, dict):
        d_subelements = OrderedDict(sorted(subelements.items()))
        for key, value in d_subelements.items():
            # Check for valid xml tag name:
            # http://stackoverflow.com/questions/2519845/how-to-check-if-string-is-a-valid-xml-element-name
            # poor man's check: just prefix with Z if first character is a digit..
            # the only bad type of tagname encountered using various applications... so far ...
            if key[0] >= '0' and key[0] <= '9':
                key = 'Z' + key
            subelement = etree.SubElement(element, key)
            add_subelements(subelement, value)
    elif isinstance(subelements, list):
        # Make a dict indexed by item index/count for each value2 in the 'value' that is a list
        for i, value in enumerate(subelements):
            subelement = etree.SubElement(element, 'item-{}'.format(str(i+1).zfill(8)))
            add_subelements(subelement, value)
    else: # Assume it is a string-like value. Just set the element.text and do not recurse.
        element.text = str(subelements)
    return True
# end def add_subelements()

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
import datetime

class DBConnection():
    def __init__(self, server='lib-sobekdb\\sobekcm',db='SobekDB',driver_index=0):
        self.verbosity = 1
        self.server = server
        self.db = db
        self.outdelim = '\t'
        drivers = ['SQL Server'
                  ,'SQL Server Native Client 9.0'
                  ,'SQL Server Native Client 10.0'
                  ,'SQL Server Native Client 11.0'
                  ]
        self.cxs = ("DRIVER={%s};SERVER=%s;"
              "dataBASE=%s;Trusted_connection=yes"
              % (drivers[driver_index],self.server, self.db))
        try:
            # Open the primary cursor for this connection.
            #self.conn = pypyodbc.connect(self.cxs)
            self.conn = pyodbc.connect(self.cxs)

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

#end class DBConnection()

#
# NOTE: The selected columns and column order are relied upon by caller, so do not change them.
def select_ls_bibvid_piis(conn, ntop=3):
    l_messages=[]
    l_messages.append("Building d_bibvid dictionary of bibvids for Elsevier...")
    # Get ntop rows from db connection with a query herein.
    # Return messages, a dictionary d_bibvid of results.
    # Later we will time the task of retrieving entitlement for each PII/article.
    # NOTE: the %LS005% condition is a capitulation to the sad state that lower bib values
    # that are BAD elsevier records haunt the SobekCM v4.9 database since january 2016 since
    # there is not a clean and quick way to delete old records yet. Maybe in v4.10.
    #
    top = "top({})".format(ntop) if ntop else ""
    query = '''
             select g.bibid, i.vid, i.itemid, i.groupid, i.link
             from sobekcm_item i, sobekcm_item_group g
             where
               i.groupid = g.groupid and g.bibid like '%LS005%'
             order by i.link
             '''.format(top)

    header, results = conn.query(query)

    l_messages.append("Query='{}':\n returned PII values in {} result rows\n"
          .format(query, len(results)))

    rows = [] # result rows
    d_bibvid = {}
    d_piis = {}
    for row in results:
        #print(row)
        fields = row.split('\t')
        bibvid='{}_{}'.format(fields[0],fields[1])
        link_index=4
        link = fields[link_index]
        # pii is after last slash, but before a ?, if any
        part_qs = link.split('?')
        is_oac = False
        if len(part_qs) > 1:
            part_sides = part_qs[1].split('=')
            if len(part_sides) > 1:
                # 20160707- if ? is in link suffix, then it may have oac=x at the end, where x is true or false
                is_oac = True if part_sides[1] == 't' else False

        # link has pii value as last slash-delimited field before q mark.
        pii = part_qs[0].split('/')[-1]

        #overwrite link result field with just the is_oac value
        fields[link_index] = repr(is_oac)

        rows.append(fields)

        rows.append(repr(is_oac))

        d_bibvid[bibvid] = fields[2:]

        obibvid = d_piis.get(pii,None)
        if obibvid is not None:
            l_messages.append(
                "WARNING:PII {} is first associated with bibid {}."
                " Ignoring its additional association with bibid={}"
                .format(pii, obibvid, bibvid))
        else:
            d_piis[pii] = fields[:]

    return l_messages,d_bibvid, query, d_piis
# end def ls_select_bibvid

def ls_mets_validate(d_bibvid, resources_folder):
    all_ok = False
    l_messages = []
    l_messages.append("Starting...")
    l_messages.append("Done. all_ok={}".format(repr(all_ok)))
    return l_messages, all_ok

#end ls_mets_validate

# TEST RUN ON PRODUCTION - EBIBVID ---
# DO the select
if 1==1:
    #########
    try:
        #test_conn = DBConnection(server='lib-ufdc-cache\ufdcprod,49352',db='SobekTest')
        # conn = DBConnection(server='lib-ufdc-cache\\ufdcprod,49352', db= 'SobekTest')

        # PRODUCTION DATABASE #NOTE: from RVP Desk must FIRST TURN off cisco mobile client to reach this.
        server = r'lib-sobekdb\SobekCM'
        db = 'SobekDB'
        conn = DBConnection(server=server, db=db)
        cxs = conn.cxs

    except Exception as e:
        print("Failed connection to server=n{},db={}:\nwith exception:\n{}".format(server,db,repr(e)))
        raise e

    #conn = test_conn

    ########
    d_log = {}
    d_params = {}
    d_log['params'] = d_params

    # We also use secsz_start as part of a filename, but windows chokes on ':'
    # in a filename, so use all hyphens for delimiters
    utc_now = datetime.datetime.utcnow()
    secsz_begin = utc_now.strftime("%Y-%m-%dT%H-%M-%SZ")

    # elsevier_base
    elsevier_base = ('c:/rvp/elsevier')
    app_run = 'ebibvid/{}'.format(secsz_begin)

    #20160624 testing..
    output_folder = '{}/output_test/{}'.format(elsevier_base, app_run)
    log_filename = '{}/logfile.xml'.format(output_folder)

    output_dict_pii_filename = (
        "{}/dictionary_pii_bibvid_ou_smathers.txt".format(output_folder))

    d_params['connection-string'] = conn.cxs
    d_params['output-folder'] = output_folder
    os.makedirs(output_folder, exist_ok=True)

    d_params['secsz-begin'] = secsz_begin

    ## MAIN WORK --  Create the dictionaries
    l_messages,d_bibvid,query,d_pii = select_ls_bibvid_piis(conn, ntop=0)
    d_log['step-001-select_ls_bibvids_piis'] = l_messages

    # Save d_pii dictionary to csv file for use by eatxml, other utilities
    # RESUME...

    od_pii = OrderedDict(d_pii)

    d_log['output-dict-pii-filename'] = output_dict_pii_filename
    print("printing to output_dict_pii_filename={}".format(output_dict_pii_filename))
    with open(output_dict_pii_filename, 'w') as outfile:
        for i,(key,value) in enumerate(od_pii.items()):
            if i % 1000 == 0:
                print("{}, key={}, value[]={}".format(i, repr(key), repr(value)))
            # combine bib with vid with intervening underbar for primary user, program extmets
            print("{},{}_{},{},{},{}".format(key,value[0],value[1],value[2],value[3],value[4])
                 ,file=outfile)

    # TODO: visit resources directories of LS bibvid named METS files and validate pii value.
    # TODO: also modify to validate pii and hash values for limited set of LS bibvids.
    # todo: add support to give option to visit ALL resource LS mets files and report any
    # that exist for which we do not have a d_bibvid entry.

    # Set resources folder: may need to double-up on backslashes, just test it first.
    # PRODUCTION: resources_folder = '\\flvc.fs.osg.ufl.edu\flvc-ufdc\resources'

    # TEST SYSTEM RESOURCES FOLDER:
    resources_folder = (
      '\\\\osg-prod.cns-fs04.osg.ufl.edu\\uflibfs01\\DeptData\\IT\\WebDigitalUnit'
      '\\testufdc_elsevier\\resources\\')

    # TODO: Or move this to its own utility that reads the d_bibvid dictionary file.
    # Validate that all bibvid-prefixed mets files in resource folder have the pii
    # that we got from sobekcm database query as part of the SobekCM_Item table's 'link' column value.
    # l_messages, all_ok = ls_mets_validate(d_bibvid, resources_folder)
    # d_log['step-002-ls-mets-validate'] = l_messages

    # Final Log Output
    utc_now = datetime.datetime.utcnow()

    secsz_end = utc_now.strftime("%Y-%m-%dT%H-%M-%SZ")
    d_params['secsz_end'] = secsz_end

    e_root = etree.Element("uf-ebibvid")
    #add_subelements_from_dict(e_root, d_log)
    add_subelements(e_root, d_log)

    with open(log_filename, 'wb') as outfile:
        outfile.write(etree.tostring(e_root, pretty_print=True))

    rv="See output log file name='{}'".format(log_filename)
