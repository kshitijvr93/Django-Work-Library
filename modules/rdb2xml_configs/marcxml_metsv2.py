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
For first draft purposes, its fields are considered to be in the 'record'
relation, though the are not in the actual database.
Since only record-level output is generated, we can do it this way... that
is, there is no 'context' record that is supposed to be outputted, so the
context info can be imputed to each record logically.

Since this tree is not too deep, for clarity, and to avoid any column name
collisions among tables, all column names will be prefixed by their
ancestor relation names in order, separated by the '.' character

Where an attribute or xml tag is linked to a data value, if the value or
values do not exist then the tag is not going to be output either.
Maybe a flag will be provided to indicate that empty output tags are desired.

Where some METS output value depends on a combination of other values, a method will be provided similar to xml2rdb
column functions that can input various values and apply coding and logic to determine its output to be used
in the xml output.

Note: Maybe use 'batch_context' or 'batch' as opseudo-relationto hold context info
It is a pseudo-relation  of just one row with batch/global variables like start time of the run, user who is running
Here will be the batch variables,

Also: phase N feature: consider: do allow it to 'tick' with a real-time clock, at least one current_time value?
or implement that as yet another pseudo-relation that has its own cursor or that just gives the current time when 'incremented'
and tie it somehow to co-yield (aka increment, aka iterate) only when a new record is incremented. Maybe just set it as a
special 'column_name' that can be ascribed/referenced in any/every relation. If a relation has that value and it is incremented,
the program will just set that constant value in this column name that can be used like any other column name (phase N feature).

Phase N alt feature: for each relation name, allow a keyword that defines of a yield

Alt Clock - best so far:  -- an ordinary xml2rdb style of column function can be/do a clock. It will simply not use any data input, but rather
do a date call to the os and return that.

Alt Batch - same idea as the column_function to implement the clock. Also use a column function to implement assignment of the
next bibid and invoke it for the record relation. fine.

'''

d_node_params: {
    '''
    This node is for the highest level marc rdb relation named 'record'
    or some configuration pre-defined relation name for the main_relation.
    Each record will be reprented by its own xml file in an output directory,
    with files named like:

    element_tag_00000000.xml

    where element_tag is the value for the key of element_tag
    given below (here that value is also 'record') in the main dictionary
    and 00000000 is a zero padded 8 digit consecutive integer.

    Future feature: can add a check to NOT produce a record or xml tagged section in the
    output file if all  the mined column values for attributes for the xml element_tag
    are found to be null or empty.
    For now, each child xml open/close tag is written to the output file for
    each encountered db record.
    '''

    ,'element_tag':'record'
    ,'attribute_column': {
        'text' : 'leader'
    }
    ,'relation_child_nodes': {
        'controlfield': {
            'element_tag' : 'controlfield'
            'attribute_column':{
                'tag':'tag', 'text':'value'
            }
        }
        ,'datafield': {
            'element_tag': 'datafield',
            'attribute_column': {
                'tag' : 'tag'
                ,'ind1': 'indicator1'
                ,'ind2': 'indicator2'
            }
            'relation_child_nodes' : {
                'subfield': {
                    'element_tag': 'subfield'
                    ,'attribute_column' : {
                        'code':'code'
                        ,'text':'value'
                    }
                }
            }
        }
    }
}
