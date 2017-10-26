# rdb2xml-active
# Somewhat cleaned-up code with various debug statements and cruft removed
# to use as a supplement document for IP examination

'''
Program rdb2xml  reads strcutured hierarchical relational database data
from a set of database tables that are rooted in a main root table.
It also reads a configuration file that defines how fields from the database
tables are to be output in an xml output file.

This program is based logically on doing the 'reverse' of what mature program
xml2rdb does.
Each input xml file has xml-coded information pertaining to a single xml
document.
'''
import sys, os, os.path, platform
sys.path.append('{}/git/citrus/modules'.format(os.path.expanduser('~')))
print("sys.path={}".format(repr(sys.path)))
import datetime
import pytz
import os
import sys
from collections import OrderedDict

from pathlib import Path
import hashlib

from lxml import etree
from lxml.etree import tostring
from pathlib import Path
import etl
'''
To read our structured related input data, we will use a simple database
table object that has a generator method, rows().

Each call to method rows will return the next row of data, in a dictionary
with string field values, or None if no more rows exist.

The keys used for each row match the column names in the database
for the returned values.

For the first implementation, consider to read each relational table from
a file.... or instantiate a parent db object that indicates the type of
dataset (mysql, postgres, sql server, tsv files etc) and a connection string if needed.
'''

'''
Method new_od_relation

Given arg od_rel_datacolumns, use its keys of relation names
to initialize a new odict od_relation with entries of the same key name,
and values of values of new od_rel_info dicts.

Return the new dict od_relation
'''
def new_od_relation(od_rel_datacolumns, verbosity=1):
    od_relation = OrderedDict()
    if verbosity:
        print("Creating relation with datacolumns:")
    for i,key in enumerate(od_rel_datacolumns.keys()):
        od_rel_info = OrderedDict()
        od_relation[key] = od_rel_info
        print("Table {}, name={}".format(i+1,key))
    return od_relation

'''
Method get_writable_db_file:

This method is designed to be called while the mining map nodes are being
visited from node_visit_output(), so that the od_parent_index dictionary is
properly populated with the parent relation name values that assign the
composite primary key column names of the given db_name in the mining map's
hierarchy.
This information is given in the argument od_parent_index.

The actual index values are not important here, but the parent relation
names are important so that the primary key column names for them can be
assigned to the given db_name relation.
This need only be done once, and coincidentally, the writable file handle
for the relation need only
be created once, and so it is also done within this routine.

Given a db_name of interest and od_relation of all relation names,
we get od_rel_info as the ordered dictionary value of od_relation[db_name].

We get or create od_column value for the od_rel_info key 'attrib_column' .
od_column is the dictionary of xml attribute-name keys with their sql
column-name values in the parent dictionary.

Note: SQL Server 2008 cannot handle utf-8 encoding, but we can use it for
most if not all other RDBs.

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
        raise Exception("{}:od_relation key (db_name) '{}' is undefined. "
            .format(me,repr(db_name)))

    od_column = od_rel_info.get('attrib_column', None)
    if od_column is None:
        # When here, this is the first encounter of a node with this db_name in
        # an input xml_file, and we assume the xml files are of consistent
        # structure, with same xml tag lineage,
        # with regard to the mining map'a paths of interest.
        # So we can use the first one found to set up the hierarchy/lineage of
        # the primary key's composite columns.
        #
        # We will create places to store info for this relation's attrib columns
        # and other 'mining' info, including sql olumn names of data we will
        # output for this relation
        od_column = OrderedDict()
        od_rel_info['attrib_column'] = od_column

        # Create and open a writable output file for this relation, mode='w',
        # encoding='utf-8'
        # If SQL server 2008 bulk insert chokes on utf-8, encode this to ascii

        filename = '{}/{}.txt'.format(output_folder,db_name)
        print('{}: opening output {}'.format(me, filename))
        od_rel_info['db_file'] = open(filename, mode='w'
            , encoding=output_encoding, errors=errors)

        #This RDB Table's Primary key value will be output as a simple string
        # of csv of column names
        od_pkey = OrderedDict()

        #Set up the primary key columns for this relation
        pkey_columns = ""
        sep = ''

        # First, for every parent of this relation, register a column name to
        # hold its index value and concat each col name to list of primary key
        # col names.
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

        # For datacolumns, set the SQL datatypes. Set all to nvarchar(MAX), which seems OK for now.
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
                od_column[column_name] = 'nvarchar(MAX)'
    # end storing misc mining info for a newly encounterd relation in the input
    else:
        #print("{}:Dict for attribute_column already found for db_name={}".format(me,db_name))
        pass
    # For the given db_name, return the writable file to the caller
    return od_rel_info['db_file']

#end def get_writable_db_file
'''
Method rnode_visit_output

