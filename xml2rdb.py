#
# xml2rdb-active
# Somewhat cleaned-up code with various debug statements and cruft removed
# to use as a supplement document for IP examination

'''
Program xml2rdb inputs xml docs from saved xml files (for example from the Elsevier Publisher's
full-text api).
Each input xml file has xml-coded information pertaining to a single xml document.
'''
import datetime
import pytz
import os
import sys

from pathlib import Path
import hashlib

from lxml import etree
from lxml.etree import tostring
from pathlib import Path
import etl

#- - - - - - - - - - - START USER PARAMETERS
'''
    Note: I also envision a revision of this program to do an initial walk-through of the
    xml input files.
    From that, it will derive a complete set of SQL tables, infer and define the entire
    hierarchical structure, and glean all of the XML input into relational tables
    for a consistent set of structured XML files.

    It will infer names for tables and columns from the xml tags and attribute names as well.

    However the user configuration will remain useful mainly to simplify and target creation
    of SQL data to simplify and abbreviate the outputted SQL database.
    That would make some studies easier to follow and faster to create and run selected
    sub-analyses of the entire pool of xml data.
'''

'''
Method sql_mining_params_elsevier

Plain Python code here define and return the two main data structures:
(1) od_rel_datacolumns: defines RDB output tables and data columns per table.
     Note: table columns for the primary key composite index for each table are
     defined indirectly by input structure 2, and populated automatically by xml2rdb
(2) d_node_params: Define a 'mining  map'. It is a nested hierarchy of relative XPATH
    expressions leading to XML nodes, each with a
    with a map of xml tag(text) or attribute values to output to associated SQL table columns.

The functionality of doing custom configuration can move to using configuration files to
assist users who are not familiar with Python.
'''
def sql_mining_params_elsevier():

    '''
    d_nodeparams is a dictionary hierarchy of parameters for a call to node_visit_output().

    The d_nodeparams dictionary may have keys with the following described values:
    Key 'multiple':
        If present, this means that this node will produce some output db data, and it means that the
        other keys in this dictonary will be examined.
        If not present, any other keys listed below will be ignored.
        The value of 0 means this is a single (or zero)-occurrence node under its parent,
        and value of 1 means that it is a multiple-occurrence node under its parent.
        This parameter may be removed soon. The presence of a dbname rather can be used to infer that
        a node has multiple of 1 and the absence of a dbname for a node implies a multiple value of 0.
    Key 'db_name':
       This is the table name for a db-relation for this node, which is allowed to appear multiple
       times under its ancestor node. The node count under its ancestor will be outputted as part
       of a sql table row composite key value.
    Key 'text':
        If present, this means that the text value of the visited node is to be output, with the
        value being the name of the db output column to use for the output of any text value of this node.
        However if that value is None or empty, the column name will be the db_name value.
        Note: the user must pre-examine all the  db_name and text values to make sure that those
        under the same immediate parent xpath have unique names.
        And that no db_name with multiple = 1 is a duplicate name.
    Key 'attrs':
        If present, the value is a list of attribute names to produce the database column
        names named in the values.
        A value for each db column name will be output, regardless of whether that attribute names is
        found on a particular node.
        The special name 'text' now means to output the content of the node, rather than an attribute.
        This special name may change to 'node_content' soon to avoid collision with valid attributes
        also named 'text' in some cases.
    Key 'child-xpaths'
        If present, the xpath must lead to a descendant node in the tree, and the the value is another
        dictionary like the d_nodeparams dictionary.

    '''

    '''
    Note: The main program declares a root node relation name, 'doc', and affixes one special
    column_name, called 'file_name', where it records the file name of the inputted xml doc.
    Therefore, this od_rel_datacolumns dictionary below must define one table/key called 'doc' with
    the column 'file_name', and add any other desired column names there as well.
    An option to not require this of course can be easily added.

    Program xml2rdb will parse each xml file to an xml document tree with a document root,
    and it will call node_visit_output(d_node_params) on that doc root.
    Maybe a paramter will be added to allow selection of another root relation name than 'doc',
    but it is not a bad general name, as it is a node to describe a doc metadata, like the
    input filename for it and other data about it...

    Note: I also envision a revision of this program to do a walk-through of the xml input files and derive
    a complete set of SQL tables, infer and define the entire hierarchical structure, and glean all of
    the XML input into relational tables (for a consistent set of structured XML). It will infer names
    for tables and columns from the xml tags and attribute names as well.
    '''

    od_rel_datacolumns = OrderedDict([
        ('doc', OrderedDict([
            ('serial_type','0'),
            ('pii',''),
            ('doi',''),
            ('eid',''),
            ('first_author_surname',''),
            ('first_author_initial',''),
            ('open_access','0'),
            ('cover_year',''),
            ('cover_date',''),
            ('title',''),
            ('publication_name',''),
            ('file_name',''),
        ])),

        ('author_group', OrderedDict([('id','')])),

        ('author', OrderedDict([
            ('id',''),
            ('given_name',''),
            ('surname',''),
            ('last_first_name', ''),
            ('degrees',''),
            ('roles',''),
            ('e_address',''),
            ('e_type',''),
        ])),

        ('author_ref', OrderedDict([
            ('id',''),
            ('refid',''),
        ])),

        ('affiliation', OrderedDict([
            ('id',''),
            ('uf',''),
            ('name',''),
            ('org_name',''),
            ('address_line',''),
            ('city',''),
            ('state',''),
            ('postal_code',''),
        ])),

        ('correspondence', OrderedDict([
            ('id',''),
            ('info',''),
            ('org_name',''),
            ('address_line',''),
            ('city',''),
            ('state',''),
            ('postal_code',''),
        ])),

        ('organization_aff', OrderedDict([
            ('id',''),
            ('org_name',''),
        ])),

        ('organization_cor', OrderedDict([
            ('id',''),
            ('org_name',''),
        ])),
    ])
    # - - - - - - - DEFINE COMPONENTS OF, AND FINALLY, d_node_params, the 'Mining Map'.
    '''
    For nonserial items, visual inspection of multiple xml files indicates that
    every author listed in an author-group is associated with
    every affiliation listed in that author-group, and this association is different from
    serial items (below).
    '''
    d_affiliation_sa_affiliation = {
        #'db_name':'sa_affiliation',
        'multiple':0,

        'child_xpaths' : {
            './/sa:organization':{ 'db_name':'organization_aff', 'multiple':1,
                'attrib_column':{'text':'org_name'},
            },
            './/sa:address-line':{ 'multiple':0,
                'attrib_column':{'text':'address_line'},
            },
            './/sa:city':{ 'multiple':0,
                'attrib_column':{'text':'city'},
            },
            './/sa:state':{ 'multiple':0,
                'attrib_column':{'text':'state'},
            },
            './/sa:postal-code':{'multiple':0,
                'attrib_column':{'text':'postal_code'},
            },
        }
    }

    d_correspondence_sa_affiliation = {
        #'db_name':'sa_affiliation',
        'multiple':0,

        'child_xpaths' : {
            './/sa:organization':{ 'db_name':'organization_cor', 'multiple':1,
                'attrib_column':{'text':'org_name'},
            },
            './/sa:address-line':{ 'multiple':0,
                'attrib_column':{'text':'address_line'},
            },
            './/sa:city':{ 'multiple':0,
                'attrib_column':{'text':'city'},
            },
            './/sa:state':{ 'multiple':0,
                'attrib_column':{'text':'state'},
            },
            './/sa:postal-code':{'multiple':0,
                'attrib_column':{'text':'postal_code'},
            },
        }
    }

    d_nonserial_author_group = {
        'db_name':'author_group', 'multiple':1,
        'attrib_column': {'id':'id'},
        'column_constant': {'serial_type':0},
        'child_xpaths':{
            ".//ce:author":{
                'db_name':'author', 'multiple':1,
                'attrib_column' : {'id':'id', 'last_first_name':'last_first_name'},
                'column_function' : {'last_first_name':last_first_name},

                'child_xpaths':{
                    './/ce:given-name':{
                        'db_name':'given_name','multiple':0,
                        'attrib_column':{'text':'given_name'}
                    }
                    ,'.//ce:surname':{
                        'db_name':'surname', 'multiple':0,
                        'attrib_column':{'text':'surname'}
                    }
                    ,'.//ce:degrees':{
                        'db_name':'degrees', 'multiple':0,
                        'attrib_column':{'text':'degrees'}
                    }
                    ,'.//ce:e-address':{
                        'db_name':'e_address',
                        'multiple':0,
                        'attrib_column':{'text':'e_address','type':'e_type', }
                    }
                    ,'.//ce:cross-ref':{
                        'db_name':'author_ref', 'multiple':1,
                        'attrib_column':{'id':'id', 'refid':'refid'}
                    }

                }

            }
            ,".//ce:affiliation":{
                'db_name':'affiliation', 'multiple':1,
                'attrib_column':{'id':'id'},
                'child_xpaths':{
                    './/ce:textfn':{
                        'multiple':0,
                        'attrib_column':{'text':'name', 'uf':'uf'},
                        'column_function' : {'uf':(uf_affiliation_by_colname,{'colname':'name'})},
                    },
                    './/sa:affiliation':d_affiliation_sa_affiliation,
                }
            }
            ,".//ce:correspondence":{
                'db_name':'correspondence', 'multiple':1,
                'attrib_column':{'id':'id'},
                'child_xpaths':{
                    './/ce:text':{
                        'multiple':0,
                        'attrib_column':{'text':'info'},
                    },
                    './/sa:affiliation':d_correspondence_sa_affiliation,
                }
            }
        }
    }
    # end d_nonserial_author_group

    '''
    For serial items, visual inspection shows that in an author-group each author normally has a subelt
    'cross-ref' with a refid value starting with af and integer suffix, and that integer suffix matches
    the integer suffix part of an 'id' attribute for a unique affiliation subelt of the same author group,
    thereby identifying the affiliation of each author. So we extract each author cross-ref so that once the
    xml data is loaded into relational db tables, a custom query can be done for 'serial' authors to make
    reports of those author-affiliations.
    A different query (see above) would be used for author-affiliation associations for the 'B' book
    or 'nonserial' items,and see above for those details.
    '''

    # Input parameter structure - od_rel_columns:
    # For each relation name (for d_node_params dict nodes with multiple=1 and db_name
    # is the relation name, the key here)
    # Note: the 'primary key' columns are defined separately from these 'data' columns
    # for every relation/table.
    # Those primary key columns are now
    # inferred from the d_node_param rooted dicts with child_xpaths.
    #
    # Here are:
    # (1) the relation/table names, ordered (to allow for future foreign key
    #     dependencies on bulk inserts), and
    # (2) the 'data' column names, which are ordered as well to allow customized
    #     setting of column order, each followed by its default string value, empty
    #   for all for now.
    #
    # Note - Later for each column name may extend to set a db datatype and also
    # set default value too, but now assume empty string.

    d_serial_author_group = {
        'db_name':'author_group', 'multiple':1,
        'attrib_column': {'id':'id'},
        'column_constant': {'serial_type':1},

        'child_xpaths':{
            ".//ce:author":{
                'db_name':'author', 'multiple':1,
                'attrib_column' : {'id':'id', 'last_first_name':'last_first_name'},
                'column_function' : {'last_first_name':last_first_name},
                'child_xpaths':{
                    './/ce:given-name':{
                        'db_name':'given_name',
                        'multiple':0,
                        'attrib_column':{'text':'given_name'}
                        }
                    ,'.//ce:surname':{
                        'db_name':'surname',
                        'multiple':0,
                        'attrib_column':{'text':'surname'}
                        }
                    ,'.//ce:degrees':{
                        'db_name':'degrees',
                        'multiple':0,
                        'attrib_column':{'text':'degrees'}
                        }
                    ,'.//ce:e-address':{
                        'db_name':'e_address',
                        'multiple':0,
                        'attrib_column':{'text':'e_address'}
                        }
                    ,'.//ce:cross-ref':{
                        'db_name':'author_ref',
                        'multiple':1,
                        'attrib_column':{'id':'id', 'refid':'refid'}
                        }
                }
            }
            ,".//ce:affiliation":{
                'db_name':'affiliation', 'multiple':1,
                'attrib_column':{'id': 'id'},
                'child_xpaths':{
                    './/ce:textfn':{
                        #'db_name':'name',
                        'multiple':0,
                        'attrib_column':{'text':'name', 'uf':'uf'},
                        'column_function' : {'uf':uf_affiliation_value}
                    },
                    './/sa:affiliation':d_affiliation_sa_affiliation,
                }
            }
            ,".//ce:correspondence":{
                'db_name':'correspondence',
                'multiple':1,
                'attrib_column':{'id':'id'},
                'child_xpaths':{
                    './/ce:text':{
                        #'db_name':'name',
                        'multiple':0,
                        'attrib_column':{'text':'info'},
                        },
                    './/sa:affiliation':d_correspondence_sa_affiliation,
                }
            }
        }
    }
    # end d_serial_author_group

    d_node_params = {
        #
        # The db_name of this root node is always set by the caller, so db_name is
        # NOT given for this node.
        # Must use multiple 0 for this root node too, for technical reasons.
        #
        'multiple':0,
        'child_xpaths' : {
            ".//{*}coredata/{*}pii": {
                'multiple':0,
                'attrib_column': { 'text':'fpii' }, # 'fpii' name need not be used in output relation.
                'column_function': {'pii': pii_unformatted}
            }
            ,".//{*}coredata/{*}eid": {
                'multiple':0,
                'attrib_column': { 'text':'eid' },
            }
            ,".//{*}openaccess": {
                'db_name':'open_access', 'multiple':0,
                'attrib_column': {'text':'open_access' }
            }
            ,".//prism:publicationName":{
                'db_name':'publication_name', 'multiple':0,
                'attrib_column':{'text':'publication_name'}
            }
            ,".//prism:doi":{
                'multiple':0,
                'attrib_column':{'text':'doi'},
            }
            ,".//prism:coverDate":{
                'multiple':0,
                'attrib_column':{'text':'cover_date', 'cover_year':'cover_year'},
                'column_function': {'cover_year': cover_year}
            }
            ,".//dc:title":{
                'multiple':0,
                'attrib_column':{'text':'title'}
            }
            ,".//xocs:title":{
                'multiple':0,
                'attrib_column':{'text':'title'}
            }
            ,".//xocs:normalized-first-auth-surname":{
                'multiple':0,
                'attrib_column':{'text':'first_author_surname'}
            }
            ,".//xocs:normalized-first-auth-initial":{
                'multiple':0,
                'attrib_column':{'text':'first_author_initial'}
            }
            ,".//xocs:serial-item":{
                'multiple':0,
                'column_constant':{'serial_type':'1'},
                'child_xpaths' : {
                    ".//ce:author-group":d_serial_author_group
                }
            }
            ,".//xocs:nonserial-item":{
                'multiple':0,
                'column_constant':{'serial_type':'0'},
                'child_xpaths' : {
                    ".//ce:author-group":d_nonserial_author_group
                }
            }
        } # end child_xpaths
    } # end d_node_params
    return od_rel_datacolumns, d_node_params
