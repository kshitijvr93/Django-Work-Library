from collections import OrderedDict
def sql_mining_params():

    od_rel_datacolumns = OrderedDict([
        ('entitlement', OrderedDict([
            ('doi_url',''),
            ('prism_url',''),
            ('pii_norm',''),
            ('eid',''),
            ('entitled',''),
            ('message',''),
            ('scidir_url',''),
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
            "./dc:identifier": {
                'multiple':0,
                'attrib_column': { 'text':'entitlement' },
            }
            ,"./prism:url": {
                'multiple':0,
                'attrib_column': { 'text':'prism_url' },
            }
            ,"./pii-norm": {
                'multiple':0,
                'attrib_column': {'text':'pii_norm' }
            }
            ,"./eid": {
                'multiple':0,
                'attrib_column': {'text':'eid' }
            }
            ,"./entitled":{
                'multiple':0,
                'attrib_column':{'text':'entitled'}
            }
            ,"./message":{
                'multiple':0,
                'attrib_column':{'text':'message'}
            }
            ,".//link":{
                'multiple':0,
                'attrib_column':{'text':'scidir_url'}
            }
        } # end child_xpaths
    } # end d_node_params

    return od_rel_datacolumns, d_node_params

#end def sql_mining_params
