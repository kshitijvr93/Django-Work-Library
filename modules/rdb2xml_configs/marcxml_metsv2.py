'''
different mining map for rdb2xml than another alternatives..
here we show ournodes are simple.. just nested properly relation names.
We need to let the data selection of a row happen by visiting a 'relpath' node
and then under that we have params that show how to build the xml based on the existence
of the data in the current row of each ancestor to the node and the current node.
In case of repeated column names, do allow relname.colname notation.
For a given relpath node we have a list of nodes, each that informs how to construct some xml tag that relies on it,
like a dictionary of column_attribute names or column_to_list of attribute names in case we need to project
a column name to more than 1 xml attributes or values..
.
This provides the way to detect and properly process repeated rows under a parent node, as we do with the findall()
method when doing the xml2rdb
examine the marc tables for ccila and visit them to create a METS file.

NOTE: the keys of relation params may all be prefixed with a runtime parameter name,
for example "ccila_" for my first runs.

note: the global relation context is not in the database, but rather it has context information like the
current date and time, person who is running the process, etc.
For first draft purposes, its fields are considered to be in the 'record' relation, though the are not in the actual
database. Since only record-level output is generated, we can do it this way... that is, there is no 'context' record
that is supposed to be outputted, so the context info can be imputed to each record logically.

Since this tree is not too deep, for clarity, and to avoid any column name collisions among tables, all column names will be prefixed by their ancestor relation names in order, separated
by the '.' character

Where an attribute or xml tag is linked to a data value, if the value or values do not exist then the tag is not
going to be output either. Maybe a flag will be provided to indicate that empty output tags are desired.

Where some METS output value depends on a combination of other values, a method will be provided similar to xml2rdb
column functions that can input various values and apply coding and logic to determine its output to be used
in the xml output.
'''
od_relation_params = {
'record': {
    'child_records': {
        'controlfield': {}
        ,'datafield': {
            'subfield': {
                }
            }
        }
    }
}
'controlfield':


}