#end def sql_mining_params_elsevier()

######################### USER-DEFINED VALUE DERIVATION METHODS ##########################
'''
NOTE: these methods must all take the single argument of d_row
Any method may use any column value found in d_row, which has values
of all child singleton nodes to the node that uses any derivation function
in the mining map.

'''

import re

def last_first_name(d_row):
    first_name = d_row['given_name'] if 'given_name' in d_row else ''
    last_name = d_row['surname'] if 'surname' in d_row else ''

    return '{}, {}'.format(last_name,first_name)

def uf_affiliation(text_lower=None):
    for match in ['university of florida','univ.fl','univ. fl'
        ,'univ fl' ,'univ of florida'
        ,'u. of florida','u of florida']:
        if text_lower.find(match) != -1:
            #print("Match")
            return '1'
    #end for match
    return '0'


def uf_affiliation_value(d_row):
    if 'name' in d_row:
        text_lower = d_row['name'].lower()
    else:
        text_lower = ''
    return uf_affiliation(text_lower)

def lower_by_colname(d_row,d_params):
    name = d_params.get('colname', None)
    #print("Found colname to use of {}".format(name))
    if name is None:
        raise Exception("Did not find colname paramter")
    if name in d_row:
        text_lower = d_row[name].lower()
        #print("Checking affiliation_name={}".format(text_lower))
    else:
        text_lower=''
    return text_lower

def uf_affiliation_by_colname(d_row,d_params):
    name = d_params.get('colname', None)
    #print("Found colname to use of {}".format(name))
    if name is None:
        raise ValueError("Did not find colname paramter")
    if name in d_row:
        text_lower = d_row[name].lower()
        #print("Checking affiliation_name={}".format(text_lower))
    else:
        text_lower=''
        #print("No given affiliation_name={}".format(text_lower))

    rv = uf_affiliation(text_lower)
    #print("Got uf_affiliation={}".format(rv))
    return rv




def cover_year(d_row):
    if 'cover_date' in d_row:
        # maybe check for length later... but all input data seems good now
        return(d_row['cover_date'][0:4])
    else:
        return ''
    return #need this or pass else highlighting syntax error on next def

def pii_unformatted(d_row):
    if 'fpii' in d_row:
        # maybe check for length later... but all input data seems good now
        return(d_row['fpii'].replace('-','').replace('(','').replace(')','').replace('.',''))
    else:
        return ''

###### START SCOPUS INPUT PARAMS ########

###### START OADOI INPUT PARAMETERS ########
def sql_mining_params_oadoi():

    od_rel_datacolumns = OrderedDict([
        ('oadoi', OrderedDict([
            ('title',''),
            ('doi',''),
            ('doi_resolver',''),
            ('evidence',''),
            ('free_fulltext_url',''),
            ('is_boa_license',''),
            ('is_free_to_read',''),
            ('is_subscription_journal',''),
            ('license',''),
            ('oa_color',''),
            ('doi_url',''),
        ])),
    ])

#----------------------------------------------
    d_node_params = {
        #
        # The db_name of this root node is given in a runtime parameter, so db_name is
        # not given for this node.
        #
        'multiple':0,
        'child_xpaths' : {
            ".//{*}_title": {
                'multiple':0,
                'attrib_column': { 'text':'title' },
            }
            ,".//{*}doi": {
                'multiple':0,
                'attrib_column': { 'text':'doi' },
            }
            ,".//{*}doi_resolver": {
                'multiple':0,
                'attrib_column': {'text':'doi_resolver' }
            }
            ,".//{*}evidence": {
                'multiple':0,
                'attrib_column': {'text':'evidence' }
            }

            ,".//{*}free_fulltext_url":{
                'multiple':0,
                'attrib_column':{'text':'free_fulltext_url'}
            }
            ,".//{*}is_boai_license":{
                'multiple':0,
                'attrib_column':{'text':'is_free_boai_license'}
            }
            ,".//{*}is_subscription_journal":{
                'multiple':0,
                'attrib_column':{'text':'is_subscription_journal'}
            }
            ,".//{*}license":{
                'multiple':0,
                'attrib_column':{'text':'license'},
            }
            ,".//{*}oa_color":{
                'multiple':0,
                'attrib_column':{'text':'oa_color'},
            }
            # NOTE: one row has <open_version/> - ask api team what it is, what types of values can
            # it have?
            ,".//{*}url":{
                'multiple':0,
                'attrib_column':{'text':'doi_url'},
            }
        } # end child_xpaths
    } # end d_node_params

    return od_rel_datacolumns, d_node_params

#end def sql_mining_params_oadoi


###### START SCOPUS INPUT PARAMETERS ########
# 20161205 - Next, revert to using scopus xml files, but first alter satxml to add uf-harvest tag to those

def sql_mining_params_scopus():

    od_rel_datacolumns = OrderedDict([
        ('scopus', OrderedDict([
            ('scopus_id',''),
            ('eid',''),
            ('doi',''),
            ('pii',''),
            ('title',''),
            ('creator',''),
            ('publication_name',''),
            ('issn',''),
            ('eissn',''),
            ('cover_year',''),
            ('cover_date',''),
            ('citedby_count',''),
            ('agg_type',''),
            ('subtype',''),
            ('subtype_description',''),
            ('source_id',''),
            ('file_name',''),
            ('uf_harvest',''),
        ])),

        ('scopus_aff', OrderedDict([
            ('name',''),
            ('city',''),
            ('country',''),
        ])),
    ])
#----------------------------------------------
    d_node_params = {
        #
        # The db_name of this root node is given in a runtime parameter, so db_name is
        # not given for this node.
        #
        'multiple':0,
        'child_xpaths' : {
            ".//dc:identifier": {
                'multiple':0,
                'attrib_column': { 'text':'identifier' },
                'column_function': {'scopus_id': make_scopus_id}
            }
            ,".//{*}eid": {
                'multiple':0,
                'attrib_column': { 'text':'eid' },
            }
            ,".//dc:title": {
                'multiple':0,
                'attrib_column': {'text':'title' }
            }
            ,".//dc:creator": {
                'multiple':0,
                'attrib_column': {'text':'creator' }
            }

            ,".//prism:publicationName":{
                'multiple':0,
                'attrib_column':{'text':'publication_name'}
            }
            ,".//prism:issn":{
                'multiple':0,
                'attrib_column':{'text':'issn'}
            }
            ,".//prism:eIssn":{
                'multiple':0,
                'attrib_column':{'text':'eissn'}
            }
            ,".//prism:coverDate":{
                'multiple':0,
                'attrib_column':{'text':'cover_date', 'cover_year':'cover_year'},
                'column_function': {'cover_year': cover_year} #re-use Elsevier's method here
            }
            ,".//prism:doi":{
                'multiple':0,
                'attrib_column':{'text':'doi'},
            }
            ,".//{*}citedby-count":{
                'multiple':0,
                'attrib_column':{'text':'citedby_count'}
            }
            ,".//{*}pii":{
                'multiple':0,
                'attrib_column':{'text':'pii'},
            }

            ,".//prism:aggregationType":{
                'multiple':0,
                'attrib_column':{'text':'agg_type'}
            }
            ,".//{*}subtype":{
                'multiple':0,
                'attrib_column':{'text':'subtype'},
            }
            ,".//{*}subtypeDescription":{
                'multiple':0,
                'attrib_column':{'text':'subtype_description'},
            }
            ,".//{*}source-id":{
                'multiple':0,
                'attrib_column':{'text':'source_id'},
            }
            ,".//{*}affiliation":{
                'db_name':'scopus_aff',
                'multiple':1,
                'child_xpaths' : {
                    ".//{*}affilname":{
                        'multiple':0,
                        'attrib_column':{'text':'name'}
                    },
                    ".//{*}affiliation-city": {
                        'multiple':0,
                        'attrib_column':{'text':'city'}
                    },
                    ".//{*}affiliation-country": {
                        'multiple':0,
                        'attrib_column':{'text':'country'}
                    },
                },
            }
            ,".//{*}uf-harvest":{
                'multiple':0,
                'attrib_column':{'text':'uf_harvest'},
            }
        } # end child_xpaths
    } # end d_node_params

    return od_rel_datacolumns, d_node_params
#end def sql_mining_params_scopus

def make_scopus_id(d_row):
    identifier = d_row['identifier'] if 'identifier' in d_row else ''
    scopus_id = ''
    if len(identifier) >= 10:
        scopus_id = identifier[10:]
    return scopus_id

# CRATXML params

def get_date(part_names=None, d_row=None):
    if  part_names is None or d_row is None:
        raise Exception("get_date: Missng part_names. Bad args")
    sep = ''
    result_date = ''
    fills = [4,2,2]
    for i,part_name in enumerate(part_names):
        if part_name in d_row:
            result_date += sep + d_row[part_name].zfill(fills[i])
        else:
            break
        sep = '-'
    return result_date

def date_by_keys_year_month_day(d_row, d_params):
    part_names = []
    for col_key in ['year','month','day']:
        part_names.append(d_params[col_key])
    print("dbkymd: sending part_names='{}'".format(repr(part_names)))
    return get_date(part_names=part_names,d_row=d_row)

def make_issued_date(d_row):
    return get_date(part_names=['issued_year','issued_month','issued_day'],d_row=d_row)

def make_date(d_row, colnames=['year','month','day']):
    return get_date(part_names=colnames, d_row=d_row)

def make_crossref_author_name(d_row):
    family = ''
    given = ''
    if 'family' in d_row:
        family = d_row['family']
    if 'given' in d_row:
        given = d_row['given']
    #print("Got given={} family={}".format(given,family))

    if family and given:
        name = family + ', ' + given
    else:
        name = family + given

    return name