Given parameters:
(*) node_index - the index of the current node (it is the depth of
    nesting) into the following parameters for lists of node_names and uuids
    The 'current node' in this method represents a single row in a relation
    that match the hierarchy of node_names (relations) and uuids.

(*) node_names (names of outer parents in nested
    relations where the first node name is the outermost nested relation and
    the last name is for this row row of the current relation), identified in uuids[]

(*) uuids[], (the parent nodes and current node is represented by this list
    path of hierarchical uuids from a set of parent database tables, with the
    final uuid identifying a unique row in the current node), and

(*) opened_index: index into node_names indicating the highest level where an opening tag
    has so far been outputted. This way, a recursive call that generates the first output for
    a node can determine the greatest ancestor parent that has not yet output its opening tag,
    and then output those tags in proper order, as needed.

(*) d_node_params, the 'mining map' starting with the
   given node's entry in the mining map hierarchy, garner the input fields
   for this node from the mining map in d_col elt maps each rdb column name
   inputs that is to be outputted to a named xml element.

 (*)od_row - ordered dictionary where each key is a column name and each value
 is the value for the column.
 This method reads that and uses it output the xml element values in the output.

(Note) to-be-considered: od_rel_datacolumns - key is column name, value is
    found value in the relational-database.
    In xml2rdb it is used to store values to be composed, for example a first
    name and last name may be stored among siblings to same xml parent, and a
    column_attribute function may be applied to derive a column with full
    last_name, comma, first_name' value. It is used for the 'translation' functionality
    of an ETL process, which may be of limited use since the data has already been
    mapped into the relational database, usually in a nice format.
    However, it might be reversed-emulated somehow in future versions for use
    in the rdb2xml direction.

Processing:

The node represents a 'current row', a specific data row in a table/db_name.
(*) If the row has any data to be output (per the below processing), an xml element
opening tag is outputted with the same name as the current row's table name.

(*) The param od_node_params may include a key 'od_attribute_column' which value is a dictionary where
each key is an attribute name to output and the value is a column name in the current row.
Special attribute names are reserved: text_content' indicates tha the rdb value is to put output as the main content of
the current xml elemnt being output. Other names are the actual xml attribute names to be outputted.

For each entry in od_attribute_column,
....
(1) first check the given 'opening_index' value that somhow indicates not-yet-outputted parent xml tags
and open all the parent tags given in array 'tags'(output their opening tag to the output stream)
consider:  let prior recursive caller just maintain arg tags and put in the ancestral line of unopened tags.
So in this call, if any value is detected that needs to be output, then output all openings of any tags, plus this
tag, and clear the tags list to pass down in next recursive call. To make things simpler, at very start of this method,
always append 'this' tag to the list of tags.


After a recursive call, the tags are included in the return values by the child.
If a child returns the tags list with any tags, then the last tag pertains to
this call instance, meaning no data was found to output for this tag,
and so do not output a closing tag, and DO delete this last tag in the list,
and then return that as part of the return value. This may be a phase 0 or phase 1 feature.
...

In a call instance, if an attribute has a non-null associated value:
(1) if the tags list has any tags, output an opening tag for each, in order, and
set the 'tags' list to empty.
(2) output the data value or setting
(3) plus output this nodes' closing tag which is the key value in rdb_xml,
(4) also update and return opening_index so the parent can determine whether its
node was opened and needs to have a closing tag outputted.

(*) If the param d_node_Params includes a key "child_names", then a loop
processes each child_name key to do a recursive call to output any child
elements and data.
Within iterations of that loop, meaning a child_name is given, a new select
cursor is created that selects all rows of the relation indicated in the child
name, and an inner loop is entered to deliver each row (via parameter od_row)
to a recursive call to rnode_visit_output for that row.

(*) After the 'child_path' processing code, and if any data was output from this node,
as inferred from the return values from the recursive calls (or the presence of a key in d_rdb_xml)
a closing tag is output.

Def rel_node_visit_output()
use this name, same as in xml2rdb except with rel_ prefix.

Compare and contrast some features with established node_visit_output() in xml2rdb as of 20171026:



