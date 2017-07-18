###### START OADOI INPUT PARAMETERS ########
from collections import OrderedDict
def sql_mining_params():

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