def funder_id_by_funder_doi(d_row):
    funder_id = ''
    funder_doi = d_row.get('funder_doi', '/')
    parts = funder_doi.split('/')
    if len(parts) > 1:
        funder_id = parts[len(parts)-1]
    return funder_id

def sql_mining_params_crossref():

    od_rel_datacolumns = OrderedDict([
        ('cross_doi', OrderedDict([
            ('doi',''),
            ('issn',''),
            ('url',''),
            ('archive',''),
            ('container_title',''),
            ('restriction',''),
            ('created_date_time',''),
            ('deposited_date_time',''),
            ('indexed_date_time',''),
            ('issue',''),
            ('issued_date',''),
            ('member',''),
            ('original_title',''),
            ('page_range',''),
            ('prefix',''),
            ('online_date',''),
            ('print_date',''),
            ('publisher',''),
            ('reference_count',''),
            ('score',''),
            ('short_container_title',''),
            ('short_title',''),
            ('source',''),
            ('subtitle',''),
            ('title',''),
            ('type',''),
            ('volume',''),
        ])),
        ('cross_author', OrderedDict([
            ('name',''),
            ('family',''),
            ('given',''),
            ('affiliation_name',''),
            ('affiliation_uf',''),
            ('orcid',''),
        ])),
        ('cross_link', OrderedDict([
            ('url',''),
            ('content_type',''),
            ('content_version',''),
            ('intended_application',''),
        ])),
        ('cross_license', OrderedDict([
            ('url',''),
            ('content_version',''),
            ('delay_in_days',''),
            ('start_date',''),
        ])),
        ('cross_subject', OrderedDict([
            ('term',''),
        ])),
        ('cross_funder', OrderedDict([
            ('funder_doi',''),
            ('funder_id',''),
            ('doi_asserted_by',''),
            ('name',''),
        ])),
        ('cross_award', OrderedDict([
            ('code_id',''),
        ])),
    ])

#-------------crossref api---------------------------------

    d_node_params1 = {
        #
        # The db_name of this root node is given in a runtime parameter, so db_name is
        # not given for this node.
        #
        'multiple':0,
        'child_xpaths' : {
            "./license" : { # One crossref doi record may have multiple licenses
                'db_name': 'cross_license', 'multiple': 1,
                'child_xpaths': {
                    ".//{*}URL" : {
                        'attrib_column': {'text':'url'},
                    },
                    ".//{*}content-version" : {
                        'attrib_column': {'text':'content_version'},
                    },
                    ".//{*}delay-in-days" : {
                        'attrib_column': {'text':'delay_in_days'},
                    },

                    ".//{*}start/{*}date-parts/item[@id='00000001']" : {
                        'child_xpaths' : {
                            "./item[@id='00000001']":{
                                'attrib_column' : { 'text':'year'},
                            },
                            "./item[@id='00000002']":{
                                'attrib_column' : { 'text':'month'},
                            },
                            "./item[@id='00000003']":{
                                'attrib_column' : { 'text':'day'},
                            },
                        },
                        'column_function': {'start_date': make_date},
                    },
                },
            },

            "./subject" : {
                'db_name': 'cross_subject', 'multiple': 1,
                'child_xpaths': {
                    "./*" : {
                        'attrib_column': {'text':'term'},
                    },
                },
            },

            "./author/item" : {
                'db_name': 'cross_author', 'multiple': 1,
                'child_xpaths': {
                    ".//affiliation//name" : {
                        'attrib_column': {'text':'affiliation_name'},
                    },
                    ".//family" : {
                        'attrib_column': {'text':'family'},
                    },
                    ".//given" : {
                        'attrib_column': {'text':'given'},
                    },
                    ".//orcid" : {
                        'attrib_column': {'text':'orcid'},
                    },
                },
                'column_function': {
                    'name': make_crossref_author_name,
                    'affiliation_uf': (uf_affiliation_by_colname,{'colname':'affiliation_name'}),
                    },
            },
            "./link" : {
                'db_name': 'cross_link', 'multiple': 1,
                'child_xpaths': {
                    ".//URL" : {
                        'attrib_column': {'text':'url'},
                    },
                    ".//content_type" : {
                        'attrib_column': {'text':'content_type'},
                    },
                    ".//content-version" : {
                        'attrib_column': {'text':'content_version'},
                    },
                    ".//intended-application" : {
                        'attrib_column': {'text':'intended_application'},
                    },
                },
            },
            "./funder/item" : {
                'db_name': 'cross_funder', 'multiple': 1,
                'child_xpaths': {
                    "./DOI" : {
                        'attrib_column': {'text':'funder_doi'},
                        'column_function': {'funder_id': funder_id_by_funder_doi},
                    },
                    "./doi-asserted-by" : {
                        'attrib_column': {'text':'doi_asserted_by'},
                    },
                    "./name" : {
                        'attrib_column': {'text':'name'},
                    },
                    "./award" : {
                        'db_name': 'cross_award', 'multiple': 1,
                        'child_xpaths': {
                            "./*" : {
                                'attrib_column': {'text': 'code_id'},
                            },
                        },
                    },
                },
            },

            "./DOI": {
                'multiple':0,
                'attrib_column': { 'text':'doi' },
            },
            "./ISSN": {
                'multiple':0,
                'attrib_column': { 'text':'issn' },
            },
            "./URL": {
                'multiple':0,
                'attrib_column': { 'text':'url' },
            },
            "./archive/item[@id='00000001']": {
                'multiple':0,
                'attrib_column': { 'text':'archive' },
            },
            "./container-title": {
                'multiple':0,
                'attrib_column': { 'text':'container_title' },
            },
            "./content-domain/crossmark-restriction": {
                'multiple':0,
                'attrib_column': { 'text':'restriction' },
            },
            # Note: some xml date-like tags do NOT have tag for date-time, but for these next
            # three that do, just use them and disregard parts for year, month, day.
            "./created/date-time": {
                'multiple':0,
                'attrib_column': { 'text':'created_date_time' },
            },

            "./deposited/date-time": {
                'multiple':0,
                'attrib_column': { 'text':'deposited_date_time' },
            },
            "./indexed/date-time": {
                'multiple':0,
                'attrib_column': { 'text':'indexed_date_time' },
            },
            "./issue": {
                'multiple':0,
                'attrib_column': { 'text':'issue' },
            },
            "./issued/date-parts/item[@id='00000001']": {
                'multiple':0,
                'child_xpaths' : {
                    './{*}item[@id="00000001"]':{ 'multiple':0,
                        'attrib_column':{'text':'issued_year'}},
                    './{*}item[@id="00000002"]':{ 'multiple':0,
                        'attrib_column':{'text':'issued_month'}},
                    './{*}item[@id="00000003"]':{ 'multiple':0,
                        'attrib_column':{'text':'issued_day'}},
                    },
                'column_function': {'issued_date': make_issued_date}
            },
            "./member": {
                'multiple':0,
                'attrib_column': { 'text':'member' },
            }
            ,"./original-title": {
                'multiple':0,
                'attrib_column': { 'text':'original_title' },
            }
            ,"./page": {
                'multiple':0,
                'attrib_column': { 'text':'page_range' },
            }
            ,"./prefix": {
                'multiple':0,
                'attrib_column': { 'text':'prefix' },
            }
            ,"./eid": {
                'multiple':0,
                'attrib_column': { 'text':'eid' },
            }
            ,"./published-online/date-parts/item[@id='00000001']": {
                'multiple':0,
                'child_xpaths' : {
                    './{*}item[@id="00000001"]':{ 'multiple':0,
                        'attrib_column':{'text':'year'}},
                    './{*}item[@id="00000002"]':{ 'multiple':0,
                        'attrib_column':{'text':'month'}},
                    './{*}item[@id="00000003"]':{ 'multiple':0,
                        'attrib_column':{'text':'day'}},
                },
                'column_function': {'online_date': make_date }
            }
            ,"./published-print/date-parts/item[@id='00000001']" : {
                'multiple':0,
                'child_xpaths' : {
                    './{*}item[@id="00000001"]':{ 'multiple':0,
                        'attrib_column':{'text':'year'}},
                    './{*}item[@id="00000002"]':{ 'multiple':0,
                        'attrib_column':{'text':'month'}},
                    './{*}item[@id="00000003"]':{ 'multiple':0,
                        'attrib_column':{'text':'day'}},
                },
                'column_function': {'print_date': make_date}
            }
            ,"./publisher": {
                'multiple':0,
                'attrib_column': { 'text':'publisher' },
            }
            ,"./reference-count": {
                'multiple':0,
                'attrib_column': { 'text':'reference_count' },
            }
            ,"./score": {
                'multiple':0,
                'attrib_column': { 'text':'score' },
            }
            ,"./short-container-title": {
                'multiple':0,
                'attrib_column': { 'text':'short_container_title' },
            }
            ,"./short-title": {
                'multiple':0,
                'attrib_column': { 'text':'short_title' },
            }
            ,"./eid": {
                'multiple':0,
                'attrib_column': { 'text':'eid' },
            }
            ,"./source": {
                'multiple':0,
                'attrib_column': { 'text':'source' },
            }
            ,"./subtitle/item[@id='00000001']": {
                'multiple':0,
                'attrib_column': { 'text':'subtitle' },
            }
            ,"./title": {
                'multiple':0,
                'attrib_column': { 'text':'title' },
            }
            ,"./type": {
                'multiple':0,
                'attrib_column': { 'text':'type' },
            }
            ,"./volume": {
                'multiple':0,
                'attrib_column': { 'text':'volume' },
            }
        } # end child_xpaths

    } # end d_node_params2

    # Interpose a new 'message' tag to support multiple crossref xml response formats:
    # see programs crafatxml and crawdxml for example, that produce these formats
    d_node_params2 = {
        'child_xpaths':{'.//message' : d_node_params1}
    }

    d_node_params = d_node_params1
    return od_rel_datacolumns, d_node_params
#end def sql_mining_params_crossref
'''
Method sql_mining_params_orcid

See https://github.com/ORCID/ORCID-Source/tree/master/orcid-model/src/main/resources/record_2.0
and its links for xsd information to assist in creating ORCID db schema and mining maps.
'''
def sql_mining_params_orcid():

    od_rel_datacolumns = OrderedDict([
        # The main parent table for orcid public records
        ('person', OrderedDict([ #
            ('orcid_id',''),    # ./common:orcid-identifier/common:path
            ('preferred_language',''), #./preferences/preferences:locale
            ('givens',''),       # ./person:person/perons:name/personal-details:given_names
            ('family',''),      # ./person:person/perons:name/personal-details:family-name
            ('family_givens',''),# method family_given(['given','family']
            ('person_modified_date',''), # ./person:person/common:last-modified-date
        ])),
        # orcid_xid: has any external ids (xid) for record holders, such as ResearcherID,
        # any others
        ('xid', OrderedDict([ # (./person:person)
            # ./external-identifier:external-identifiers/external-identifier:external-identifier
            ('type',''), # ./common:external-id-type
            ('value',''), # ./common:external-id-value
            ('url',''), # ./common:external-id-url
            ('relationship',''), #./common:external-id-relationship
            ('xid_modified_date',''), #./common:last_modified_date
        ])),
        # orcid_education: education events
        ('education', OrderedDict([ #./activities:activities-summary/activities:educations
                        # ... /activities:education-summary
            ('ed_modified_date',''), # ./common:last-modified-date
            ('department_name',''), # ./education:department-name
            ('role_title',''),      # ./education:role-title
            ('start_date',''), # method() ./common:start-date (year, month,day)
            ('end_date',''),        # method() ./common:start-date/year, month, day
            ('organization_name',''), # ./education:organization/common:name
            ('organization_city',''), # ./education:organization/common:address/common:city
            ('organization_region',''), # ./education:organization/common:address/common:region
            ('organization_country',''), # ./education:organization/common:address/common:country
            ('disambiguated_id',''),# ./education:organization/common:disambiguated-organization
                                 # /common:disambiguated-organization-identifier
            ('disambiguation_source',''),# ./education:organization/common:disambiguated-organization
                                 # /common:disambiguation-source
        ])),
        # orcid_employment: employment events
        ('employment', OrderedDict([ #./activities:activities-summary
                        # /activities:employments/employment:employment-summary
            ('created_date',''), # ./common:created-date
            ('emp_modified_date',''), # ./common:last-modified-date
            ('department_name',''),
            ('role_title',''),      # ./education:role-title
            ('start_date',''), # method() ./common:start-date (year, month,day)
            ('end_date',''),        # method() ./common:start-date/year, month, day
            ('organization_name',''), # ./employment:organization/common:namedef node_

            ('organization_city',''), # ./employment:organization/common:address/common:city
            ('organization_region',''), # ./employment:organization/common:address/common:region
            ('organization_country',''), # ./employment:organization/common:address/common:country
            ('disambiguated_id',''),# ./employment:organization/common:disambiguated-organization
                                 # /common:disambiguated-organization-identifier
            ('disambiguation_source',''),# ./education:organization/common:disambiguated-organization
                                 # /common:disambiguation-source
        ])),
        # orcid_work: works
        ('work', OrderedDict([ #./activities:activities-summary
                        # /activities:works/activities:group
            ('created_date',''), # ./work:work-summary/common:created-modified-date
            ('modified_date',''), # ./work:work-summary/common:last-modified-date
            ('title',''),      # ./work:work-summary/work:title/common:title
            ('type',''),      # ./work:work-summary/work:type
            ('publication_date',''),  # (method on 3 ymd values)
                        #./work:work-summary/common:publication-date
        ])),
        # orcid_work_xid: has any external ids (xid) for works, such as DOI, PCM,
        # any others
        ('work_xid', OrderedDict([ # (...activities:group)
            # ./common:external-ids/common:external-id
            ('type',''), # ./common:external-id-type
            ('value',''), # ./common:external-id-value
            ('url',''), # ./common:external-id-url
            ('relationship',''), #./common:external-id-relationship
         ])),
    ])