'''

def rel_node_visit_output(node=None, node_index=None, d_namespaces=None,
    d_node_params=None, od_rel_datacolumns=None, od_parent_index=None,
    od_relation=None, output_folder=None,d_xml_params=None,verbosity=0):

    me = 'rel_node_visit_output()'
    verbose = 0
    if verbosity > 0:
        msg = ("{}:START: verbosity={},node.tag={}, node_index={}"
               .format(me, verbosity, node.tag, node_index))
        print(msg)
    log_messages = []

    # check arguments: later - revamp to check for this new rel_* method version...
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

    # if there is a special mining map 'attribute' keyword defined to indicate
    # to use the xml inner_content rather than
    # interpret that keyword to mean an attribute name to use... otherwise use
    # 'text' to mean inner xml element text content.
    attribute_text = d_xml_params.get('attribute_text','text')

    # same idea: seek special keyword to mean inner_html ... or inner_xml really
    attribute_innerhtml = d_xml_params.get('attribute_innerhtml','attribute_innerhtml')

    # if 'multiple' not in d_node_params:
    #    raise RuntimeError("{}: multiple keyword missing for node.tag={}"
    #            .format(me,node.tag))
    # pass along the parent index - we will append our index below only if multiple is 1

    # Prepare to pass along odict of parent indices to the child/recursive call...
    od_child_parent_index = od_parent_index

    #default multiple (repeatable element) value is 0 - so 0 means non-repeatable
    multiple = d_node_params.get('multiple', 0)
    multiple = 0 if mutliple == 0 else 1

    if verbose > 0 and multiple == 0 and node_index > 1:
        # Solution: in d_node_params, change multiple =0, provide a db_name, and also update
        # od_rel_datacolumns to include this db_name as a table if it does not already appear there.
        print("WARN:{}: node.tag={} has multiple == 0 but node_index = {}"
                    .format(me,node.tag,node_index))

    # We will put the data values of interest for this node into d_row.
    # d_row collects a dict of named data values for this node and is returned to caller if this node
    # has multiple indicator == 0.
    d_row = {}

    # d_attr_column: key is an attribute name and value is a relational column
    # name in which to outut the attribute value.
    # Because some attrib names have hyphens, this provides a way
    # that we can convert the attribute name to a similar-looking db column name, e.g, to
    # replace hyphens (that commonly appear in attribute names but are disallowed in many rdbs in
    # column names) with underbars (which are commonly alowed in rdbs in column names).
    # Of course, this mapping it also provides a way to change an attribute name
    # to any valid and different column name, but this is not recommended.

    d_attr_column = d_node_params.get('attrib_column', None)

    if d_attr_column is not None:
        # We have some node attributes destined for output to relational columns,
        # so we will set them up in d_row key-value pairs.
        if not isinstance(d_attr_column, dict):
            # detect some sorts of errors/typos in the d_node_params parsing configuration
            import types
            raise Exception("d_attrib_column {}, type={} is not dict. node.tag={}, node_index={}"
                    .format(repr(d_attr_column),repr(type(d_attr_column)),node.tag, node_index))

        node_text = etree.tostring(node, encoding='unicode', method='text')
        # Must discard tabs, used as bulk load delimiter, else sql server 2008 bulk insert error
        # messages appear, numbered 4832 and 7399, and inserts fail.
        node_text = node_text.replace('\t',' ').replace('\n',' ').strip()
        #node_text = "" if stringify is None else stringify.strip()

        for attr_name, column_name in d_attr_column.items():
            # For every key in attr_column, if it is reserved name in attribute_text,
            # use the node's text value, else seek the key in node.attrib
            # and use its value.

            # probably ill-thought 'shortcut' on next line. May deprecate/delete it,
            # as it invites non-explicit, easy to puzzle-over, None values in mining map.
            column_name = attr_name if column_name is None else column_name

            column_value = ''
            if attr_name == attribute_text:
                # Special reserved name in attribute_text: it is not really an attribute name,
                # but this indicates that we shall use the node's content/text for
                # this attribute
                column_value = node_text
            elif attr_name == attribute_innerhtml:
                # Special reserved name in attribute_text: it is not really an attribute name,
                # but this indicates that we shall use the node's inner 'html' value for
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

        # This node has an output, in the sense that is is mulitple/repeatable and so will have
        # as assigned node_index to track that is the count of this node as it is encountered in
        # the xml input file among the list also containing its siblings.
        # So we must make a copy of od_child_parent_index to an ordered dict by the same name,
        # as we do not need the original one.
        # Now to od_child_parent_index we will append this dbname with this node's index.
        # We will pass then pass our new od_child_parent_index to calls for child visits.
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
            if (verbosity > 0):
                print("{}:for xpath={} found {} children".format(me,xpath,len(children)))
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
                    , d_xml_params = d_xml_params
                    , verbosity=verbosity)
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
Method rdb_to_xml: from given xml doc(eg, from an Elsevier full text retrieval apifile),
convert the xml doc for output to relational data and output to relational tab-separated-value (tsv) files.
Excel and other apps allow the '.txt' filename extension for tab-separated-value files.

New twist - now this is rdb_to_xml
'''
def rdb_to_xml(
    tags=None
    ,d_root_node_params=None
    ,d_node_params=None
    ,output_folder=None
    ,d_xml_params=None
    ,od_rel_datacolumns=None # Add later to validate mining map
    ,od_relation=None
    ,input_file_name=None
    ,file_count=None
    ,doc_rel_name=None
    ,doc_root=None # doc element is meta element to use as root xml node per article/doc
    ,doc_root_xpath=None
    ,verbosity=0):

    me = 'rdb_to_xml()'
    log_messages = []

    required_args = [tags, output_folder]

    if not all(required_args)
        raise ValueError('Not all args {} were given.'.format(required_args))


        msg = ("{}:Got tags='{}', output_folder='{}', od_relation='{}',"
           "len(d_node_params)='{}', len od_rel_datacolumns={}."
          .format(me, repr(tags), output_folder, repr(od_relation)
                  ,len(d_node_params) ,len(od_rel_datacolumns)))
        print(msg)

    # retrieve next row from main relation's row generator method
    #
    # (1) Read an input xml file to variable input_xml_str
    # correcting newlines and doubling up on curlies so format() works on them later.
    # Class db will have opened the proper database that contains the relations.
    # The generator restricts the selected records to those that match in order on the hierarchy
    # coordinates or path indexes, in order of the columns defined by the relation's primary key.

    # 20171026 testing runs

    root_tag = 'docroot'
    relation_name = 'record'

    # final: row_selection = dataset.cursor_relation(relation_name='record', node_index=[])
    # testing:

    row_selection =  [{'a':'5', 'b':'6'}, { 'a':'8', 'b':'9' }]
    node_index = []
    output_file = ""
    tags = [root_tag]
    node = d_node_params['start'];
    # Above was emulation of some args - now star method code prototype

    tag = tags[len(tags) - 1]
    for row_index, d_row in enumerate(row_selection):
        print("For row {}, using d_row={}".format(row_index,repr(d_row)))
        # set args for rel_node_visit_output()
        node_index.append(row_index)

        #MAKE RECURSIVE CALL
        tags = rel_node_doc_visit(node=node, tags=tags, node_index,)

        if len(tags) == 0:
            # The tag at this level was opened and outputted, so now close it
            print("</{}>".format(tag), file=output_file)

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

    if verbosity > 1:
        print("xml2rdb: Using db_name='{}', doc_root_xpath='{}'"
          .format(doc_rel_name , doc_root_xpath))

    # OrderedDict with key of parent tag name and value is parent's index among its siblings.
    od_parent_index = OrderedDict()
    node_index = file_count

    # In this scheme, the root node always has multiple = 1 - that is, it may have multiple
    # occurences, specifically, over the set of input files.
    # Also, this program requires that it be included in the relational output files.
    multiple = 1

    with open(output_file_name, "w", encoding="utf-8") as output_file

    d_return = rel_node_visit_output(
        tags=['document_root']
        ,od_relation=od_relation
        ,d_namespaces=d_namespaces
        ,d_node_params=d_root_params
        ,od_rel_datacolumns=od_rel_datacolumns
        ,output_folder=output_folder
        ,od_parent_index=od_parent_index
        ,node_index=node_index
        ,node=doc_root
        ,d_xml_params=d_xml_params
        ,verbosity=verbosity
        )
    return log_messages
