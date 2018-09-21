###### START merrick_oai_set PARAMETERS ########
from collections import OrderedDict

'''
Note: main document root tag is <OAI-PMH>, single main container is <ListSets>, and record container is <set>, aka the node for the main db_name 'merrick_oai_set'

NOTE: these rel names must NOT collide with rel names in other merrick_*.py config
files because though the extract data from separate API endpoints,
their data must interrelate in the same output database to facilitate analytics, reports.
Better, they should all use the same unique prefix "merrick_oai_" to establish sane
relation/table names in the same destination database.
'''

def sql_mining_params():

    od_rel_datacolumns = OrderedDict([
        ('parent', OrderedDict([
            ('notes',''),
        ])),
        ('oaiset', OrderedDict([
            ('set_spec',''),
            ('set_name',''),
            ('set_description',''),
        ])),
    ])

#----------------------------------------------
    d_node_params = {
        #
        # The db_name of this root node is given in a runtime parameter, so db_name is
        # not given for this node.
        # NOTE: since a query for ListSets is not gigantic, the xml file is harvested by a simple copy-paste to a browser
        # url, and a request, followed by a copy of the xml results and paste to a local singleton file with a parent
        # <ListSets> node and multiple <set> nodes. This is unlike many other harvests where one directory holds mulitple
        # input files that are meant to be read.
        'multiple':0,
        'child_xpaths': {
            './{*}set' : {
                'db_name' : 'oaiset', 'multiple':1,
                'child_xpaths' : {
                    ".//{*}setSpec": {
                        'multiple':0,
                        'attrib_column': { 'attribute_text':'set_spec' },
                    }
                    ,".//{*}setName": {
                        'multiple':0,
                        'attrib_column': { 'attribute_text':'set_name' },
                    }
                    ,".//{*}description": {
                        'multiple':0,
                        'attrib_column': {'attribute_text':'set_description' }
                    }
                } # end set child_xpaths
            }
        }# end parent child_xpaths
    } # end d_node_params

    return od_rel_datacolumns, d_node_params

#end def sql_mining_params