#-------------orcid api---------------------------------

    d_node_params1 = {
        #
        # The db_name of this root node is given in a runtime parameter, so
        # db_name is not given for this node.
        #
        'multiple':0,
        'child_xpaths' : {
            "./common:orcid-identifier/common:path" : {
                'attrib_column':{'text':'orcid_id'},
            },
            "./preferences:preferences/preferences:locale" : {
                'attrib_column':{'text':'preferred_language'},
            },
            "./person:person/person:name/personal-details:given-names" : {
                'attrib_column':{'text':'givens'},
            },
            "./person:person/person:name/personal-details:family-name" : {
                'attrib_column':{'text':'family'},
            },
            #"./person:person/person:name/personal-details:family-name"{
            #    'attrib_column':{'text':'family-given'},
            #},
            "./person:person/common:last-modified-date" : {
                'attrib_column':{'text':'person_modified_date'},
            },
            "./person:person/common:created-modified-date" : {
                'attrib_column':{'text':'person_created_date'},
            },

            ########    EXTERNAL IDENTIFIERS ##########

            "./person:person/external-identifier:external-identifiers/external-identifier:external-identifier" : {
                'db_name': 'xid', 'multiple': 1,
                'child_xpaths': {
                    './common:external-id-type': {
                        'attrib_column': {'text':'type'},
                    },
                    './common:external-id-value': {
                        'attrib_column': {'text':'value'},
                    },
                    './common:external-id-url': {
                        'attrib_column': {'text':'url'},
                    },
                    './common:external-id-relationship': {
                        'attrib_column': {'text':'relationship'},
                    },
                    './common:last-modified-date': {
                        'attrib_column': {'text':'modified_date'},
                    },
                },
            },

            ########    EMPLOYMENT ##########

            "./activities:activities-summary/activities:employments/employment:employment-summary" : {
                'db_name': 'employment',  'multiple': 1,
                'child_xpaths': {
                    './common:last-modified-date': {
                        'attrib_column': {'text':'modified_date'},
                    },
                    './employment:role-title': {
                        'attrib_column': {'text':'role_title'},
                    },
                    './employment:department-name': {
                        'attrib_column': {'text':'department_name'},
                    },

                    './common:start-date': {
                        'multiple':0,
                        'child_xpaths': {
                            './common:year': {
                                'attrib_column': {'text':'year'},
                            },
                            './common:month': {
                                'attrib_column': {'text':'month'},
                            },
                            './common:day': {
                                'attrib_column': {'text':'day'},
                            },
                        },
                        'column_function': {'start_date': make_date},
                    },

                    './common:end-date': {
                        'multiple':0,
                        'child_xpaths': {
                            './common:year': {
                                'attrib_column': {'text':'year'},
                            },
                            './common:month': {
                                'attrib_column': {'text':'month'},
                            },
                            './common:day': {
                                'attrib_column': {'text':'day'},
                            },
                        },
                        'column_function': {'end_date': make_date},
                    },

                    './employment:organization/common:name': {
                        'attrib_column': {'text':'organization_name'},
                    },
                    './employment:organization/common:address/common:city': {
                        'attrib_column': {'text':'organization_city'},
                    },
                    './employment:organization/common:address/common:region': {
                        'attrib_column': {'text':'organization_region'},
                    },
                    './employment:organization/common:address/common:country': {
                        'attrib_column': {'text':'organization_country'},
                    },
                    ('./employment:organization/common:disambiguated-organization'
                        +'/common:disambiguated-organization-identifier') : {
                        'attrib_column': {'text':'disambiguated_id'},
                    },
                    ('./employment:organization/common:disambiguated-organization'
                        +'/common:disambiguation-source') : {
                        'attrib_column': {'text':'disambiguation_source'},
                    },
                },
            },

            #############       EDUCATION     #################

            "./activities:activities-summary/activities:educations/education:education-summary" : {
                'db_name': 'education',  'multiple': 1,
                'child_xpaths': {
                    './common:last-modified-date': {
                        'attrib_column': {'text':'modified_date'},
                    },
                    './education:department-name': {
                        'attrib_column': {'text':'department_name'},
                    },
                    './education:role-title': {
                        'attrib_column': {'text':'role_title'},
                    },

                    './common:start-date': {
                        'multiple':0,
                        'child_xpaths': {
                            './common:year': {
                                'attrib_column': {'text':'year'},
                            },
                            './common:month': {
                                'attrib_column': {'text':'month'},
                            },
                            './common:day': {
                                'attrib_column': {'text':'day'},
                            },
                        },
                        'column_function': {'start_date': make_date},
                    },

                    './common:end-date': {
                        'multiple':0,
                        'child_xpaths': {
                            './common:year': {
                                'attrib_column': {'text':'year'},
                            },
                            './common:month': {
                                'attrib_column': {'text':'month'},
                            },
                            './common:day': {
                                'attrib_column': {'text':'day'},
                            },
                        },
                        'column_function': {'end_date': make_date},
                    },


                    './education:organization/common:name': {
                        'attrib_column': {'text':'organization_name'},
                    },
                    './education:organization/common:address/common:city': {
                        'attrib_column': {'text':'organization_city'},
                    },
                    './education:organization/common:address/common:region': {
                        'attrib_column': {'text':'organization_region'},
                    },
                    './education:organization/common:address/common:country': {
                        'attrib_column': {'text':'organization_country'},
                    },
                    ('./education:organization/common:disambiguated-organization'
                        +'/common:disambiguated-organization-identifier') : {
                        'attrib_column': {'text':'disambiguated_id'},
                    },
                    ('./education:organization/common:disambiguated-organization'
                        +'/common:disambiguation-source') : {
                        'attrib_column': {'text':'disambiguation_source'},
                    },
                },
            },

            ############  WORK #############

            "./activities:activities-summary/activities:works/activities:group/work:work-summary" : {
                'db_name': 'work',  'multiple': 1,
                'child_xpaths': {
                    './common:last-modified-date': {
                        'attrib_column': {'text':'modified_date'},
                    },
                    './work:title/common:title': {
                        'attrib_column': {'text':'title'},
                    },
                    './common:external-ids/common:external-id': {
                        'db_name': 'work_xid', 'multiple':1,
                        'child_xpaths': {
                            './common:external-id-type' : {
                                'attrib_column': {'text':'type'},
                            },
                            './common:external-id-value': {
                                'attrib_column': {'text':'value'},
                            },
                            './common:external-id-url' :{
                                'attrib_column': {'text':'url'},
                            },
                            './common:external-id-relationship' : {
                                'attrib_column': {'text':'relationship'},
                            },
                        },
                    },

                    './work:type': {
                        'attrib_column': {'text':'type'},
                    },
                    './work:title/common:title': {
                        'attrib_column': {'text':'title'},
                    },
                    './work:title/common:title': {
                        'attrib_column': {'text':'title'},
                    },
                    './work:title/common:title': {
                        'attrib_column': {'text':'title'},
                    },
                    './common:publication-date': {
                        'multiple':0,
                        'child_xpaths': {
                            './common:year': {
                                'attrib_column': {'text':'year'},
                            },
                            './common:month': {
                                'attrib_column': {'text':'month'},
                            },
                        },
                        'column_constant': {'day':''},
                        'column_function': {'publication_date': make_date},
                    },
                },
            },
        },

    } # end d_node_params1

    # Interpose a new 'message' tag to support multiple crossref xml response formats:
    # see programs crafatxml and crawdxml for example, that produce these formats
    d_node_params2 = {
        'child_xpaths':{'.//message' : d_node_params1}
    }

    d_node_params = d_node_params1
    return od_rel_datacolumns, d_node_params
#end def sql_mining_params_orcid

def sql_mining_params_citrus_bibs():
    '''
    od_rel_datacolumns notations:
    (0) key 'attribute_text' reserves a special 'attribute name' to mean text content of a node
         - may also introduce reserved keyword attribute_innerhtml to mean the whole xml content,
            eg from an lxml etree.tostring() call for the node
         - might later introduce keys for node text prefixes and tails per node, if need arises
    (1) first table, named mods, is the main table, xpath set by caller
    (2) other table names below show first comment is the expected xpath to be used in the mining map.
    (3)


    ====================== to add later... to mining map...

        ('genre', OrderedDict([ # [mods]./mods:genre
            ('authority',''), #@authority
            ('text_content',''), # @text_content
        #
        ('language', None), # [mods]./mods:language - pure wrapper object
        ('language_term', OrderedDict([ # [language]./mods:languageTerm
            ('type',''), # @type ('text' or 'code')
            ('authority',''), # @authority
            ('node_text',''), # @node_text, eg, English for type text, eng for type code
        #
        ('location', None), # [mods]./mods:location - pure wrapper object
        #
        ('physical_location', OrderedDict([ #[location]./mods:physicalLocation
            ('type',''), # @type, eg 'code' or ''
            ('node_text',''), #@node_text, eg UFSPEC or UF Special Collections
            ('url_access',''), #./mods:url@access
            ('url_text',''), #/.mods_url@node_text
        ])),
        ('role', None), # This relation is only the index set for the html tag so no columns

        ('role_term', OrderedDict([ #./mods:roleTerm
            ('type',''), # @type
            ('authority',''), # @authority
            ('text_content',''), #@text_content
        ])),
        #
        ('note', OrderedDict([ #./mods:note
            ('text_content',''), # @text_content
            ('name_part',''), # ./mods:namePart
        ])),
        #
        ('related_item', OrderedDict([ #./mods:relatedItem
            ('type',''), # ./@type
            ('physical_description_extent',''), # ./mods:physicalDescription/mods:extent
            ('part_detail_type') #./mods.part/mods:detail@type
            ('part_caption'), #./mods:part/mods:caption@text_content
            ('part_number'), #/mods:part/mods:number@text_content
        ])),
         -------------------------------------------------------------------------------------------------------------
    '''

    od_rel_datacolumns = OrderedDict([
        # The main parent table
        ('mets', OrderedDict([ # ./METS:mets
            ('bib_vid',''),     # .//mods:mods/mods:recordInfo/mods:recordIdentifier@source
            ('date_issued',''), #.//mods:mods/mods:originInfo/mods:dateIssued
            ('temporal_start',''),
            ('temporal_end',''),
            ('temporal_period',''),
            ('country',''),
            ('state',''),
            ('county',''),
            ('city',''),
            ('coordinates_lat_lng', ''),
            ('abstract',''),    # .//mods:mods/mods:abstract
            #('access_condition',''), #.//mods:mods/mods:accessCondition@node_text
            ('url',''), #.//mods:mods/mods:url@text_content
            ('url_access',''), #.//mods:mod/smods:url@access
            ('original_date_issued',''),
           #('hgeo',''), #.//mods:mods/mods:subject/mods:hierarchicalGeographic@node_innerhtml
        ])),

        #
        ('subject', OrderedDict([ #.//mods:mods/mods:subject
            ('id',''), # ./@ID
            ('authority',''), # @authority
            ('topic',''), # .//mods:mods/mods:topic@text_content
        ])),

        ('hgeo', OrderedDict([ # [subject].//mods:mods/mods:hierarchicalGeographic
            #Note: may change to use separate table hierarchicalGeographic so reverse will
            # keep state, county, city within a single hierarchicalGeographic tag
            ('state',''), # .//mods:mods/mods_hierarchicalGeographic/mods:state
            ('county',''), # .//mods:mods/mods:state
            ('city',''), # .//mods:mods/mods:city
            ('type',''), # .//mods:mods/mods:name@type
            ('name_part',''), # .//mods:mods/mods:namePart
        ])),
    ])

