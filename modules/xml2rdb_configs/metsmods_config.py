# metsmods_config.py
# originally based on elsevier.py config,
#

import sys, os, os.path, platform
def get_path_modules(verbosity=0):
  env_var = 'HOME' if platform.system().lower() == 'linux' else 'USERPROFILE'
  path_user = os.environ.get(env_var)
  path_modules = '{}/git/citrus/modules'.format(path_user)
  if verbosity > 1:
    print("Assigned path_modules='{}'".format(path_modules))
  return path_modules
sys.path.append(get_path_modules())

from collections import OrderedDict
import mappers

'''
Method sql_mining_params_metsmods

Plain Python code here define and return the two main data structures:
(1) od_rel_datacolumns: defines RDB output tables and data columns per table.
     Note: table columns for the primary key composite index for each table are
     defined indirectly by input structure 2, and populated automatically by
     xml2rdb
(2) d_node_params: Define a 'mining  map'. It is a nested hierarchy of relative
    XPATH expressions leading to XML nodes, each with a with a map of xml
    tag(text) or attribute values to output to associated SQL table columns.

The functionality of doing custom configuration can move to using configuration
files to assist users who are not familiar with Python.
'''

def sql_mining_params():
    '''
    d_nodeparams is a dictionary hierarchy of parameters for a call to
    node_visit_output().

    The d_nodeparams dictionary may have keys with the following described
    values:

    Key 'multiple':
        If present, this means that this node will produce some output db data,
        and it means that the other keys in this dictonary will be examined.
        If not present, any other keys listed below will be ignored.
        The value of 0 means this is a single (or zero)-occurrence node under
        its parent, and value of 1 means that it is a multiple-occurrence node
        under its parent.
        This parameter may be removed soon. The presence of a dbname rather can
        be used to infer that a node has multiple of 1 and the absence of a
        dbname for a node implies a multiple value of 0.
    Key 'db_name':
       This is the table name for a db-relation for this node, which is
       allowed to appear multiple times under its ancestor node.
       The node count under its ancestor will be outputted as part of a sql
       table row composite key value.
    Key 'text':
        If present, this means that the text value of the visited node is to
        be output, with the value being the name of the db output column to
        use for the output of any text value of this node.
        However if that value is None or empty, the column name will be the
        db_name value.
        Note: the user must pre-examine all the  db_name and text values to
        make sure that those under the same immediate parent xpath have
        unique names.
        And that no db_name with multiple = 1 is a duplicate name.
    Key 'attrs':
        If present, the value is a list of attribute names to produce the
        database column names named in the values.
        A value for each db column name will be output, regardless of whether
        that attribute names is found on a particular node.
        The special name 'text' now means to output the content of the node,
        rather than an attribute.
        This special name may change to 'node_content' soon to avoid collision
        with valid attributes also named 'text' in some cases.
    Key 'child-xpaths'
        If present, the xpath must lead to a descendant node in the tree, and
        the value is another dictionary like the d_nodeparams dictionary.

    '''

    '''
    Note: The main program declares a root node relation name, 'doc', and
    affixes one special column_name, called 'file_name',
    where it records the file name of the inputted xml doc.
    Therefore, this od_rel_datacolumns dictionary below must define one
    table/key called 'doc' with the column 'file_name', and add any other
    desired column names there as well.
    An option to not require this can be easily added.

    Program xml2rdb will parse each xml file to an xml document tree with a
    document root, and it will call node_visit_output(d_node_params) on that
    doc root.
    Maybe a paramter will be added to allow selection of another root relation
    name than 'doc', but it is not a bad general name, as it is a node to
    describe a doc metadata, like the input filename for it and other data
    about it...

    Note: I also envision a revision of this program to do a walk-through of
    the xml input files and derive a complete set of SQL tables, infer and
    define the entire hierarchical structure, and glean all of the XML input
    into relational tables (for a consistent set of structured XML).
    It will infer names for tables and columns from the xml tags and attribute
    names as well.
    '''

    od_rel_datacolumns = OrderedDict([
        ('doc', OrderedDict([
            ('id','0'),
            ('mets_objid','0'),
            ('mets_create_dtatetime,'')
            ('mets_lastmod_datetime',''),
            ('mods_abstract','')
            ('mods_access_condition',''),
            ('mods_classification',''),
            ('mods_extension',''),
            ('mods_genre',''),
            ('mods_identifier',''),
            ('mods_language',''),
            ('mods_location',''),
            ('mods_name',''),
            ('mods_originInfo',''),
            ('mods_part',''),
            ('mods_physical_description',''),
            ('mods_record_info',''),
            ('mods_related_item',''),
            ('mods_table_of_contents',''),
            ('mods_target_audience',''),
            ('mods_title_info',''),
            ('mods_type_of_resource',''),
        ])),

        ('identifier', OrderedDict([ #parent relatio is 'doc'
            ('id',''),
            ('type',''),
            ('text',''),
        ])),
        ('agent', OrderedDict([ #parent relatio is 'doc'
            ('id',''),
            ('role',''),
            ('name',''),
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
    every affiliation listed in that author-group, and this association is
    different from serial items (below).
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
                'column_function' : {'last_first_name':mappers.last_first_name},

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
                        'column_function' : {'uf':(mappers.uf_affiliation_by_colname,{'colname':'name'})},
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
                'column_function' : {'last_first_name':mappers.last_first_name},
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
                        'column_function' : {'uf':mappers.uf_affiliation_value}
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
                'column_function': {'pii': mappers.pii_unformatted}
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
                'column_function': {'cover_year': mappers.cover_year}
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
#end def s_elsevier(
print("Done")