# end def rdb_to_xml():

'''
Method xml_paths_rdb():
Loop through all the input xml files in a slice of the input_path_list,
and call rdb_to_xml to create relational database table output rows
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
    , verbosity=0
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
    if (verbosity > 0):
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
            if verbosity > 0:
              # This clause used for testing only...
              msg =  "Max number of {} files processed. Breaking.".format(i)
              log_messages.append(msg)
            break

        file_count = file_count_first + i + 1

        # Full absolute path of input file name is:
        input_file_name = "{}/{}".format(path.parents[0], path.name)
        if verbosity > 0:
            print("{}:Reading file {} with file_count={}"
                 .format(me,input_file_name,file_count))
        batch_size = 250
        if batch_size > 0  and (i % batch_size == 0):
            progress_report = 1
        else:
            progress_report = 0

        if (progress_report):
            utc_now = datetime.datetime.utcnow()
            utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")
            msg = ("{}: At {}, processed through input file count = {} so far."
                   .format(me,utc_secs_z, file_count))
            print(msg)
            #log_messages.append(msg)
            # Flush all the output files in od_relation
            for relation, d_info in od_relation.items():
                file = d_info.get('db_file', None)
                if file is not None:
                    file.flush()

        # Try to read the article's input full-text xml file and accrue its statistics
        with open(str(input_file_name), "r", encoding='utf-8') as input_file:
            try:
                input_xml_str = input_file.read().replace('\n','')
                # print("### Got input_xml_str={}".format(input_xml_str))
            except Exception as e:
                if 1 == 1:
                    msg = ( "\tSkipping read failure {} for input_file_name={}"
                        .format(e,input_file_name))
                    print("{}:ERROR: {}".format(me,msg))
                    log_messages.append(msg)
                count_input_file_failures += 1
                continue
        if verbosity > 0:
            print("{}:Have read input file {} with length = {}"
                  .format(me,input_file_name,len(input_xml_str)))
        row_index += 1

        #Create an internal root document node to manage database outputs
        doc_root = etree.Element("doc")
        doc_root.attrib['file_name'] = input_file_name
        msg = ("{}:calling xml_rdb_doc with doc_root.tag={}, file_count={},verbosity={}"
          .format(me,doc_root.tag, file_count,verbosity))
        doc_root_tag = 'documen_root'
        tags = [doc_root_tag]

        if verbosity > 0:
            print("{}:{}".format(me,msg))

        sub_messages = xml_rdb_doc(tags=tags
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
    print ("{}:Finished processing through file_count={}".format(me,file_count))

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
            # print("WITH (FIELDTERMINATOR ='\\t', ROWTERMINATOR = '\\n');\n", file=sql_file)
            # Next works better -- else may get bulk insert error # 4866
            print("WITH (FIELDTERMINATOR ='\\t', ROWTERMINATOR = '0x0A');\n", file=sql_file)
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

If folder_output_base is None, then
the output folder is defined herein, but it may be promoted to a required argument soon.

These parameters may be re-grouped later into fewer parameters to more plainly separate
the three groups, each which contains sub-parameters for its group.
'''
def xml2rdb( input_path_list=None,
            folder_output_base=None,
            doc_root_xpath=None, rel_prefix=None,
            doc_rel_name=None, use_db=None,
            d_node_params=None, od_rel_datacolumns=None,
            d_params=None, file_count_first=0, file_count_span=1,
            d_xml_params=None,verbosity=0):
    me = "xml2rdb"
    utc_now = datetime.datetime.utcnow()
    utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")

    print("{}: STARTING at {}".format(me, utc_secs_z))

    if not (input_path_list
            and (rel_prefix or rel_prefix == '')
            and doc_root_xpath and use_db and doc_rel_name
            and d_node_params and od_rel_datacolumns
            and d_params
            and d_xml_params is not None
            ):
        raise Exception('{}:bad args'.format(me))

    d_log = OrderedDict()

    if folder_output_base is None:
        # folder_output_base = input_folders + me + '/'
        folder_output_base = etl.data_folder(linux="/home/robert/", windows="U:/",
            data_relative_folder='data/outputs/xml2rdb')

    d_params['folder-output-base'] = folder_output_base
    os.makedirs(folder_output_base, exist_ok=True)

    # We also use secsz_start as part of a folder name, and windows chokes on ':', so use
    # all hyphens for delimiters
    secsz_start = utc_now.strftime("%Y-%m-%dT%H-%M-%SZ")

    # The output_folder encodes start time of run in its name.
    output_folder_secsz = '{}/{}'.format(folder_output_base, secsz_start)
    os.makedirs(output_folder_secsz, exist_ok=True)
    print("Using output folder={}"
          .format(output_folder_secsz))

    lil = len(input_path_list)
    print("Using total real input file count={}"
          .format(lil))

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

    #os.makedirs(output_folder_secsz, exist_ok=True)
    skip_extant = False
    d_params.update({
        'secsz-1-start': secsz_start
        ,'output-folder': output_folder_secsz
        ,'input-files-index-limit-1-low': repr(input_low_index)
        ,'input-files-index-limit-2-high': repr(input_high_index)
    })

    d_log['run_parameters'] = d_params

    #### Open all the output files for all the relations... ####

    ################# READ THE INPUT, AND COLLECT AND OUTPUT STATS ################

    count_input_file_failures = xml_paths_rdb(
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
      , verbosity=verbosity
      , d_xml_params=d_xml_params
    )
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