#-------------citrus ufdc mets xml files files---------------------------------

    d_node_params1 = {
        #
        # The db_name of this root node is given in a runtime parameter, so
        # db_name is not given for this node, though the name should be the first table name above.
        #
        'multiple':0,
        'child_xpaths' : {
            ".//mods:recordIdentifier" : {
                'attrib_column':{'attribute_text':'bib_vid'},
            },
            ".//mods:dateIssued" : {
                'attrib_column':{'attribute_text':'date_issued'},
            },
            ".//sobekcm:period" : {
                'attrib_column':{
                    'start':'temporal_start',
                    'end':'temporal_end',
                    'attribute_text':'temporal_period'
                },
            },

            ".//mods:mods/mods:subject/mods:hierarchicalGeographic/mods:country": {
                'attrib_column': {'attribute_text':'country'},
            },

            ".//mods:mods/mods:subject/mods:hierarchicalGeographic/mods:state": {
                'attrib_column': {'attribute_text':'state'},
            },

            ".//mods:hierarchicalGeographic/mods:county": {
                'attrib_column': {'attribute_text':'county'},
            },

             ".//mods:hierarchicalGeographic/mods:city": {
                'attrib_column': {'attribute_text':'city'},
            },

             ".//{*}Coordinates": { # gml:Coordinates, but gml not in mets prefix maps
                'attrib_column': {'attribute_text':'coordinates_lat_lng'},
            },

           ".//mods:mods/mods:abstract" : {
                'attrib_column':{'attribute_text':'abstract'},
            },
            #".//mods:mods/mods:accessCondition" : {
            #    'attrib_column':{'attribute_text':'access_condition'},
            #},
            ".//mods:mods/mods:url" : {
                'attrib_column':{'attribute_text':'url'},
            },
            ".//mods:mods/mods:url" : {
                'attrib_column':{'access':'url_access'},
            },

            # NOTE: due to xml2rdb constraint, must use different child_path string here than
            # for 'date_issued' above.
            # Just repeating the value for easy extract of duplicate column for a spreadsheet where
            # Angie is not supposed to change this original date value.
            ".//mods:mods//mods:dateIssued" : {
                'attrib_column':{'attribute_text':'original_date_issued'},
            },

            ########    Subjects ##########

            ".//mods:mods/mods:subject" : {
                'db_name': 'subject', 'multiple': 1,
                'child_xpaths': {
                    './*': {
                        'attrib_column': {'id':'id'},
                    },
                    './*': {
                        'attrib_column': {'authority':'authority'},
                    },
                    './mods:topic': {
                        'attrib_column': {'attribute_text':'topic'},
                    },
                    "./mods:hierarchicalGeographic" : {
                        'db_name': 'hgeo', 'multiple': 1,
                        'child_xpaths': {
                            './mods:state': {
                                'attrib_column': {'attribute_text':'state'},
                            },
                            './mods:county': {
                                'attrib_column': {'attribute_text':'county'},
                            },
                            './mods:city': {
                                'attrib_column': {'attribute_text':'city'},
                            },
                        },
                    },
                },
            },
        }, #end mods table child expaths

    } # end d_node_params1

    d_node_params = d_node_params1

    return od_rel_datacolumns, d_node_params
#end sql_mining_params_citrus_bibs()

#############################################
################################ END MISC USER PARAMETERS ###############################

'''
Method new_od_relation
'''
def new_od_relation(od_rel_datacolumns):
    od_relation = OrderedDict()
    print("Creating relation with datacolumns:")
    for i,key in enumerate(od_rel_datacolumns.keys()):
        od_rel_info = OrderedDict()
        od_relation[key] = od_rel_info
        print("Table {}, name={}".format(i+1,key))
    return od_relation

'''
Method get_writable_db_file:

This method is designed to be called while the mining map nodes are being visited from node_visit_output(),
so that the od_parent_index dictionary is properly populated with the parent relaton name values that
assign the composite primary key column names of the given db_name in the mining map's hierarchy.
This information is given in the argument od_parent_index.

The actual index values are not important here, but the parent relation names are important
so that the primary key column names for them can be assigned to the given db_name relation.
This need only be done once, and coincidentally, the writable file handle for the relation need only
be created once, and so it is also done within this routine.

Given a db_name of interest and od_relation of all relation names,
we get od_rel_info as the ordered dictionary value of od_relation[db_name].

We get or create od_column value for the od_rel_info key 'attrib_column' .
od_column is the dictionary of xml attribute-name keys with their sql column-name values in the
parent dictionary.


Note: SQL Server 2008 cannot handle utf-8 encoding, but can use it for many other RDBs.

'''
def get_writable_db_file(od_relation=None, od_rel_datacolumns=None,
    db_name=None, output_folder=None, od_parent_index=None,
    output_encoding='latin-1', errors="xmlcharrefreplace"):

    me='get_writable_db_file'
    if (od_relation is None or db_name is None
        or output_folder is None or od_parent_index is None
        or od_rel_datacolumns is None):
        raise Exception('{}:bad args'.format(me))

    # NOTE: method new_od_relation must be called before this one to create
    # all od_relations in same order as od_rel_datacolumns.
    # ... ?? and is that all... maybe to set od_relation[db_name] = OrderedDict()?

    od_rel_info = od_relation.get(db_name, None)
    if od_rel_info is None:
        raise Exception("{}:od_relation key (db_name) '{}' is undefined. ".format(me,db_name))

    od_column = od_rel_info.get('attrib_column', None)
    if od_column is None:
        # When here, this is the first encounter of a node with this db_name in an input xml_file,
        # and we assume the xml files are of consistent structure, with same xml tag lineage,
        # with regard to the mining map'a paths of interest.
        # So we can use the first one found to set up the hierarchy/lineage of the
        # primary key's composite columns.
        #
        # We will create places to store info for this relation's attrib columns and
        # other 'mining' info, including sql olumn names of data we will output for this relation
        od_column = OrderedDict()
        od_rel_info['attrib_column'] = od_column

        # Create and open a writable output file for this relation, mode='w', encoding='utf-8'
        # If SQL server 2008 bulk insert chokes on utf-8, encode this to ascii

        filename = '{}/{}.txt'.format(output_folder,db_name)
        print('{}: opening output {}'.format(me, filename))
        od_rel_info['db_file'] = open(filename, mode='w', encoding=output_encoding, errors=errors)

        #This RDB Table's Primary key value will be output as a simple string of csv of column names
        od_pkey = OrderedDict()

        #Set up the primary key columns for this relation
        pkey_columns = ""
        sep = ''

        # First, for every parent of this relation, register a column name to
        # hold its index value and concat each col name to list of primary key col names.
        if len(od_parent_index) > 0:
            for column_name in od_parent_index.keys():
                od_column[column_name] = 'integer'
                pkey_columns += "{}{}".format(sep,column_name)
                sep = ','

        # Column data type for this db_name node index is also an integer count.
        od_column[db_name] = 'integer'
        # ... and also a primary key column called by the name of the db_name itself
        pkey_columns +="{}{}".format(sep, db_name)
        od_rel_info['pkey'] = pkey_columns

        # For datacolumns, set the SQL datatypes. Set all to nvarchar(3550), which seems OK for now.
        # Could also encode data types into user inputs for convenience by adding fields to the input
        # structure od_rel_datacolumns but may not be needed.
        # This is because fter xml2rdb is run, the end user can use standard SQL to change
        # datatypes for columns within a database.

        od_datacolumn_default = od_rel_datacolumns[db_name]

        # Make character column names for this node's data columns
        if len(od_datacolumn_default) > 0:
            for column_name in od_datacolumn_default.keys():
                if column_name is None:
                    raise Exception("Relation '{}' has a null row key.".format(db_name))
                print("{}:Relation={},adding column_name={}".format(me,db_name,column_name))
                od_column[column_name] = 'nvarchar(3550)'
    # end storing misc mining info for a newly encounterd relation in the input
    else:
        #print("{}:Dict for attribute_column already found for db_name={}".format(me,db_name))
        pass
    # For the given db_name, return the writable file to the caller
    return od_rel_info['db_file']

#end def get_writable_db_file
'''
Method node_visit_output

Given node, the current node, and d_node_params, the 'mining map' starting with the
given node's entry in the mining map hierarchy, garner the input fields for this node.

If the node has a db_name (and/or a multiple=1 value, meaning multiple of this node type is
allowed to exist under the same parent), the node represents a row in an sql relation,
so after visiting its children nodes (using each given child_xpath),
and getting their values via return value d_row, then we output a row for this node.
Else, this node is not a db_name node, rather only one node of this type is allowd under its parent
node in the xml input document, so this node is mined to garner input values into a
dictionary, d_row, to return to the parent node for its use.
'''

