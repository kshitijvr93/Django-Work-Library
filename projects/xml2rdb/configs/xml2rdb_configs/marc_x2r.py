'''
marc_x2r.py

20171111

t1121- SUSPEND THIS DEVELOPMENT :for practical purposes --
because can sooner accomplish this by using
the simpler schema with marc records, control, data and sub fields,
and use a python script or stored procedures to produce per-marc-tag-value
relations/tables and insert into them.

--

This is proposed to read marcxml files and create a rdb representation that
provides a separate relation for each marc tag.

This is more directly usable for some programs than a simpler db representation
that simply has relations for record, datafield, controlfield, subfield.
Also, the set of output tables is more conceptually object based, in that each
marc_tag_named relation has rows that hold more similar data from row to row.

tags to harvest may expand as the input marc files vary, or other subsets of this
config file may be used to make simpler rdb datasets by simply ignoring some
rarely used marc tags.


'''
od_rel_datacolumns = OrderedDict([
    ('record', OrderedDict([
        ('leader',''),
    ])),

    ('data100', OrderedDict([
        ('indicator1',''),
        ('indicator2',''),
    ])),

    ('datafield', OrderedDict([
        ('tag', ''),
        ('indicator1',' '),
        ('indicator2',' '),
    ])),

    ('subfield', OrderedDict([
        ('code',''),
        ('value',''),
    ])),
])

#  DEFINE  d_node_params, the 'Mining Map'.
'''
For nonserial items, visual inspection of multiple xml files indicates that
every author listed in an author-group is associated with
every affiliation listed in that author-group, and this association is different from
serial items (below).
'''

d_node_params = {
    #
    # The db_name of this root node is always set by the caller, so db_name is
    # NOT given for this node.
    # Until design is improved, developer  should make sure it is the first name
    # given above,  'record'.
    # Must use multiple 0 for this root node too, for technical reasons.
    #
    'multiple':0,
    'child_xpaths' : {
        ".//{*}leader": {
            'multiple':0,
            'attrib_column': { 'text' : 'leader' },
        },
        ".//{*}controlfield": {
                'db_name':'controlfield', 'multiple':1,
                'attrib_column': { 'tag':'tag',  'text':'value', },
        },
        ".//{*}datafield": {
            'db_name':'datafield', 'multiple':1,
            'attrib_column': {
                'tag':'tag', 'ind1':'indicator1','ind2':'indicator2'
                },
            'child_xpaths' : {
                ".//{*}subfield" : {
                    'db_name':'subfield', 'multiple':1,
                    'attrib_column' : { 'code':'code', 'text':'value' },
                },
            },
        },
    } # end child_xpaths
} # end d_node_params
return od_rel_datacolumns, d_node_params