def run(study=None):
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
    me = 'run'
    # Study choices
    study_choices = [
     'ccila'
     , 'citrus'
     , 'crafa'
     , 'crafd' # Crossreff affiliation filter where D here is for Deposit Date.
     , 'crawd' # Crossref filter where D is for doi
     , 'elsevier'
     , 'entitlement' # Elevier entitlment data.
     , 'merrick_oai_set'
     , 'oadoi'
     , 'orcid'
     , 'scopus'
    ]

    if study not in study_choices:
        raise ValueError("Unknown study='{}'".format(repr(study)))

    # KEEP ONLY ONE LINE NEXT: Study Selection
    study = 'crafd' # Crossreff affiliation filter where D here is for Deposit Date.

    file_count_first = 0
    file_count_span = 0
    use_db = 'silodb'

    #folders_base = etl.home_folder_name() + '/'
    data_elsevier_folder = etl.data_folder(linux='/home/robert/', windows='U:/',
            data_relative_folder='data/elsevier/')

    d_xml_params = {}
    # Part of a deprecation... now only marcxml uses this and passes it to xml2rdb,
    # So value of None is signal to interpret arguments an 'older' way.
    folder_output_base = None

    if study == 'crafa':
        import xml2rdb_configs.crossref as config
        # Note- input folder is/was populated via program crafatxml
        rel_prefix = 'y2016_'
        # All files under the input folder selected for input_path_list below will be used as input
        input_folder = '{}/output_crafatxml/doi/2016'.format(input_folders_base)
        input_folder = etl.home_relative_folder('/output_crafatxml/doi/2016')
        doc_rel_name = 'cross_doi' # must match highest level table dbname in od_rel_datacolumns
        #doc_root_xpath = './crossref-api-filter-aff-UF' #this matches root node assignment in crafatxml program
        doc_root_xpath = './crossref-api-filter-aff-UF/message'
        input_path_list = list(Path(input_folder).glob(input_path_glob))
        input_path_list = list(Path(input_folder).glob('**/doi_*.xml'))
        print("STUDY={}, got {} input files under {}"
              .format(study, len(input_path_list),input_folder))
        # Get SQL TABLE PARAMS (od_rel_datacolumns) and MINING MAP PARAMS
        od_rel_datacolumns, d_node_params = config.sql_mining_params()
        file_count_first = 0
        file_count_span = 0

    elif study in [ 'ccila' ] : #ccila is cuban collection i? latin america
        import xml2rdb_configs.marcxml as config
        rel_prefix = 'ccila_'

        # This is where the precursor program marc2xml leaves its marcxml data for ccila UCRiverside
        # items
        in_folder_name = etl.data_folder(linux='/home/robert/',
            windows='U:/', data_relative_folder='data/outputs/marcxml/UCRiverside/')

        folder_output_base = etl.data_folder(linux='/home/robert/',
            windows='U:/', data_relative_folder='data/outputs/xml2rdb/UCRiverside')

        input_folder = in_folder_name
        input_folders = []
        input_folders.append(input_folder)
        input_path_glob = '**/marc*.xml'

        doc_rel_name = 'record' # must match highest level table dbname in od_rel_datacolumns
        doc_root_xpath = ".//{*}record"

        input_path_list = list(Path(input_folder).glob(input_path_glob))
        d_xml_params['attribute_text'] = 'text'

        print("STUDY={}, got {} input files under {}"
              .format(study, len(input_path_list),input_folder))
        # Get SQL TABLE PARAMS (od_rel_datacolumns) and MINING MAP PARAMS
        od_rel_datacolumns, d_node_params = config.sql_mining_params()
        file_count_first = 0
        file_count_span = 0

    elif study in [ 'entitlement' ] : #
        import xml2rdb_configs.entitlement as config
        rel_prefix = 'enttl_'

        # This is where the precursor program marc2xml leaves its marcxml data for ccila UCRiverside
        # items
        in_folder_name = etl.data_folder(linux='/home/robert/', windows='U:/'
            , data_relative_folder='data/elsevier/output_entitlement/')

        folder_output_base = etl.data_folder(linux='/home/robert/', windows='U:/'
            , data_relative_folder='data/outputs/xml2rdb/entitlement/')

        input_folder = in_folder_name
        input_folders = []
        input_folders.append(input_folder)
        input_path_glob = 'pii*.xml'

        doc_rel_name = 'entitlement' # must match highest level table dbname in od_rel_datacolumns
        doc_root_xpath = ".//{*}document-entitlement"

        input_path_list = list(Path(input_folder).glob(input_path_glob))
        d_xml_params['attribute_text'] = 'text'

        print("STUDY={}, got {} input files under {}"
              .format(study, len(input_path_list),input_folder))
        # Get SQL TABLE PARAMS (od_rel_datacolumns) and MINING MAP PARAMS
        od_rel_datacolumns, d_node_params = config.sql_mining_params()
        file_count_first = 0
        file_count_span = 0
    elif study == 'crawd': # CrossRefApi Works by Doi-list
        import xml2rdb_configs.crossref as config
        # Note- input folder is/was populated via program crawdxml- where crawdxml
        # gets Works Dois MD for 'new' uf articles as found by diffing a week to
        # week SCOPUS harvest # of UF-affiliated dois/articles
        rel_prefix = 'crawd_' # maybe try wd_ as a prefix sometime
        input_folder = '{}/output_crawdxml/doi'.format(data_elsevier_folder)
        doc_rel_name = 'cross_doi' # must match highest level table dbname in od_rel_datacolumns
        doc_root_xpath = './response/message'
        input_path_list = list(Path(input_folder).glob('**/doi_*.xml'))
        print("STUDY={}, got {} input files under {}"
            .format(study, len(input_path_list),input_folder))
        # Get SQL TABLE PARAMS (od_rel_datacolumns) and MINING MAP PARAMS
        od_rel_datacolumns, d_node_params = config.sql_mining_params()
        file_count_first = 0
        file_count_span = 0

    elif study == 'crafd': # CrossRefApi filter by D for deposit date (and it selects only UF affiliations)
        import xml2rdb_configs.crossref as config
        # Note- input folder is/was populated via program crafdtxml
        rel_prefix = 'crafd2017_'
        # NOTE LIMIT INPUT FOLDER for now...
        input_folder = '{}/output_crafdtxml/doi/2017/06/23'.format(data_elsevier_folder)
        input_folders = [ input_folder ]
        input_path_glob = 'doi_*.xml'
        doc_rel_name = 'cross_doi' # must match highest level table dbname in od_rel_datacolumns, set below.
        #Next doc_root_xpath is set by the harvester crafdtxml so see its code.
        doc_root_xpath = './crossref-api-filter-date-UF/message'

        input_path_list = list(Path(input_folder).glob('**/doi_*.xml'))
        print("STUDY={}, got {} input files under {}"
              .format(study, len(input_path_list),input_folder))
        # Get SQL TABLE PARAMS (od_rel_datacolumns) and MINING MAP PARAMS
        od_rel_datacolumns, d_node_params = config.sql_mining_params()
        file_count_first = 0
        file_count_span = 0

    elif study == 'elsevier':
        import xml2rdb_configs.elsevier as config

        file_count_first = 0
        file_count_span = 0
        input_path_glob = '**/pii_*.xml'

        rel_prefix='e2016b_'
        # Set input folders to 'orig load date' to capture recent years through 20170824,
        # that is, the latest elsevier harvest to date.
        rel_prefix='e2017b_'

        input_folders = []
        for year in range(2010, 2018):
            input_folders.append('{}/output_ealdxml/{}/'.format(data_elsevier_folder,year))

        doc_rel_name = 'doc'
        doc_root_xpath = './{*}full-text-retrieval-response'

        # Get SQL TABLE PARAMS (od_rel_datacolumns) and MINING MAP PARAMS
        od_rel_datacolumns, d_node_params = config.sql_mining_params()
    elif study == 'scopus':
        import xml2rdb_configs.scopus as config
        rel_prefix = 'h5_' #h5 is harvest 5 of 20161202
        rel_prefix = 'h6_' #h6 is harvst 6 of 20161210 saturday
        rel_prefix = 'h7_' #h7 is 20161216 friday
        rel_prefix = 'h8_' #h8 is 20161223 friday - not run
        rel_prefix = 'h9_' #h9 is 20161230 friday - not run
        rel_prefix = 'h2016_10_' #h2016 is for query pubyear 2016, 10 is for harvest 10 done on 20170106 friday

        rel_prefix, year = ('h201709_', '2017')

        # Year 2016 input
        input_folder = '{}/output_satxml/{}/doi'.format(data_elsevier_folder,year)

        input_path_list = list(Path(input_folder).glob('**/doi_*.xml'))

        doc_rel_name = 'scopus'
        doc_root_xpath = './{*}entry'
        od_rel_datacolumns, d_node_params = config.sql_mining_params()

    elif study == 'oadoi':
        import xml2rdb_configs.oadoi as config
        # for 20161210 run of satxml(_h6) and oaidoi - c:/rvp/elsevier/output_oadoi/2016-12-10T22-21-19Z
        # for 20170308 run using dois from crafd_crawd for UF year 2016

        input_folder =  data_elsevier_folder + "/outputs/oadoi/"
        input_folders = [input_folder]
        input_path_glob = '**/oadoi_*.xml'
        input_path_list = list(Path(input_folder).glob(input_path_glob))

        print("Study oadoi, input folder={}, input path glob={}, N input files={},"
              " data_elsevier_folder = {}"
              .format(input_folder,input_path_glob,len(input_path_list),data_elsevier_folder))

        # rel_prefix 'oa2016_' is used because the oaidoi precursor process to produce the dois input list
        # was run on scopus dois fo/der uf authors from year 2016... should probably change prefix to oa_scopus2016_
        # input_folder = '{}/output_oadoi/2016-01-10T12-54-23Z'.format(data_elsevier_folder)
        rel_prefix = 'oa_cruf2016_'
        doc_rel_name = 'oadoi'
        doc_root_xpath = './{*}entry'
        od_rel_datacolumns, d_node_params = config.sql_mining_params()

    elif study == 'orcid':
        import xml2rdb_configs.orcid as config
        #for 20161210 run of satxml(_h6) and oaidoi - c:/rvp/elsevier/output_oadoi/2016-12-10T22-21-19Z
        #input_folder = '{}/output_oadoi/2017-01-10T12-54-23Z'.format(data_elsevier_folder)
        # for 20170308 run using dois from crafd_crawd for UF year 2016
        input_folder = '{}/output_orpubtxml'.format(data_elsevier_folder)
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
        od_rel_datacolumns, d_node_params = config.sql_mining_params()

    elif study == 'citrus':
        import xml2rdb_configs.citrus as config


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

        od_rel_datacolumns, d_node_params = config.sql_mining_params()
    elif study == 'merrick_oai_set':
        import xml2rdb_configs.merrick_oai_sets as config

        input_folder = etl.data_folder(linux='/home/robert/', windows='u:/',
            data_relative_folder='data/merrick_oai_set')
        input_folders = [ input_folder]
        input_path_glob = '**/*listsetspecs.xml'
        input_path_list = list(Path(input_folder).glob(input_path_glob))

        print("Study {}, input folder={}, input path glob={}, input files={}"
              .format(study, input_folder,input_path_glob,len(input_path_list)))
        input_path_list = list(Path(input_folder).glob(input_path_glob))
        rel_prefix = 'merrick_oai_'
        doc_rel_name = 'parent'
        #TODO: add batch id or dict column_constant to define column name and constant to insert in the
        # doc_rel_name table to hold hash for external grouping studies, repeated/longitutinal studies
        #raise Exception("Development EXIT")

        doc_root_xpath = './/{*}ListSets'
        d_xml_params['attribute_text'] = 'attribute_text'
        d_xml_params['attribute_innerhtml'] =  'attribute_innerhtml'

        od_rel_datacolumns, d_node_params = config.sql_mining_params()
    else:
        raise Exception("Study ={} is not valid.".format(repr(study)))

    # OPTIONAL - If a study specified multiple input folders and input_path_glob,
    # then honor them when constructing the input_path_list
    if (input_folders is not None and input_path_glob is not None):
        # compose input_path_list over multiple input_folders
        input_path_list = []
        for input_folder in input_folders:
            print("{}:Study {}:Using input_folder='{}'\n"
                .format(me,study,input_folder))
            input_path_list.extend(list(Path(input_folder).glob(input_path_glob)))

    # If input_folders not defined in a study, define it by putting the single input folder into this list
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
        ,'folder-output-base': repr(folder_output_base)
        ,'input-files-count': str(len(input_path_list))
        ,'file-count-first': file_count_first
        ,'file-count-span': file_count_span
        ,'folders_base': data_elsevier_folder
        ,'doc-rel-name': doc_rel_name
        ,'doc-root-xpath': doc_root_xpath
        ,'use-db': use_db
        ,'d-node-params': repr(d_node_params)
        ,'od-rel-datacolumns': repr(od_rel_datacolumns)
    })

    # RUN the analysis and collect stats
    log_filename, pretty_log = xml2rdb(
        input_path_list=input_path_list,
        folder_output_base=folder_output_base,
        doc_root_xpath=doc_root_xpath, rel_prefix=rel_prefix,
        doc_rel_name=doc_rel_name, use_db=use_db,
        d_node_params=d_node_params, od_rel_datacolumns=od_rel_datacolumns,
        d_params=d_params, file_count_first=file_count_first, file_count_span=file_count_span,
        d_xml_params=d_xml_params)

    print("Done.")
#end def run()
#
run('scopus')