def node_visit_output(node=None, node_index=None, d_namespaces=None,
    d_node_params=None, od_rel_datacolumns=None, od_parent_index=None,
    od_relation=None, output_folder=None,d_xml_params=None):

    me = 'node_visit_output()'
    verbose = 0
    msg = ("{}:START: node.tag={}, node_index={}".format(me, node.tag, node_index))
    log_messages = []

    if (node is None
        or node_index is None or d_namespaces is None or od_parent_index is None
        or od_relation is None or output_folder is None
        or od_rel_datacolumns is None or d_xml_params is None):
        msg = (
          '''{}:BAD arg(s) within:od_parent_index={},\nnode={},
          \noutput_folder={}, \nd_namespaces={}, \nod_relation={}'''
          .format(me,repr(od_parent_index),repr(node)
          ,repr(output_folder), repr(d_namespaces), repr(od_relation))
        )
        msg += "\n" + ("node_index={}".format(repr(node_index)))
        raise RuntimeError(msg)
    attribute_text = d_xml_params.get('attribute_text','text')
    attribute_innerhtml = d_xml_params.get('attribute_innerhtml','attribute_innerhtml')
    #if 'multiple' not in d_node_params:
    #    raise RuntimeError("{}: multiple keyword missing for node.tag={}"
    #            .format(me,node.tag))
    # pass along the parent index - we will append our index below only if multiple is 1
    od_child_parent_index = od_parent_index

    multiple = d_node_params.get('multiple', 0)
    if multiple is None:
        msg = ("{}:Node tag={}, index={},node multiple is None."
               .format(me,node.tag,node_index))
        raise Exception()
    if verbose > 0 and multiple == 0 and node_index > 1:
        # Solution: in d_node_params, change multiple =0, provide a db_name, and also update
        # od_rel_datacolumns to include this db_name as a table if it does not already appear there.
        print("WARN:{}: node.tag={} has multiple == 0 but node_index = {}"
                    .format(me,node.tag,node_index))
    if multiple != 0 and multiple != 1:
        raise Exception("{}: Multiple value='{}' is bad for db_name{}".format(me,multiple,db_name))

    # We will put the data values of interest for this node into d_row.
    # d_row collects a dict of named data values for this node and is returned to caller if this node
    # has multiple indicator == 0.
    d_row = {}
    # d_attr_column: key is an attribute name and value is a relational column
    # name in which to outut the attribute value.
    # Because some attrib names have hyphens, this provides a way
    # that we can change the attribute name to a db column name, e.g, to
    # replace hyphens (that commonly appear in attribute names but are disallowed in many rdbs in
    # column names) with underbars (which are commonly alowed in rdbs in column names).
    d_attr_column = d_node_params.get('attrib_column', None)
    if d_attr_column is not None:
        # We have some node attributes destined for relational columns,
        # so set them up in d_row key-value pairs.
        if not isinstance(d_attr_column, dict):
            # detect some sorts of errors/typos in the d_node_params parsing configuration
            import types
            raise Exception("d_attrib_column {}, type={} is not dict. node.tag={}, node_index={}"
                    .format(repr(d_attr_column),repr(type(d_attr_column)),node.tag, node_index))

        node_text = etree.tostring(node, encoding='unicode', method='text')
        # Must discard tabs, used as bulk load delimiter, else bulk insert msgs
        # appear 4832 and 7399 and inserts fail.
        node_text = node_text.replace('\t',' ').replace('\n',' ').strip()
        #node_text = "" if stringify is None else stringify.strip()

        for attr_name, column_name in d_attr_column.items():
            # For every key in attr_column, if it is reserved name in attribute_text,
            # use the node's text value, else seek the key in node.attrib
            # and use its value.
            column_name = attr_name if column_name is None else column_name
            column_value = ''
            if attr_name == attribute_text:
                # Special reserved name in attribute_text: it is not really an attribute name,
                # but this indicates that we shall use the node's content/text for
                # this attribute
                column_value = node_text
            elif attr_name == attribute_innerhtml:
                # Special reserved name in attribute_text: it is not really an attribute name,
                # but this indicates that we shall use the node's innerhtml value for
                # this attribute
                column_value = etree.tostring(node, encoding='unicode')
            else:
                if attr_name in node.attrib:
                    column_value = node.attrib[attr_name]
            #print("setting d_row for column_name={} to value={}".format(column_name,column_value))
            d_row[column_name] = column_value
    # When multiple is 1 we always stack a node index
    if multiple == 1:
        # Where multiple is 1, db_name is name of an output relation.
        db_name = d_node_params.get('db_name', None)
        if db_name is None:
            raise RuntimeError(
              "{}: db_name={},Mandatory db_name is not a key in d_node_params={}"
              .format(me, db_name, repr(d_node_params)))

        # This node has an output, so it must append its own index to copy of
        # od_child_parent_index and pass it to calls for child visits.
        od_child_parent_index = OrderedDict(od_parent_index)

        # Note: this next dup db_name check could be done once in get_d_node_params(), but
        # easy to put here for now
        if db_name in od_child_parent_index:
            raise Exception("{}:db_name={} is a duplicate in this path.".format(me,db_name))

        od_child_parent_index[db_name] = node_index

    ################# SECTION - RECURSE TO CHILD XPATH NODES ###############

    od_child_row = None
    d_child_xpaths = d_node_params.get('child_xpaths',None)

    if d_child_xpaths is not None:
        for xpath, d_child_node_params in d_child_xpaths.items():
            #print("{} seeking xpath={} with node_params={}".format(me,repr(xpath),repr(d_child_node_params)))
            children = node.findall(xpath, d_namespaces )
            #print("{}:for xpath={} found {} children".format(me,xpath,len(children)))
            # TODO:Future: may add a new argument for caller-object that child may use to accumulate, figure,
            # summary statistic
            d_child_row = None
            for i,child in enumerate(children):
                d_child_row = node_visit_output(node=child
                    , node_index=(i+1)
                    , d_namespaces=d_namespaces
                    , d_node_params=d_child_node_params
                    , od_rel_datacolumns=od_rel_datacolumns
                    , od_relation=od_relation
                    , od_parent_index=od_child_parent_index
                    , output_folder=output_folder
                    , d_xml_params = d_xml_params)
                # Finished visiting a child
            # Finished one or more children with same xpath
            if d_child_row is not None and len(d_child_row) > 0:
                for column_name, value in d_child_row.items():
                    # Allowing this may be a feature to facilitate re-use of column functions
                    # TEST RVP 201611215
                    #if column_name in d_row:
                    #    raise Exception(
                    #        'node.tag={} duplicate column name {} is also in a child xpath={}.'
                    #        .format(node.tag,column_name,xpath))
                    d_row[column_name] = value
            #Finished visiting children for this xpath.
        #Finished visting all child xpaths for this node
    #End loop through all child xpaths to visit.

    ######## Set any local column constants ##############
    if 'column_constant' in d_node_params:
        for column, constant in d_node_params['column_constant'].items():
            d_row[column] = constant
    import types
    d_column_functions = d_node_params.get('column_function',None)
    if d_column_functions is not None:
        # Add columns to d_row for derived values:
        # Change later to do these after children return and provide
        # as args all child data dict and the lxml node itself so such a function
        # has more to work with.
        for column_name, function in d_column_functions.items():
            if type(function) is types.FunctionType:
                # This function knows the d_row key(s) to use
                d_row[column_name] = function(d_row)
            else: # Assume types.TupleType of: (function, dict of params)
                # This function will find its arguments in the given dict of function params
                d_row[column_name] = function[0](d_row, function[1])

    ####################### OUTPUT for MULTIPLE (== 1) NODES
    if multiple == 1:
        # For multiple == 1 nodes, we write an output line to the database
        # relation/table named by this node's 'db_name' value.
        db_file = get_writable_db_file(od_relation=od_relation,
            od_rel_datacolumns=od_rel_datacolumns,
            db_name=db_name, output_folder=output_folder, od_parent_index=od_parent_index)

        sep = ''
        db_line = ''
        #First, ouput parent indexes
        for parent_index in od_parent_index.values():
            db_line += ("{}{}".format(sep,parent_index))
            sep = '\t'
        # Now output this node's index
        # It identifies a row for this node.tag in this relation among all rows outputted.
        # It is assigned by the caller via an argument, as the caller
        # tracks this node's count/index value as it scans the input xml document.

        db_line += ("{}{}".format(sep,node_index))

        # ##################  NOW, OUTPUT THE DATA COLUMNS ##################
        # For each field in d_row, put its value into od_column_values
        #
        od_column_default = od_rel_datacolumns[db_name]

        for i,(key,value) in enumerate(od_column_default.items()):
            # Note: this 'picks' the needed column values from d_row, rather than scan
            # the d_row and try to test that each is an od_column_default key, by design.
            # This design allows the child to set up local d_row attribute_column values with names
            # other than those in od_column_default so that the column_function feature may use
            # those 'temporary values' to derive its output to put into named d_row entries.
            value = ''
            if key in d_row:
                value = d_row[key]
            db_line += ("\t{}".format(str(value).replace('\t',' ')))

        #Output a row in the db file
        print('{}'.format(db_line), file=db_file)

        ############################################################
        # Now that all output is done for multiple == 1, set d_row = None, otherwise it's
        # presence would upset the caller.
        d_row = None
    # end if multiple == 1

    msg = ("{}:FINISHED node.tag={}, node_index={}, returning d_row={}"
           .format(me, node.tag, node_index,repr(d_row)))
    #print(msg)
    return d_row
# def end node_visit_output

'''
Method xml_doc_rdb: from given xml doc(eg, from an Elsevier full text retrieval apifile),
convert the xml doc for output to relational data and output to relational tab-separated-value (tsv) files.
Excel and other apps allow the '.txt' filename extension for tab-separated-value files.
'''
def xml_doc_rdb(
    od_relation=None
    ,output_folder=None
    ,input_file_name=None
    ,file_count=None
    ,doc_rel_name=None
    ,doc_root=None # doc element is meta element to use as root xml node per article/doc
    ,doc_root_xpath=None
    ,d_node_params=None
    ,od_rel_datacolumns=None
    ,d_root_node_params=None
    ,d_xml_params=None
    # first draft: slice_name a slice name apply to the root node.
    #
    # Later:
    #   We also will add a naturally useful row offset integer paramemter:
    #   If user intends to append extant data tables with the rows in the output data,
    #   USER IS RESPONSIBLE to set row offset to beyond the highest
    #   offset in the root table to which to append these rows.
    #   With a proper offset row integer, all outputted tables data files
    #   will be also suitable to be appended to their respective DB tables. The user is responsible for
    #   creating the SQL to do this, at this point.
    ,load_name=None # A name to apply to this load group-segment of outputted  rows.
    ,verbosity=0):

    me = 'xml_doc_rdb()'
    log_messages = []
    err = 0
    if (
        input_file_name is None or output_folder is None or
        d_node_params is None or d_xml_params is None):
        err=1
    if ( od_rel_datacolumns is None):
        err = 'od_rel_datacolumns is None'
    if (file_count is None ):
        err = 'file_count is None'
    if (doc_rel_name is None):
        err='doc_rel_name is None'
    if (d_xml_params is None):
        err='doc_rel_name is None'
    if (doc_root is None
        or doc_root_xpath is None or od_relation is None
       ):
        err = 3

    if err != 0:
        msg = ("{}:Got input file_name='{}', output_folder='{}', od_relation='{}',"
           "file_count='{}', doc_root='{}',doc_root_xpath='{}', len d_node_params='{}'"
           " len od_rel_datacolumns={}. Bad arguments."
          .format(me, input_file_name, output_folder, repr(od_relation)
                  ,file_count,doc_root, doc_root_xpath,len(d_node_params)
                 ,len(od_rel_datacolumns)))
        #log_messages.append(msg)
        print(msg)
        import sys
        sys.stdout.flush()
        raise Exception("{}:bad arguments. err = {}".format(me,err))

    msg = "{}:Using input_file_name='{}'".format(me, input_file_name)
    #log_messages.append(msg)
    #print(msg)

    # (1) Read an input xml file to variable input_xml_str
    # correcting newlines and doubling up on curlies so format() works on them later.
    with open (str(input_file_name), "r") as input_file:
        input_xml_str = input_file.read().replace('\n','')

    # (2) and convert input_xml_str to a tree input_doc using etree.fromstring,

    if input_xml_str[0:9] == '<failure>':
        # IMPORTANT: This 'if clause' is a custom check for a 'bad' xml file common to a
        # particular set of test UF xml files.
        # This skipping is not generic feature of xml2rdb and may be removed.
        # print("This xml file is a <failure>. Skipping it.")
        log_messages.append("<failure> input_file {}.Skip.".format(input_file_name))
        return log_messages, None, None

    try:
        tree_input_doc = etree.parse(input_file_name)
    except Exception as e:
        msg = (
            "Skipping exception='{}' in etree.fromstring failure for input_file_name={}"
            .format(repr(e), input_file_name))
        #print(msg)
        log_messages.append(msg)
        return log_messages, None, None

    # GET xml ROOT for this file
    try:
        input_node_root = tree_input_doc.getroot()
    except Exception as e:
        msg = ("Exception='{}' doing getroot() on tree_input_doc={}. Return."
                .format(repr(e),repr(tree_input_doc)))
        #print(msg)
        log_messages.append(msg)
        return log_messages, None, None

    #Append this xml files root node to doc_root so it can be processed, wallked.
    doc_root.append(input_node_root)

    # Do not put the default namespace (as it has no tag prefix) into the d_namespaces dict.
    d_nsmap = dict(input_node_root.nsmap)
    d_namespaces = {key:value for key,value in d_nsmap.items() if key is not None}

    if load_name is not None:
        print("Warning: User must add column names 'load' and 'file_name' to the root table"
              " to enable their values to be output in the output data")
    else:
        load_name=""

    # document root params
    d_root_params = {
        'db_name': doc_rel_name, 'multiple':1,
        'attrib_column': {
            'file_name':'file_name',
            'load': load_name,
        },
        'child_xpaths':{doc_root_xpath:d_node_params}
    }

    # OrderedDict with key of parent tag name and value is parent's index among its siblings.
    od_parent_index = OrderedDict()
    node_index = file_count

    # In this scheme, the root node always has multiple = 1 - that is, it may have multiple
    # occurences, specifically, over the set of input files.
    # Also, this program requires that it be included in the relational output files.
    multiple = 1
    d_row = node_visit_output(
         od_relation=od_relation
        ,d_namespaces=d_namespaces
        ,d_node_params=d_root_params
        ,od_rel_datacolumns=od_rel_datacolumns
        ,output_folder=output_folder
        ,od_parent_index=od_parent_index
        ,node_index=node_index
        ,node=doc_root
        ,d_xml_params=d_xml_params
        )
    return log_messages
# end def xml_doc_rdb():

'''
Method xml_paths_rdb():
Loop through all the input xml files in a slice of the input_path_list,
and call xml_doc_rdb to create relational database table output rows
for each input xml doc.

'''
def xml_paths_rdb(
      input_path_list=None
    , doc_root_xpath=None
    , rel_prefix=None
    , doc_rel_name=None
    , d_node_params=None
    , od_rel_datacolumns=None
    , output_folder=None
    , use_db=None
    , file_count_first=0
    , file_count_span=1
    , verbosity=1
    , d_xml_params=None
    ):
    me = "xml_paths_rdb"
    bad = 0
    if not (output_folder):
        bad = 1
    elif not (rel_prefix)and rel_prefix != '':
        bad = 2
    elif not (input_path_list):
        bad = 3
    elif not(doc_root_xpath):
        bad = 4
    elif not( doc_rel_name):
        bad=5
    elif not (d_node_params):
        bad = 6
    elif not (output_folder):
        bad = 7
    elif not (od_rel_datacolumns):
        bad = 8
    elif not (use_db):
        bad = 9
    elif d_xml_params is None:
        bad = 10

    if bad > 0:
        raise Exception("Bad args. code={}".format(bad))

    log_messages = []
    msg = ("{}:START with file_count_first={} among total file count={}"
           .format(me, file_count_first, len(input_path_list)))
    print(msg)

    max_input_files = 0
    count_input_file_failures = 0

    # Dictionary with output relation name key and value is dict with row keys,
    # values may be types later
    od_relation = new_od_relation(od_rel_datacolumns)
    row_index = 0

    # Caller has already sliced input_path_list with first 'real file count'
    # value being file_count_first. So in the for loop, add i to file_count_first to
    # get the file_count among the input_path_list.
    for i, path in enumerate(input_path_list):
        if (max_input_files > 0) and ( i >= max_input_files):
            # This clause used for testing only...
            log_messages.append(
                "Max number of {} files processed. Breaking.".format(i))
            break

        file_count = file_count_first + i + 1

        # Full absolute path of input file name is:
        input_file_name = "{}/{}".format(path.parents[0], path.name)
        batch_size = 250
        if batch_size > 0  and (i % batch_size == 0):
            progress_report = 1
        else:
            progress_report = 0

        if (progress_report):
            utc_now = datetime.datetime.utcnow()
            utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")
            msg = ("{}: Processed through input file count = {} so far."
                   .format(utc_secs_z, file_count))
            print(msg)
            #log_messages.append(msg)
            # Flush all the output files in od_relation
            for relation, d_info in od_relation.items():
                file = d_info.get('db_file', None)
                if file is not None:
                    file.flush()

        # Try to read the article's input full-text xml file and accrue its statistics
        with open(str(input_file_name), "r") as input_file:
            try:
                input_xml_str = input_file.read().replace('\n','')
                # print("### Got input_xml_str={}".format(input_xml_str))
            except Exception as e:
                if 1 == 1:
                    log_messages.append(
                        "\tSkipping read failure {} for input_file_name={}"
                        .format(e,input_file_name))
                count_input_file_failures += 1
                continue

        row_index += 1

        #Create an internal root document node to manage database outputs
        doc_root = etree.Element("doc")
        doc_root.attrib['file_name'] = input_file_name
        msg = ("{}:calling xml_doc_rdb with doc_root.tag={}, file_count={},"
          .format(me,doc_root.tag, file_count))
        #print(msg)

        sub_messages = xml_doc_rdb(od_relation=od_relation
            , output_folder=output_folder
            , input_file_name=input_file_name
            , file_count=file_count
            , doc_rel_name = doc_rel_name
            , doc_root=doc_root
            , doc_root_xpath=doc_root_xpath
            , d_node_params=d_node_params
            , od_rel_datacolumns=od_rel_datacolumns
            , verbosity=verbosity
            , d_xml_params=d_xml_params)

        if len(sub_messages) > 0 and False:
            log_messages.append({'xml-tsv':sub_messages})

        if verbosity > 2:
            log_messages.append( "Got stats for input file[{}], name = {}. \n"
                .format(i+1, input_file_name)
                 )
        # end for i, fname in input_file_list
    # end with open() as output_file
    print ("Finished processing through file_count={}".format(file_count))

    #### CREATE THE RDB INSERT COMMANDS - HERE USING SQL THAT WORKS WITH MSOFT SQL
    # SERVER 2008, maybe 2008+

    sql_filename = "{}/sql_server_creates.sql".format(output_folder)
    use_setting = 'use [{}];\n'.format(use_db)
    msg = ("Database sql create statements file name: {}".format(sql_filename))
    log_messages.append(msg)
    print(msg)

    with open(sql_filename, mode='w', encoding='utf-8') as sql_file:
        print(use_setting, file=sql_file)
        #TEST OUTPUT create table statements for sql server...
        print('begin transaction;', file=sql_file)
        for rel_key, d_relinfo in od_relation.items():
            relation = '{}{}'.format(rel_prefix,rel_key)

            print(("IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{}') "
                   "TRUNCATE TABLE {}").format(relation,relation), file=sql_file)

            print(("IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{}') "
                   "drop table {}").format(relation,relation), file=sql_file)

        for rel_key, d_relinfo in od_relation.items():
            relation = '{}{}'.format(rel_prefix,rel_key)
            #print("{}: Table {}, od_relation has key={}, value of d_relinfo with its keys={}"
            #      .format(me, relation, rel_key, repr(d_relinfo.keys())))
            if 'attrib_column' not in d_relinfo:
                print("{}: WARNING: Table {} has keys={}, but no values for it in current "
                    "file were found.".format(me,relation,repr(d_relinfo.keys())))
                continue

            # SQL CREATE SYNTAX FOR COLUMNS
            print('create table {}('.format(relation), file=sql_file)

            d_column_type = d_relinfo['attrib_column']
            # Create serial number, sn column for every table
            # print('sn int not null identity(1,1)', file=sql_file)
            sep = ''
            #print("{}:Getting columns for relation '{}'".format(me,relation))
            if d_column_type is None:
                raise Exception("Table {}, d_column_type is None".format(relation))
            for i,(column, ctype) in enumerate(d_column_type.items()):
                #print("Column index {}".format(i))
                import sys
                sys.stdout.flush()
                #print("Column = {}.{}".format(relation,column))

                if ctype is None:
                    raise Exception("Table {}, column {} ctype is None".format(relation,column))
                if column is None:
                    raise Exception("Table {} has a None column".format(relation))

                print('{}{} {}'.format(sep,column.replace('-','_'),ctype)
                    ,file=sql_file)
                sep = ','

            #PRIMARY KEY eg: CONSTRAINT pk_PersonID PRIMARY KEY (P_Id,LastName)
            print('CONSTRAINT pk_{} PRIMARY KEY({})'.format(relation, d_relinfo['pkey'])
                 , file=sql_file)

            #End table schema definition
            print(');', file=sql_file)

        # loop over relations
        print("\nCOMMIT transaction;", file=sql_file)

        ############### WRITE BULK INSERTS STATEMENTS TO SQL_FILE

        for rel_key, d_relinfo in od_relation.items():
            # Allow a prefix for all table names. Sometimes useful for
            # longitudinal studies.
            relation = '{}{}'.format(rel_prefix,rel_key)

            #bulk insert statement
            print('begin transaction;', file=sql_file)

            print("\nBULK INSERT {}".format(relation), file=sql_file)
            print("FROM '{}/{}.txt'".format(output_folder,rel_key), file=sql_file)
            print("WITH (FIELDTERMINATOR ='\\t', ROWTERMINATOR = '\\n');\n", file=sql_file)
            print("\nCOMMIT transaction;", file=sql_file)
            print('begin transaction;', file=sql_file)

            # AFTER loading data for this relation, now add the sn column.
            print("ALTER TABLE {} ADD sn INT IDENTITY;"
                  .format(relation), file=sql_file)
            print("CREATE UNIQUE INDEX ux_{}_sn on {}(sn);"
                  .format(relation,relation), file=sql_file)
            print("\nCOMMIT transaction;", file=sql_file)
        # end statements for bulk inserts
    # end sql output

    # Close all the table data output files in od_relation
    for d_info in od_relation.values():
        file = d_info.get('db_file', None)
        if file is not None:
            file.flush()
            file.close()

    return count_input_file_failures
# end def xml_paths_rdb

# RUN PARAMS AND RUN
import datetime
import pytz
import os
from collections import OrderedDict
'''
xml2rdb is the main method.
It accepts three main groups of input parameters:
(1) to define the  group of input xml files to read
(2) to define the SQL schema for tables and columns to be outputted
(3) to define the mining map that associates table and column names with
    target nodes (designated by child xpath expressions) and their values in
    each inputted xml file.
These parameters may be re-grouped later into fewer parameters to more plainly separate
the three groups, each which contains sub-parameters for its group.
'''
def xml2rdb(folders_base=None, input_path_list=None,
            doc_root_xpath=None, rel_prefix=None,
            doc_rel_name=None, use_db=None,
            d_node_params=None, od_rel_datacolumns=None,
            d_params=None, file_count_first=0, file_count_span=1,
            d_xml_params=None):
    me = "xml2rdb"
    utc_now = datetime.datetime.utcnow()
    utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")
    print("{}: STARTING at {}".format(me, utc_secs_z))


    if not ( 1 == 1
        #and folders_base and input_path_list
        #and doc_root_xpath and use_db and doc_rel_name
            #and (rel_prefix or rel_prefix == '')
            #and d_node_params and od_rel_datacolumns
            #/and d_params
            and d_xml_params is not None
            ):
            print ("bad args 1")
    if not (folders_base and input_path_list
            and (rel_prefix or rel_prefix == '')
            and doc_root_xpath and use_db and doc_rel_name
            and d_node_params and od_rel_datacolumns
            and d_params
            and d_xml_params is not None
            ):
        raise Exception('{}:bad args'.format(me))

    d_log = OrderedDict()

    folder_output_base = folders_base + me + '/'
    folder_output_base = etl.data_folder(
        linux = "/home/robert/data/",
        windows = "U:/data/",
        data_relative_folder='outputs/xml2rdb')

    d_params['folder-output-base'] = folder_output_base
    os.makedirs(folder_output_base, exist_ok=True)

    # We also use secsz_start as part of a folder name, and windows chokes on ':', so use
    # all hyphens for delimiters
    secsz_start = utc_now.strftime("%Y-%m-%dT%H-%M-%SZ")

    # The output_folder encodes start time of run in its name.
    output_folder_secsz = '{}/{}'.format(folder_output_base, secsz_start)
    os.makedirs(output_folder_secsz, exist_ok=True)
    lil = len(input_path_list)

    print("Using output folder={} total real file count={}"
          .format(output_folder_secsz, lil))

    if file_count_first is None:
        input_low_index = 0
    else:
        input_low_index = file_count_first

    # Special test - if file count span is 0, then examine all files above low_index
    if  file_count_span is None or file_count_span <= 0:
        input_high_index = lil
    else:
        input_high_index = file_count_first + file_count_span

    # Use a slice of the total input file list, which may also be the full list.

    index_max = lil if input_high_index > lil else input_high_index
    sliced_input_path_list = input_path_list[input_low_index:index_max]
    #output_name_suffix="_{}_{}".format(input_low_index,index_max)

    os.makedirs(output_folder_secsz, exist_ok=True)
    skip_extant = False
    d_params.update({
        'secsz-1-start': secsz_start
        ,'output-folder': output_folder_secsz
        ,'input-files-index-limit-1-low': repr(input_low_index)
        ,'input-files-index-limit-2-high': repr(input_high_index)
    })

    d_log['run_parameters'] = d_params

    #### Open all the output files for all the relations... ####

    ################# READ THE INPUT, AND COLLECT AND OUPUT STATS ################

    count_input_file_failures = (xml_paths_rdb(
        input_path_list=sliced_input_path_list
      , doc_root_xpath=doc_root_xpath
      , rel_prefix = rel_prefix
      , doc_rel_name = doc_rel_name
      , output_folder=output_folder_secsz
      , d_node_params=d_node_params
      , od_rel_datacolumns=od_rel_datacolumns
      , use_db=use_db
      , file_count_first=file_count_first
      , file_count_span=file_count_span
      #, output_name_suffix=output_name_suffix
      , verbosity=0
      , d_xml_params=d_xml_params
    ))
    d_log['run_parameters'].update({"count_input_file_failures": count_input_file_failures})
    # Put d_log, logfile dict info, into xml tree,  and then OUTPUT logfile info
    # as an xml tree.
    secsz_finish = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
    d_log['run_parameters'].update({"secsz-2-finish": secsz_finish})

    e_root = etree.Element("uf-xml2rdb")
    # add_subelements_from_dict(e_root, d_log)
    etl.add_subelements(e_root, d_log)

    # log file output
    log_filename = '{}/log_xml2rdb.xml'.format(output_folder_secsz)
    with open(log_filename, mode='w', encoding='utf-8') as outfile:
        pretty_log = etree.tostring(e_root, pretty_print=True)
        outfile.write(pretty_log.decode('utf-8'))
    return log_filename, pretty_log
# end def xml2rdb

''' SET UP MAIN ENVIRONMENT PARAMETERS FOR A RUN OF XML2RDB
Now all these parameters are 'hard-coded' here, but they could go into
a configuration file later for common usage.
Better still, this would all be managed by a web-interface with xml2rdb as a back end.
This is where a web service comes in that
(1) manages thousands of users accounts,
(2) collects fees for
  (a) configuration file storage,
  (b) uploads and storage of the xml input files
  (c) storage for versions of SQL output (paired with input files)
  (d) paid user downloads of the SQL outputs.
  (e) and more...
'''
# FILE INPUT PARAMS -- IDENTIFY A PARTICULAR SET OF XML INPUT FILES TO ANALYZE
# and the 'root' doc_path_xpath to expect in every xml file in the set.


# Study choices
study = 'elsevier'
study = 'oadoi'
study = 'scopus'
study = 'elsevier'
study = 'crafa'
study = 'scopus'
study = 'crawd' # Crossref filter where D is for doi
study = 'crafd' # Crossreff affiliation filter where D here is for Deposit Date.
study = 'orcid'
study = 'citrus'

# KEEP ONLY ONE LINE NEXT: Study Selection
study = 'citrus'

file_count_first = 0
file_count_span = 0
use_db = 'silodb'

folders_base = etl.home_folder_name() + '/'

d_xml_params = {}

if study == 'crafa':
    # Note- input folder is/was populated via program crafatxml
    rel_prefix = 'y2016_'
    # All files under the input folder selected for input_path_list below will be used as input
    input_folder = '{}/output_crafatxml/doi/2016'.format(folders_base)
    input_folder = etl.home_relative_folder('/output_crafatxml/doi/2016')
    doc_rel_name = 'cross_doi' # must match highest level table dbname in od_rel_datacolumns
    #doc_root_xpath = './crossref-api-filter-aff-UF' #this matches root node assignment in crafatxml program
    doc_root_xpath = './crossref-api-filter-aff-UF/message'
    input_path_list = list(Path(input_folder).glob('**/doi_*.xml'))
    print("STUDY={}, got {} input files under {}".format(study, len(input_path_list),input_folder))
    # Get SQL TABLE PARAMS (od_rel_datacolumns) and MINING MAP PARAMS
    od_rel_datacolumns, d_node_params = sql_mining_params_crossref()
    file_count_first = 0
    file_count_span = 0
elif study == 'crawd': # CrossRefApi Works by Doi-list
    # Note- input folder is/was populated via program crawdxml- where crawdxml gets Works Dois MD
    # for 'new' uf articles as found by diffing a week to week SCOPUS harvest of UF-affiliated dois/articles
    rel_prefix = 'crawd_' # maybe try wd_ as a prefix sometime
    input_folder = '{}/output_crawdxml/doi'.format(folders_base)
    doc_rel_name = 'cross_doi' # must match highest level table dbname in od_rel_datacolumns
    doc_root_xpath = './response/message'
    input_path_list = list(Path(input_folder).glob('**/doi_*.xml'))
    print("STUDY={}, got {} input files under {}".format(study, len(input_path_list),input_folder))
    # Get SQL TABLE PARAMS (od_rel_datacolumns) and MINING MAP PARAMS
    od_rel_datacolumns, d_node_params = sql_mining_params_crossref()
    file_count_first = 0
    file_count_span = 0
elif study == 'crafd': # CrossRefApi filter by D for deposit date (and it selects only UF affiliations)
    # Note- input folder is/was populated via program crafdtxml
    rel_prefix = 'crafd_'
    # NOTE LIMIT INPUT FOLDER TO YEAR 2016 for now...
    input_folder = '{}/output_crafdtxml/doi/2016'.format(folders_base)
    doc_rel_name = 'cross_doi' # must match highest level table dbname in od_rel_datacolumns, set below.
    #Next doc_root_xpath is set by the harvester crafdtxml so see its code.
    doc_root_xpath = './crossref-api-filter-date-UF/message'

    input_path_list = list(Path(input_folder).glob('**/doi_*.xml'))
    print("STUDY={}, got {} input files under {}".format(study, len(input_path_list),input_folder))
    # Get SQL TABLE PARAMS (od_rel_datacolumns) and MINING MAP PARAMS
    od_rel_datacolumns, d_node_params = sql_mining_params_crossref()
    file_count_first = 0
    file_count_span = 0
elif study == 'elsevier':
    if env == 'uf':
        #UF Machine
        file_count_first = 0
        # file_count_span of 0 means process all input files under input
        # folder of file_count_first index or greater
        file_count_span = 0
    elif env == 'home':
        #HOME - Linux machine - test run with span 1000
        file_count_first=0
        file_count_span=1000
    else:
         raise Exception("Invalid env={}".env)
    input_folders = []
    input_path_glob = '**/pii_*.xml'

    # Set input folders to 'orig load date' years that might possibly have items showing
    # cover_year 2016
    rel_prefix='e2016b_'
    for year in ['2015','2016', '2017']:
        input_folders.append('{}/output_ealdxml/{}/'.format(folders_base,year))

    doc_rel_name = 'doc'
    doc_root_xpath = './{*}full-text-retrieval-response'

    # Get SQL TABLE PARAMS (od_rel_datacolumns) and MINING MAP PARAMS
    od_rel_datacolumns, d_node_params = sql_mining_params_elsevier()
elif study == 'scopus':
    folders_base = 'c:/rvp/elsevier'
    rel_prefix = 'h5_' #h5 is harvest 5 of 20161202
    rel_prefix = 'h6_' #h6 is harvst 6 of 20161210 saturday
    rel_prefix = 'h7_' #h7 is 20161216 friday
    rel_prefix = 'h8_' #h8 is 20161223 friday - not run
    rel_prefix = 'h9_' #h9 is 20161230 friday - not run

    # Year 2016 input
    input_folder = '{}/output_satxml/2016/doi'.format(folders_base)
    rel_prefix = 'h2016_10_' #h2016 is for query pubyear 2016, 10 is for harvest 10 done on 20170106 friday

    #Year 2017 input                                                   # Year 2016 input
    #input_folder = '{}/output_satxml/2017/doi'.format(folders_base)
    #rel_prefix = 'h2017_10_' #2016 for query pubyear 2016 harvest h10 is 20170106 friday

    input_path_list = list(Path(input_folder).glob('**/doi_*.xml'))

    doc_rel_name = 'scopus'
    doc_root_xpath = './{*}entry'
    od_rel_datacolumns, d_node_params = sql_mining_params_scopus()
elif study == 'oadoi':
    # for 20161210 run of satxml(_h6) and oaidoi - c:/rvp/elsevier/output_oadoi/2016-12-10T22-21-19Z
    # for 20170308 run using dois from crafd_crawd for UF year 2016

    input_folder =  folders_base + "/outputs/oadoi/"
    input_folders = [input_folder]
    input_path_glob = '**/oadoi_*.xml'
    input_path_list = list(Path(input_folder).glob(input_path_glob))

    print("Study oadoi, input folder={}, input path glob={}, N input files={},"
          " folders_base = {}"
          .format(input_folder,input_path_glob,len(input_path_list),folders_base))

    # rel_prefix 'oa2016_' is used because the oaidoi precursor process to produce the dois input list
    # was run on scopus dois fo/der uf authors from year 2016... should probably change prefix to oa_scopus2016_
    # input_folder = '{}/output_oadoi/2016-01-10T12-54-23Z'.format(folders_base)
    rel_prefix = 'oa_cruf2016_'
    doc_rel_name = 'oadoi'
    doc_root_xpath = './{*}entry'
    od_rel_datacolumns, d_node_params = sql_mining_params_oadoi()
elif study == 'orcid':
    #for 20161210 run of satxml(_h6) and oaidoi - c:/rvp/elsevier/output_oadoi/2016-12-10T22-21-19Z
    #input_folder = '{}/output_oadoi/2017-01-10T12-54-23Z'.format(folders_base)
    # for 20170308 run using dois from crafd_crawd for UF year 2016
    input_folder = '{}/output_orpubtxml'.format(folders_base)
    input_folders = [ input_folder]
    input_path_glob = '**/orcid_*.xml'
    input_path_list = list(Path(input_folder).glob(input_path_glob))

    print("Study {}, input folder={}, input path glob={}, input files={}"
          .format(study, input_folder,input_path_glob,len(input_path_list)))
    input_path_list = list(Path(input_folder).glob(input_path_glob))
    rel_prefix = 'orcid_'
    doc_rel_name = 'person'
    #TODO: add batch id or dict column_constant to define column name and constant to insert in the
    # doc_rel_name table to hold hash for external grouping studies, repeated/longitutinal studies
    #raise Exception("Development EXIT")

    doc_root_xpath = './{*}record'
    od_rel_datacolumns, d_node_params = sql_mining_params_orcid()
elif study == 'citrus':
    #for 20161210 run of satxml(_h6) and oaidoi - c:/rvp/elsevier/output_oadoi/2016-12-10T22-21-19Z
    #input_folder = '{}/output_oadoi/2017-01-10T12-54-23Z'.format(folders_base)
    # for 20170308 run using dois from crafd_crawd for UF year 2016
    input_folder = '{}/output_citrus_mets'.format(folders_base)
    input_folder = etl.data_folder(linux='/home/robert/', windows='u:/',
        data_relative_folder='data/citrus_mets_base')
    input_folders = [ input_folder]
    input_path_glob = '**/*mets.xml'
    input_path_list = list(Path(input_folder).glob(input_path_glob))

    print("Study {}, input folder={}, input path glob={}, input files={}"
          .format(study, input_folder,input_path_glob,len(input_path_list)))
    input_path_list = list(Path(input_folder).glob(input_path_glob))
    rel_prefix = 'citrus_'
    doc_rel_name = 'mets'
    #TODO: add batch id or dict column_constant to define column name and constant to insert in the
    # doc_rel_name table to hold hash for external grouping studies, repeated/longitutinal studies
    #raise Exception("Development EXIT")

    doc_root_xpath = './METS:mets'
    d_xml_params['attribute_text'] = 'attribute_text'
    d_xml_params['attribute_innerhtml'] =  'attribute_innerhtml'
    od_rel_datacolumns, d_node_params = sql_mining_params_citrus_bibs()
else:
    raise Exception("Study ={} is not valid.".format(repr(study)))

# OPTIONAL - If a study specified multiple input folders and input_path_glob,
# then honor them when constructing the input_path_list
if (input_folders is not None and input_path_glob is not None):
    # compose input_path_list over multiple input_folders
    input_path_list = []
    for input_folder in input_folders:
        print("Using input_folder='{}'\n".format(input_folder))
        input_path_list.extend(list(Path(input_folder).glob(input_path_glob)))

# Put single input folder into this list so param 'input-folders' is logged properly.
if input_folders is None:
    input_folders = []
    input_folders.append(input_folder)

lip = len(input_path_list)
if (lip < 1 ):
    raise Exception(
        "No input files in input_folder='{}'".format(input_folder))
d_params = OrderedDict()
#d_params = OrderedDict()
d_params.update({
     'python-sys-version': sys.version
    #,'input-files-xml-folder' : input_folder
    ,'study': repr(study)
    ,'input-folders': repr(input_folders)
    ,'input-files-count': str(len(input_path_list))
    ,'file-count-first': file_count_first
    ,'file-count-span': file_count_span
    ,'folders_base': folders_base
    ,'doc-rel-name': doc_rel_name
    ,'doc-root-xpath': doc_root_xpath
    ,'use-db': use_db
    ,'d-node-params': repr(d_node_params)
    ,'od-rel-datacolumns': repr(od_rel_datacolumns)
})

# RUN the analysis and collect stats
log_filename, pretty_log = xml2rdb(
    folders_base=folders_base,input_path_list=input_path_list,
    doc_root_xpath=doc_root_xpath, rel_prefix=rel_prefix,
    doc_rel_name=doc_rel_name, use_db=use_db,
    d_node_params=d_node_params, od_rel_datacolumns=od_rel_datacolumns,
    d_params=d_params, file_count_first=file_count_first, file_count_span=file_count_span,
    d_xml_params=d_xml_params)

print("Done.")
#
