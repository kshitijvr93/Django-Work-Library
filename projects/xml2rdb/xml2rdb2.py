# xml2rdb-active
# Somewhat cleaned-up code with various debug statements and cruft removed
# to use as a supplement document for IP examination

'''
Program xml2rdb inputs xml docs from saved xml files (for example from the
Elsevier Publisher's
full-text api).
Each input xml file has xml-coded information pertaining to a single xml
document.
'''
import sys, os, os.path, platform

def register_modules():
    platform_name = platform.system().lower()
    if platform_name == 'linux':
        modules_root = '/home/robert/'
        #raise ValueError("MISSING: Enter code here to define modules_root")
    else:
        # assume rvp office pc running windows
        modules_root="C:\\rvp\\"
    sys.path.append('{}git/citrus/modules'.format(modules_root))
    return
register_modules()

import etl
from pathlib import Path
from collections import OrderedDict

import datetime
import pytz
import hashlib

from lxml import etree
from lxml.etree import tostring

'''
    Note: I also envision a revision of this program to do an initial
    walk-through of the xml input files.
    From that, it could:
    * register the repeat vs non-repeat nature of every xml tag, and thus be
      able to derive a complete set of SQL tables, or candidate tables,
      efficiently and automatically promoting non-repeated child
      elements/fields to parent relation attributes
    * Allow the user to select a subset of tables and columns within them as
      well from that 'full schema'
    * register the mapping-converson functions that a user provides and make
      suggestions or derive function candidates for translations from which
      the user may also choose.

    * derive a complete set of SQL tables, infer and define the entire
    hierarchical structure, and glean all of the XML input into relational
    tables for a consistent set of structured XML files.

    It will infer names for tables and columns from the xml tags and attribute
    names as well.

    However the user configuration will remain useful mainly to simplify and
    target creation of SQL data to simplify and abbreviate the outputted SQL
    database.
    That would make some studies easier to follow and faster to create and run
    selected sub-analyses of the entire pool of xml data.
'''

'''
Typical call: Caller will usually provide arg1 as its locals() dict to
check for provision of its required arguments by its own caller.
Where a function requires argument names 'd_oai' and 'output_folder'
one of its first code lines would be:

      require_arg_names(locals(), ['d_oai', 'output_folder'])
'''
def require_arg_names(d_caller_locals, names):
    required_args = [ v for k, v in d_caller_locals.items() if k in names]
    if not all(required_args):
          raise ValueError(
             f"Error: Some required variables in {names!r} not set.")

'''
DocNodeSet instantiates a description of documents to use as input.
Its method generator_doc_nodes creates a generator of a sequence
of lxml document root nodes, where each is to an input document to be
processed.
'''
class DocNodeSet():
    def __init__(self, input_folders=None, input_file_glob=None,
        progress_batch_size=1000,
        doc_root_tag="Thesis",
        attribute_text = 'text',
        attribute_innerhtml = '',
        input_glob = '**/*.xml',
        verbosity=0):

        self.input_folders = input_folders
        self.input_glob = input_glob
        self.input_path_list = []
        for input_folder in input_folders:
            self.input_path_list += list(Path(input_folder).glob(input_file_glob))
        self.progress_batch_size = progress_batch_size
        # Upon parsing, converting input xml to rdb, use this as the
        # 'pseudo attribute name' for the text content of any doc node
        self.attribute_text = attribute_text

        # Similar, but for innerhtml of a doc node? output? maybe dicard this.
        self.attribute_innerhtml = attribute_innerhtml
    #end def __init__
#end class DocNodeSet


    '''
    method: generator_doc_nodes
    create and return a generator for a sequence of doc_nodes

    Also, internally uses the glob.iglob generator instead of glob.globe so the
    entire input path list need not be generated first and stored in memory.

    max_test_nodes: if non-zero, generated sequence will end after max_test_nodes

    TODO: provide optional report of failed file reads and parses..
    See older version of xml2rdb code for prototype, messages to report.
    '''
    def generator_doc_nodes(self, max_text_nodes=0):
        return None

#end class DocNodeSet
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
properly populated with the parent relaton name values that assign the
composite primary key column names of the given db_name in the mining map's
hierarchy.

This information is given in the argument od_parent_index.

The actual index values are not important here, but the parent relation
names are important so that the primary key column names for them can be
assigned to the given db_name relation.
This need only be done once, and coincidentally, the writable file handle
for the relation need only be created once, and so it is also done within
this routine.

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

    if 1 == 2:
      print("\n\n===========================\n"
        "{}:NOTICE: For dbname={},writing output data with encoding='{}'"
        .format(me,db_name,repr(output_encoding)))
      print( "May need utf-8 encoding for XML outputs or may need latin-1 encoding"
             " for SQL SERVER 2008!'")

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
        od_rel_info['pkey_columns'] = pkey_columns

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
Method node_visit_output

Given node, the current node, and d_node_params, the 'mining map' starting
with the given node's entry in the mining map hierarchy, select the the
data input fields for this node.

If the node has a db_name (and/or a multiple=1 value, meaning multiple of
this node type is allowed to exist under the same parent),
the node represents a row in an sql relation:

So after visiting its children nodes (using each given child_xpath),
and getting their values via return value d_row, then we output a row for
this node.

Else, this node is not a db_name node, rather only one node of this type is
allowed under its parent node in the xml input document:

So this node is mined to garner input values into a
dictionary, d_row, to return to the parent node for its use.
'''

def node_visit_output(
    node=None, node_index=None, d_namespaces=None,
    d_node_params=None, od_rel_datacolumns=None, od_parent_index=None,
    od_relation=None, output_folder=None,d_xml_params=None,verbosity=0):

    me = 'node_visit_output()'
    verbose = 0
    if verbosity > 0:
        msg = ("{}:START: verbosity={},node.tag={}, node_index={}"
               .format(me, verbosity, node.tag, node_index))
        print(msg)
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
    attribute_innerhtml = d_xml_params.get('attribute_innerhtml',
        'attribute_innerhtml')
    # if 'multiple' not in d_node_params:
    #    raise RuntimeError("{}: multiple keyword missing for node.tag={}"
    #            .format(me,node.tag))
    # pass along the parent index - we will append our index below only if
    # multiple is 1
    od_child_parent_index = od_parent_index

    multiple = d_node_params.get('multiple', 0)
    if multiple is None:
        msg = ("{}:Node tag={}, index={},node multiple is None."
               .format(me,node.tag,node_index))
        raise Exception()
    if verbose > 0 and multiple == 0 and node_index > 1:
        # Solution: in d_node_params, change multiple =0, provide a db_name,
        # and also update
        # od_rel_datacolumns to include this db_name as a table if it does
        # not already appear there.
        print("WARN:{}: node.tag={} has multiple == 0 but node_index = {}"
                    .format(me,node.tag,node_index))
    if multiple != 0 and multiple != 1:
        raise Exception("{}: Multiple value='{}' is bad for db_name{}"
            .format(me,multiple,db_name))

    # We will put the data values of interest for this node into d_row.
    # d_row collects a dict of named data values for this node and is
    # returned to caller if this node has multiple indicator == 0.
    d_row = {}
    # d_attr_column: key is an attribute name and value is a relational column
    # name in which to outut the attribute value.
    # Because some attrib names have hyphens, this provides a way
    # that we can change the attribute name to a db column name, e.g, to
    # replace hyphens (that commonly appear in attribute names but are
    # disallowed in many rdbs in column names) with underbars (which are
    # commonly alowed in rdbs in column names).
    d_attr_column = d_node_params.get('attrib_column', None)
    if d_attr_column is not None:
        # We have some node attributes destined for output to relational columns,
        # so set them up in d_row key-value pairs.
        if not isinstance(d_attr_column, dict):
            # detect some sorts of errors/typos in the d_node_params parsing
            # configuration
            import types
            raise Exception(
              "d_attrib_column={},type={} not dict. node.tag={},node_index={}"
              .format(repr(d_attr_column),repr(type(d_attr_column)),
                node.tag, node_index))

        node_text = etree.tostring(node, encoding='unicode', method='text')
        # Must discard tabs, used as bulk load delimiter, else sql server 2008
        # bulk insert error
        # messages appear, numbered 4832 and 7399, and inserts fail.
        # also discard carriage returns - 20171117 from crossref in orcid ids
        node_text = (node_text.replace('\t',' ').replace('\r','')
            .replace('\n',' ').strip())
        #node_text = "" if stringify is None else stringify.strip()

        for attr_name, column_name in d_attr_column.items():
            # For every key in attr_column, if it is reserved name in
            # attribute_text, use the node's text value, else seek the key in
            # node.attrib and use its value.
            column_name = attr_name if column_name is None else column_name
            column_value = ''
            if attr_name == attribute_text:
                # Special reserved name in attribute_text: it is not really an
                # attribute name, but this indicates that we shall use the
                # node's content/text for this attribute
                column_value = node_text
            elif attr_name == attribute_innerhtml:
                # Special reserved name in attribute_text: it is not really
                # an attribute name, but this indicates that we shall use
                # the node's innerhtml value for this attribute
                column_value = etree.tostring(node, encoding='unicode')
            else:
                if attr_name in node.attrib:
                    # Clean the data values
                    column_value = (node.attrib[attr_name].replace('\t',' ')
                      .replace('\n',' ').replace('\r','').strip())

            if verbosity> 0:
                print("{}:setting d_row for column_name={} to value={}"
                    .format(me,column_name,column_value))
            d_row[column_name] = column_value
    # When multiple is 1 we always stack a node index
    if multiple == 1:
        # Where multiple is 1, db_name is name of an output relation.
        db_name = d_node_params.get('db_name', None)
        if db_name is None:
            raise RuntimeError(
              "{}: db_name={}, db_name is not a key in d_node_params={}"
              .format(me, db_name, repr(d_node_params)))

        # This node has an output, so it must append its own index to copy of
        # od_child_parent_index and pass it to calls for child visits.
        od_child_parent_index = OrderedDict(od_parent_index)

        # Note: this next dup db_name check could be done once in
        # get_d_node_params(), but easy to put here for now
        if db_name in od_child_parent_index:
            raise Exception("{}:db_name={} is a duplicate in this path."
              .format(me,db_name))

        od_child_parent_index[db_name] = node_index

    ################# SECTION - RECURSE TO CHILD XPATH NODES ###############

    od_child_row = None
    d_child_xpaths = d_node_params.get('child_xpaths',None)

    if d_child_xpaths is not None:
        for xpath, d_child_node_params in d_child_xpaths.items():
            #print("{} seeking xpath={} with node_params={}"
            #  .format(me,repr(xpath),repr(d_child_node_params)))
            children = node.findall(xpath, d_namespaces )
            if (verbosity > 0):
                print("{}:for xpath={} found {} children"
                  .format(me,xpath,len(children)))
            # TODO:Future: may add a new argument for caller-object that
            # child may use to accumulate, figure, summary statistic
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
                    # Allowing this may be a feature to facilitate re-use of
                    # column functions
                    # TEST RVP 201611215
                    #if column_name in d_row:
                    #    raise Exception(
                    #        'node.tag={} duplicate column name {} is also '
                    #        'in a child xpath={}.'
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
        # as args all child data dict and the lxml node itself so such a
        # function has more to work with.
        for column_name, function in d_column_functions.items():
            if type(function) is types.FunctionType:
                # This function knows the d_row key(s) to use
                d_row[column_name] = function(d_row)
            else: # Assume types.TupleType of: (function, dict of params)
                # This function will find its arguments in the given dict
                # of function params
                d_row[column_name] = function[0](d_row, function[1])

    ####################### OUTPUT for MULTIPLE (== 1) NODES
    if multiple == 1:
        # For multiple == 1 nodes, we write an output line to the database
        # relation/table named by this node's 'db_name' value.
        db_file = get_writable_db_file(od_relation=od_relation,
            od_rel_datacolumns=od_rel_datacolumns,
            db_name=db_name, output_folder=output_folder,
            od_parent_index=od_parent_index)

        sep = ''
        db_line = ''
        #First, ouput parent indexes
        for parent_index in od_parent_index.values():
            db_line += ("{}{}".format(sep,parent_index))
            sep = '\t'
        # Now output this node's index
        # It identifies a row for this node.tag in this relation among all
        # rows outputted.
        # It is assigned by the caller via an argument, as the caller
        # tracks this node's count/index value as it scans the input xml
        # document.

        db_line += ("{}{}".format(sep,node_index))

        # ##################  NOW, OUTPUT THE DATA COLUMNS ##################
        # For each field in d_row, put its value into od_column_values
        #
        od_column_default = od_rel_datacolumns[db_name]

        for i,(key,value) in enumerate(od_column_default.items()):
            # Note: this 'picks' the needed column values from d_row, rather
            # than scan the d_row and try to test that each is an
            # od_column_default key, by design.
            # This design allows the child to set up local d_row
            # attribute_column values with names other than those in
            # od_column_default so that the column_function feature may use
            # those 'temporary values' to derive its output to put into named
            # d_row entries.
            value = ''
            if key in d_row:
                value = d_row[key]
            db_line += ("\t{}".format(str(value).replace('\t',' ')))

        #Output a row in the db file
        print('{}'.format(db_line), file=db_file)

        ############################################################
        # Now that all output is done for multiple == 1, set d_row = None,
        # otherwise it's presence would upset the caller.
        d_row = None
    # end if multiple == 1

    msg = ("{}:FINISHED node.tag={}, node_index={}, returning d_row={}"
           .format(me, node.tag, node_index,repr(d_row)))
    #print(msg)
    return d_row
# def end node_visit_output

# { def generate_doc_root_nodes
'''
def generator_doc_root_nodes(
   input_file_name=None, root_item_tag=None
    log_file=None, verbosity=0):

Generate a generator/sequence,
given an input file name, and string root_item_tag that defines the tag
for a doc_root_node in the file. Each sequence iteration yields
    the lxml doc root node for the next successive input
    lines that comprise a document in the input file.

Return null if:

(1) no line left in input file, or
(2) the next line does not begin with the <root_item_tag>

Buffer input lines into a string and keep reading until:
case: an end of file,
   in which case return null
case: an </root_item_tag> is found
   in which case
   - parse the input lines buffer into an lxml doc,
   - yield the root node of the lxml doc

'''
def generator_doc_root_nodes(
    input_file_name=None,
    root_item_tag=None,
    log_file=None,
    verbosity=0):

    me = 'generator_doc_root_nodes'
    seq = 'sequence_doc_root_nodes'
    node = None
    lines = ''

    with open(input_file_name,mode="r") as input_file:
        line = input_file.readline()
        if verbosity > 0:
            print(f"{me}: Got first input line='{line}'")
        start_str =f"<{root_item_tag}"
        if not line.startswith(sw):
            if verbosity > 0:
                print(
                  f"{me}:Error: line  '{line}' does not startwith '{start_str}'")
            return None
        lines += line
        end_str =f"</{root_item_tag}"
        for line in input_file:
            if verbosity > 1:
                print(f"{seq}: Got input line='{line}'")
            lines += line
            if line.startswith(end_str):
                #Parse the lines buffer as xml and return the item node
                if verbosity > 1:
                    print(f"{seq}: Made all lines='{lines}'")
                node_root = etree.fromstring(str.encode(lines))
                yield node_root

        #if we got here this is premature end of file
        # should never happen with automated inputs, just print it if it does
        print( f"{me}: premature end of input file {input_file}, lines={lines}")
        return None
    # end with open
    # normal end of file
    return None
# } end def generator_doc_root_nodes


'''
Method xml_doc_rdb2:
From given xml doc(eg, from a arg of input_root_node, for example an Elsevier
full text retrieval apifile),
convert the xml doc for output to relational data and output to relational
tab-separated-value (tsv) files.
Excel and other apps allow the '.txt' filename extension for
tab-separated-value files.

20180923 TODO: make sure the parent caller's input root node generator
increments doc_count variable properly, returns what it needs for next call
to this ...
'''
def xml_doc_rdb2(
    input_root_node=None,
    doc_count=None,
    od_relation=None,
    output_folder=None,
    doc_rel_name=None,
    doc_root=None, # IGNORE - we create our own in this modified method
    doc_root_xpath=None,
    d_node_params=None,
    od_rel_datacolumns=None,
    d_root_node_params=None,
    d_xml_params=None,
    # todo?:
    #   We also will add a naturally useful row offset integer paramemter:
    #   If user intends to append extant data tables with the rows in the output data,
    #   USER IS RESPONSIBLE to set row offset to beyond the highest
    #   offset in the root table to which to append these rows.
    #   With a proper offset row integer, all outputted tables data files
    #   will be also suitable to be appended to their respective DB tables. The user is responsible for
    #   creating the SQL to do this, at this point.
    load_name=None, # A name to apply to this load group-segment of outputted  rows.
    verbosity=0,):

    me = 'xml_doc_rdb2'
    log_messages = []
    need_args=['input_root_node', 'doc_count','output_folder', 'd_node_params',
      'd_xml_params','od_rel_datacolumns', 'doc_rel_name','doc_root_xpath',
      'od_relation'
      ]
    require_arg_name(locals(), arg_names=need_args)
    msg = f"{me}:Starting..."
    log_messages.append(msg)

    # Review this check...?
    if load_name is not None:
        msg = (
          f"{me}:Warning: User must add column names 'load' and 'file_name' to "
          "the root table\n"
          "to enable their values to be output in the output data")
        print(msg)
        log_messages.append(msg)
    else:
        load_name = ""

    # document root params
    # Note... may want to add check that NO rows with this load_name exist
    # in the main doc table before allowing any proessing, creating any new
    # rows in this set of outputs for that table; because passing this
    # validation is required for the main is the purpose of
    # supporting the load names.
    d_root_params = {
        'db_name': doc_rel_name, 'multiple':1,
        'attrib_column': {
            'file_name':'file_name',
            'load': load_name,
        },
        'child_xpaths':{doc_root_xpath:d_node_params}
    }

    if verbosity > 1:
        msg = ("{}: Using db_name='{}', doc_count='{}'"
          .format(me, doc_rel_name , doc_count))
        log_messages.append(msg)
        print(msg)

    # Prepare internal doc_root node to also impart some run or batch-related
    # data settings for the output data
    input_root_node = doc_root_node
    d_nsmap = dict(input_node_root.nsmap)
    d_namespaces = {key:value
        for key,value in d_nsmap.items() if key is not None}
    # We must create a separate doc root for every doc input root node
    doc_root = etree.Element("doc")
    doc_root.append(input_node_root)

    doc_root.attrib['file_name'] = "no_file_name"
    doc_root.attrib['load_name'] = 'some_load_name'

    od_parent_index = OrderedDict()

    # In this scheme, the root node always has multiple = 1
    # that is, it may have multiple occurences, specifically,
    # over the set of potentially multiple input xml documents.
    # Also, this program requires that this augmented doc_root
    # be included in the relational output files.
    multiple = 1
    d_row = node_visit_output(
          od_relation=od_relation
         ,d_namespaces=d_namespaces
         ,d_node_params=d_root_params
         ,od_rel_datacolumns=od_rel_datacolumns
         ,output_folder=output_folder
         ,od_parent_index=od_parent_index
         ,node_index=doc_count
         ,node=doc_root
         ,d_xml_params=d_xml_params
         ,verbosity=verbosity
         )

    # end for input_root node in seq_doc_root_nodes
    return log_messages
# end def xml_doc_rdb2:

'''
<summary> Method xml_paths_rdb():

Loop through all the input xml files in a slice of the input_path_list,
and call xml_doc_rdb to create relational database table output rows
for each input xml doc.

    , doc_root_xpath=None #xml tag that is used as document root
    , rel_prefix=None  # Prefix string for all relatinship names
//summary>

'''
def xml_paths_rdb(
    sequence_doc_nodes=None,
    doc_root_xpath=None,
    rel_prefix=None,
    doc_rel_name=None,
    d_node_params=None,
    od_rel_datacolumns=None,
    output_folder=None,
    use_db=None,
    verbosity=0,
    d_xml_params=None,
    ):

    me = "xml_paths_rdb"
    need_args=[
      'sequence_doc_nodes'
      'doc_xroot_path',
      'rel_prefix',
      'd_node_params',
      'doc_rel_name',
      'od_rel_datacolumns',
      'output_folder',
      'use_db',
      'd_xml_params'
      ]
    require_arg_name(locals(), arg_names=need_args)

    log_messages = []
    msg = (f"{me}:STARTING...")
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

    doc_count = 0
    dns = doc_node_set
    sequence_doc_nodes = dns.generator_doc_nodes
    max_nodes = dns.max_test_nodes
    progress_batch_size = dns.progress_batch_size

    for doc_node in sequence_doc_nodes:
        doc_count += 1
        if (max_nodes > 0) and ( doc_count >= max_nodes):
            if verbosity > 0:
              # This clause used for testing only...
              msg =  "Max number of {} files processed. Breaking.".format(i)
              log_messages.append(msg)
            break
        if batch_size > 0  and (doc_count % progress_batch_size == 0):
            progress_report = 1
        else:
            progress_report = 0

        if (progress_report):
            utc_now = datetime.datetime.utcnow()
            utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")
            msg = (
              "{}: At {}, processed through input document count = {}."
                   .format(me,utc_secs_z, file_count))
            print(msg, flush=True)
            #log_messages.append(msg)
            # Flush all the output files in od_relation
            for relation, d_info in od_relation.items():
                file = d_info.get('db_file', None)
                if file is not None:
                    file.flush()
            #end for relation
        #end if progress_report

        ############################0

        if verbosity > 0:
            print(f"{me}:Using doc count {doc_count}, call xml_doc_rdb2:")

        sub_messages = xml_doc_rdb2(
            doc_count=doc_count,
            input_root_node=doc_node,
            od_relation=od_relation,
            output_folder=output_folder,
            doc_rel_name=doc_rel_name,
            doc_root=doc_root,
            doc_root_xpath=doc_root_xpath,
            d_node_params=d_node_params,
            od_rel_datacolumns=od_rel_datacolumns,
            verbosity=verbosity,
            d_xml_params=d_xml_params,
            )

        if len(sub_messages) > 0 and False:
            log_messages.append({'xml_doc_rdb2_return_value:sub_messages})
    # end for doc_node in sequence_doc_nodes:

    msg = ("{}:Finished doc count={} input documents"
        .format(me,doc_count), flush=True)
    print (msg, flush=True)

    log_messages.append(msg)
    print(msg)

    #### CREATE THE RDB INSERT COMMANDS - HERE USING SQL THAT WORKS WITH
    # MSOFT SQL SERVER 2008, maybe 2008+

    # For MSSQL or SQL SERVER databases
    sql_filename = "{}/sql_server_creates.sql".format(output_folder)
    use_setting = 'use [{}];\n'.format(use_db)

    # MYSQL databases
    mysql_filename = "{}/mysql_creates.sql".format(output_folder)
    psql_filename = "{}/psql_creates.sql".format(output_folder)

    with open(sql_filename, mode='w', encoding='utf-8') as sql_file, \
      open(mysql_filename, mode='w', encoding='utf-8') as mysql_file, \
      open(psql_filename, mode='w', encoding='utf-8') as psql_file:

        print(use_setting, file=sql_file)

        # BEGIN/START TRANSACTION DB VERSIONS
        print('begin transaction;', file=sql_file)
        print('start transaction;', file=mysql_file)
        print('start transaction;', file=psql_file)
        for rel_key, d_relinfo in od_relation.items():
            #Insert a '_' separator after rel_prefix for clarity in table name.
            relation = '{}_{}'.format(rel_prefix,rel_key)

            # { DROP TABLE DB VERSIONS
            # MSSQL
            print(
              "IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES"
              " WHERE TABLE_NAME = '{}') TRUNCATE TABLE {}"
              .format(relation,relation), file=sql_file)

            print(
               "IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES"
               " WHERE TABLE_NAME = '{}') drop table {}"
               .format(relation,relation), file=sql_file)

            # MySQL
            print("DROP TABLE IF EXISTS {};"
              .format(relation,relation), file=mysql_file)

            # psql
            print("DROP TABLE IF EXISTS {};"
              .format(relation,relation), file=psql_file)
            # }

        # CREATE TABLE - DB VERSIONS
        for rel_key, d_relinfo in od_relation.items():
            relation = '{}_{}'.format(rel_prefix,rel_key)

            # The tsf_filename is one line of comma-separated field names
            # which are useful to csv DictReader follow-on processes
            tsf_filename = "{}/{}.tsf".format(output_folder,rel_key)
            tsf_file = open(tsf_filename, mode='w', encoding='utf-8')

            #print("{}: Table {}, od_relation has key={}, value of d_relinfo with its keys={}"
            #      .format(me, relation, rel_key, repr(d_relinfo.keys())))
            if 'attrib_column' not in d_relinfo:
                print("{}: WARNING: Table {} has keys={}, but no values for it in current "
                    "file were found.".format(me,relation,repr(d_relinfo.keys())))
                continue

            # CREATE SYNTAX FOR COLUMNS
            print('create table {}('.format(relation), file=sql_file)
            print('create table {}('.format(relation), file=mysql_file)
            print('create table {}('.format(relation), file=psql_file)

            d_column_type = d_relinfo['attrib_column']
            # Create serial number, sn column for every table
            # print('sn int not null identity(1,1)', file=sql_file)
            tsep = sep = ''
            #print("{}:Getting columns for relation '{}'".format(me,relation))
            if d_column_type is None:
                tsf_file.close()
                raise Exception("Table {}, d_column_type is None"
                    .format(relation))

            key_columns = d_relinfo['pkey_columns'].split(',')

            #print("Got key_columns={}".format(repr(key_columns)))

            for i,(column, ctype) in enumerate(d_column_type.items()):
                #print("Column index {}".format(i))
                import sys
                sys.stdout.flush()
                #print("Column = {}.{}".format(relation,column))

                if ctype is None:
                    raise Exception("Table {}, column {} ctype is None".format(relation,column))
                if column is None:
                    raise Exception("Table {} has a None column".format(relation))

                # HIERARCHICAL KEY COLUMNS - DB VERSIONS
                if column in key_columns:
                    for file in [sql_file,mysql_file,psql_file]:
                      print('{}{} integer'.format(sep,column.replace('-','_'))
                          ,file=file)
                else:

                    # DATA COLUMNS - DB VERSIONS
                    data_column_tuples = [
                        (sql_file, 'nvarchar(4555)'),(mysql_file,'text'),
                        (psql_file,'text')]

                    for dct in data_column_tuples:
                        print('{}{} {}'
                            .format(sep,column.replace('-','_'),dct[1])
                            ,file=dct[0])

                # Done: wrote line to define this column

                # Build the tab-separated fieldnames (tsf) file,
                # hence extension tsf, by printing this column name
                print('{}{}'.format(tsep,column.replace('-','_'))
                      ,file=tsf_file, end='')

                tsep = '\t'
                sep = ','
            # end loop over relation column ddl outputs
            print('', file=tsf_file)
            tsf_file.close()

            # UNIQUE CONSTRAINT FOR COMPOSITE KEY (pkey) COLUMNS

            # FOR MSSQL use a PRIMARY KEY
            # eg: CONSTRAINT pk_PersonID PRIMARY KEY (P_Id,LastName)
            print(
              'CONSTRAINT pk_{} PRIMARY KEY({})'
              .format(relation, d_relinfo['pkey_columns']) , file=sql_file)

            # FOR MYSQL UNIQUE KEY COLUMNS, BELOW WE WILL
            # use alter table

            # FOR POSTGRES SQL
            # End table ddl and create index
            print(');', file=psql_file)
            print(
              'create index {}_UXK on {}({});'
              .format(relation, relation, d_relinfo['pkey_columns'])
              , file=psql_file)

            #End table schema definition for DB VERSIONS
            print(');', file=sql_file)
            print(');', file=mysql_file)


        # WRITE BULK INSERTS STATEMENT and new column SN TO SQL_FILE

        for rel_key, d_relinfo in od_relation.items():
            # Prepend the prefix to make this table/relation name.
            relation = '{}_{}'.format(rel_prefix,rel_key)

            # Bulk insert processing for MSSQL
            print("\nBULK INSERT {}".format(relation), file=sql_file)
            print("FROM '{}{}.txt'".format(output_folder,rel_key), file=sql_file)
            # NOTE: this failed: ROWTERMINATOR = '\\n'
            # Next works fine -- else may get bulk insert error # 4866
            print("WITH (FIELDTERMINATOR ='\\t', ROWTERMINATOR = '0x0A');\n",
              file=sql_file)

            # Bulk insert processing for MySQL
            #Per SO posts for MYSL need "LOCAL" to read network drives
            print("\nLOAD DATA LOCAL INFILE '{}{}.txt'".format(output_folder, rel_key),
               file=mysql_file)
            print("INTO TABLE {}".format(relation), file=mysql_file)
            print("CHARACTER SET latin1 FIELDS TERMINATED BY '\\t'", file=mysql_file)
            # MySQL chokes on hex notation REQUIRED by mssql, so
            # here use '\\n'
            print("LINES TERMINATED BY '\\n';", file=mysql_file)

            #BULK INSERT PROCESSING FOR psql

            #copy tmpt1 from '/home/robert/tmpf.txt' ( FORMAT CSV, DELIMITER(E'\t') );
            print("\nCOPY {} FROM '{}{}.txt'"
               .format(relation, output_folder, rel_key), file=psql_file)
            print("( FORMAT CSV, DELIMITER(E'\\t') );", file=psql_file)

            # print("CHARACTER SET latin1 FIELDS TERMINATED BY '\\t'", file=mysql_file)

            # END TABLE BULK INSERTS/LOADING ROW STATEMENTS IN EACH DB

            # ADD SN COLUMN FOR DB VERSIONS
            # ADD SN FOR DB MSSQL
            print("ALTER TABLE {} ADD sn INT IDENTITY;"
                  .format(relation), file=sql_file)
            print("CREATE UNIQUE INDEX ux_{}_sn on {}(sn);"
                  .format(relation,relation), file=sql_file)

            # ADD SN FOR DB MySQL, BUT FIRST CREATE UNIQUE INDEX FOR KEYS
            # MYSQL - we had to reserve the primary key for the SN
            # add-on column due to MySQL constraints, so since earlier
            # we did NOT create a primary key for them, here we
            # add a unique index on the composite
            # hierarchical columns for fast queries
            print("CREATE UNIQUE INDEX ux1_{} ON {}({});"
                  .format(relation,relation,d_relinfo['pkey_columns']),
                  file=mysql_file)

            print(
                "ALTER TABLE {} ADD sn "
                "INT PRIMARY KEY NOT NULL AUTO_INCREMENT;"
                .format(relation), file=mysql_file)

            print("CREATE UNIQUE INDEX ux_{}_sn on {}(sn);"
                  .format(relation,relation), file=mysql_file)

            # ADD SN FOR DB POSTGRES SQL
            print("ALTER TABLE {} ADD sn SERIAL PRIMARY KEY;"
                  .format(relation), file=psql_file)

            # end statements for bulk insert for this relations
        # end relations loop statements for bulk inserts

        #FINAL COMMIT FOR DB VERSIONS
        print("\nCOMMIT TRANSACTION;", file=sql_file)
        print("\nCOMMIT;", file=mysql_file)
        print("\nCOMMIT;", file=psql_file)
    # end 'with opens' loop over db versions

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

def name_output_folder(output_folder_name=''):
    return output_folder_name

'''
xml2rdb is the main method.

It accepts three main groups of input parameters:
(1) DocRootSet to iterate through group of input xml documents to read
(2) to define the SQL schema for tables and columns to be outputted
(3) to define the mining map that associates table and column names with
    target nodes (designated by child xpath expressions) and their values in
    each inputted xml file.

If folder_output_base is None, then
the output folder is defined herein, but it may be promoted to a required
argument.

These parameters may be re-grouped later into fewer parameters to more
plainly separate the three groups, each which contains sub-parameters for
its group.
'''
def xml2rdb(
        sequence_doc_nodes=None,
        # input_path_list=None,
        file_count_first=0, file_count_span=1,
        doc_root_xpath=None,
        folder_output_base=None,
        output_folder_include_secsz=True,
        rel_prefix=None,
        doc_rel_name=None, use_db=None,
        d_node_params=None, od_rel_datacolumns=None,
        d_params=None,
        d_xml_params=None, verbosity=0):
    me = "xml2rdb"
    utc_now = datetime.datetime.utcnow()
    utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")

    print("{}: STARTING at {}".format(me, utc_secs_z))

    if not (1 == 1
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
        folder_output_base = etl.data_folder(linux="/home/robert/",
            windows="U:/", data_relative_folder='data/outputs/xml2rdb/{}/'
            .format(rel_prefix))

    d_params['folder-output-base'] = folder_output_base
    os.makedirs(folder_output_base, exist_ok=True)

    # We also use secsz_start as part of a folder name, and windows chokes
    # on ':', so use all hyphens for delimiters
    secsz_start = utc_now.strftime("%Y-%m-%dT%H-%M-%SZ")

    # The output_folder encodes start time of run in its name.
    # later
    if output_folder_include_secsz:
        output_folder_final = '{}/{}'.format(folder_output_base, secsz_start)
    else:
        output_folder_final = folder_output_base

    os.makedirs(output_folder_final, exist_ok=True)
    print("Using output folder={}"
          .format(output_folder_final))

    d_params.update({
        'secsz-1-start': secsz_start
        ,'output-folder': output_folder_final
    })

    d_log['run_parameters'] = d_params

    ################# READ THE INPUT, AND COLLECT AND OUTPUT STATS ################

    count_input_file_failures = xml_paths_rdb(
      sequence_doc_nodes=sequence_doc_nodes,
      doc_root_xpath=doc_root_xpath,
      rel_prefix = rel_prefix,
      doc_rel_name = doc_rel_name,
      output_folder=output_folder_final,
      d_node_params=d_node_params,
      od_rel_datacolumns=od_rel_datacolumns,
      use_db=use_db,
      verbosity=verbosity,
      d_xml_params=d_xml_params,
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
    log_filename = '{}/log_xml2rdb.xml'.format(output_folder_final)
    with open(log_filename, mode='w', encoding='utf-8') as outfile:
        pretty_log = etree.tostring(e_root, pretty_print=True)
        outfile.write(pretty_log.decode('utf-8'))
    return log_filename, pretty_log
# end def xml2rdb

def run(study=None,rel_prefix='e2018_', verbosity=0):

    ''' SET UP MAIN ENVIRONMENT PARAMETERS FOR A RUN OF XML2RDB
    Now all these parameters are 'hard-coded' here, but they could go into
    a configuration file later for common usage.
    Better still, this would all be managed by a web-interface with xml2rdb
    as a back end.
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
     , 'crafd' # Crossref FILTER (by affiliation) where D here is for Deposit Date.
     , 'crawd' # Crossref WORKS where D is for doi
     , 'elsevier'
     , 'entitlement' # Elsevier entitlment data.
     , 'merrick_oai_set'
     , 'oadoi'
     , 'orcid'
     , 'scopus'
     , 'x2018' # a xis export of subject terms info for 29k etd items
    ]

    # Study selection KEEP ONLY ONE LINE next
    study = 'ccila'
    if study not in study_choices:
        raise ValueError("Unknown study='{}'".format(repr(study)))

    xfile_count_first = 0
    xfile_count_span = 0
    use_db = 'silodb'

    #folders_base = etl.home_folder_name() + '/'
    data_elsevier_folder = etl.data_folder(linux='/home/robert/', windows='U:/',
            data_relative_folder='data/elsevier/')

    d_xml_params = {}
    # Part of a deprecation... now only marcxml uses this and passes it to xml2rdb,
    # So value of None is signal to interpret arguments an 'older' way.
    folder_output_base = None
    output_folder_include_secsz = False

    if rel_prefix is None:
        # Define a redo_rel_prefix for this study
        rel_prefix = 'crawd2017b'
        rel_prefix = 'cr201711'
        rel_prefix = 'orcid'

        # Select the rel_prefix
        rel_prefix = 'orcid'
        rel_prefix = 'ccila'
        rel_prefix = 'e201710_17'
        rel_prefix = 'x2018'

    print("Using rel_prefix-'{}'".format(rel_prefix))

    if rel_prefix == 'crawd2017b':
        import xml2rdb_configs.crossref as config
        study = 'crawd'
        input_folder = 'u:/data/outputs/crawdxml/run/2017-11-16T15-41-59Z/doi'
        input_path_list = list(Path(input_folder).glob('**/doi_*.xml'))

        folder_output_base = etl.data_folder(linux='/home/robert/data/outputs/'
            , windows='U:/data/outputs/'
            , data_relative_folder='xml2rdb/{}/'.format(rel_prefix))


        # doc_rel_name must match highest level table dbname in sql_mining_params od_rel_datacolumns
        doc_rel_name = 'cross_doi'
        doc_root_xpath = './response/message'

        print("STUDY for rel_prefix={}, got {} input files under {}"
            .format(rel_prefix, len(input_path_list),input_folder))
        # Get SQL TABLE PARAMS (od_rel_datacolumns) and MINING MAP PARAMS
        od_rel_datacolumns, d_node_params = config.sql_mining_params()
        xfile_count_first = 0
        xfile_count_span = 0

    elif rel_prefix == 'cr201711':
        import xml2rdb_configs.crossref as config
        # Note- input folder is/was populated via program crafdtxml
        rel_prefix = 'cr201711'
        # NOTE LIMIT INPUT FOLDER for now...
        # Set input_folders to sequence of study_days to map
        cymd_start = '20171101'
        cymd_end = '20171115'
        study_days = etl.sequence_days(cymd_start, cymd_end)
        input_folders = []
        for y4md, dt_day in study_days:
          y4 = y4md[0:4]
          mm = y4md[4:6]
          dd = y4md[6:8]
          input_folder = ('U:/data/outputs/crafdtxml/doi/{}/{}/{}'
            .format(y4,mm,dd))
          input_folders.append(input_folder)
        # end for y4md, dt_day in study_days
        input_path_glob = 'doi_*.xml'
        print("{}: rel_prefix={}, using input_path_glob={} with input folders={}"
              .format(me, rel_prefix, input_path_glob, input_folder))

        folder_output_base = etl.data_folder(linux='/home/robert/git/'
            , windows='U:/data/'
            , data_relative_folder='outputs/xml2rdb/{}/'.format(rel_prefix))

        doc_rel_name = 'cross_doi' # must match highest level table dbname in od_rel_datacolumns, set below.
        #Next doc_root_xpath is set by the harvester crafdtxml so see its code.
        doc_root_xpath = './crossref-api-filter-date-UF/message'

        input_path_list = list(Path(input_folder).glob('**/doi_*.xml'))
        print("STUDY={}, got {} input files under {}"
              .format(study, len(input_path_list),input_folder))
        # Get SQL TABLE PARAMS (od_rel_datacolumns) and MINING MAP PARAMS
        od_rel_datacolumns, d_node_params = config.sql_mining_params()
        xfile_count_first = 0
        xfile_count_span = 0

    elif rel_prefix == 'ccila': #ccila is cuban collection i? latin america
        import xml2rdb_configs.marcxml as config
        output_folder_include_secsz = False

        # This is where the precursor program marc2xml leaves its marcxml data
        # for ccila UCRiverside # items
        in_folder_name = etl.data_folder(linux='/home/robert/git/',
            windows='C:/rvp/data/', data_relative_folder='outputs/marcxml/UCRiverside/')

        #windows='c:/users/podengo/git/outputs/marcxml/', data_relative_folder='UCRiverside')
        folder_output_base = etl.data_folder(linux='/home/robert/git/'
            , windows='C:/rvp/data/'
            , data_relative_folder=(
              'outputs/xml2rdb/{}/'.format(study)))

        print("study {}, using folder_output_base={}".format(study,folder_output_base))

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
        xfile_count_first = 0
        xfile_count_span = 0
    # MIGRATING...
    elif rel_prefix == 'orcid':
        # ORCID id data
        import xml2rdb_configs.orcid as config

        input_folder = '{}/output_orpubtxml'.format(data_elsevier_folder)
        input_folders = [ input_folder]
        input_path_glob = '**/orcid_*.xml'

        xxin_folder_name = etl.data_folder(linux='/home/robert/git/',
            windows='C:/rvp/data/', data_relative_folder='outputs/marcxml/UCRiverside/')

        output_folder_include_secsz = False

        #windows='c:/users/podengo/git/outputs/marcxml/', data_relative_folder='UCRiverside')
        folder_output_base = etl.data_folder(linux='/home/robert/git/'
            , windows='C:/rvp/data/'
            , data_relative_folder=('outputs/xml2rdb/{}/'.format(study)))

        print("study {}, using folder_output_base={}"
             .format(study,folder_output_base))

        # This must be the match highest level table dbname in od_rel_datacolumns
        doc_rel_name = 'person'

        # Must be the highest xml element in xml input files
        doc_root_xpath = ".//{*}record"

        input_path_list = list(Path(input_folder).glob(input_path_glob))
        d_xml_params['attribute_text'] = 'text'

        print("STUDY={}, got {} input files under {}"
              .format(study, len(input_path_list),input_folder))
        # Get SQL TABLE PARAMS (od_rel_datacolumns) and MINING MAP PARAMS
        od_rel_datacolumns, d_node_params = config.sql_mining_params()
        xfile_count_first = 0

    elif rel_prefix == 'e2018':
        import xml2rdb_configs.elsevier as config

        print("Setting parameters for rel_prefix-'{}'".format(rel_prefix))
        xfile_count_first = 0
        xfile_count_span = 0
        input_path_glob = '**/pii_*.xml'
        # rel_prefix e2017 used 20180124 with range(2010,2018)
        # rel_prefix e2017 used 20180124 with range(2018,2019)

        input_folders = []
        for year in range(2018, 2019):
            input_folder =('{}/output_ealdxml/{}/'
               .format(data_elsevier_folder,year))
            print("Got rel_prefix={}, input_folder={}"
              .format(rel_prefix,input_folder)
            )
            input_folders.append(input_folder)

        doc_rel_name = 'doc'
        doc_root_xpath = './{*}full-text-retrieval-response'

        # Get SQL TABLE PARAMS (od_rel_datacolumns) and MINING MAP PARAMS
        od_rel_datacolumns, d_node_params = config.sql_mining_params()

    elif rel_prefix == 'x2018':
        import xml2rdb_configs.xis_subjects as config
        print("Setting parameters for rel_prefix-'{}'".format(rel_prefix))
        xfile_count_first = 0
        xfile_count_span = 0
        # here may define a Item object , where for xis it is initialized
        # to read a xis file
        # And it has its  method
        # next_item that returns the xml tree for it.
        # Later change all studies to initialized the Item.. add the
        # Item class's init params to the xml config  file
        # r'C:\rvp\data\xis\export_subjects\xis_subjects_parsed.xml'


        # { 20180922 todo:  implement a separate object called FolderSet to contain these params:
        # ERROR? need double backslash for last backlach even with r' type of string?
        input_folder = r'c:\rvp\data\xis\export_subjects\\'
        print(f" *****  Using input_folder = '{input_folder}'")
        input_folders = [input_folder]
        # } todo:  implement a separate object called FolderSet to contain these params:

        # { todo: create ITEM object
        # to contol the item READER -
        # input_path_glob will be one if its  init params...
        # Eg, for a reader of independent item files in a hierarchy
        input_path_glob = 'xis_subjects_parsed.xml'
        input_path_glob = 'xis_subjects_small.xml'
        # NOTE: Tod0, depending on oher init params of ItemReader, may also add the
        # FolderSet as optional init param,

        # Todo - create a new object ItemParser and initialize with doc_root_xpath,
        # etc
        # For document/item - the relation name to hold on instance

        doc_rel_name = 'bibvid'
        doc_root_xpath = 'Thesis'
        # Get SQL TABLE PARAMS (od_rel_datacolumns) and MINING MAP PARAMS
        od_rel_datacolumns, d_node_params = config.sql_mining_params()

    else:
         raise ValueError("Unknown rel_prefix = '{}'. Exit.".format(rel_prefix))

    # DocNodeSet is(will be) an object that identifies the full set of  individual
    # input doc nodes.
    # Its method generator_next() a genertor/reader returns the sequene of
    # all document nodes in the input, in the form of lxml document nodes.
    # Successive calls to the generator yield eturns the root doc node of the
    # document in the input set of document nodes.

    doc_node_set = DocNodeSet(input_folders=input_folders,
        input_file_glob=input_path_glob,
        verbosity=1)
    sequence_doc_nodes = doc_node_set.generator_doc_nodes()

    # OPTIONAL - If a study specified multiple input folders and input_path_glob,
    # then honor them when constructing the input_path_list
    if (input_folders is not None and input_path_glob is not None):
        # compose input_path_list over multiple input_folders
        input_path_list = []
        for input_folder in input_folders:
            print("{}:Study {}:Using input_folder='{}'\n"
                .format(me,study,input_folder))
            input_path_list.extend(list(Path(input_folder).glob(input_path_glob)))

    # If input_folders not defined in a study, define it by putting the single
    # input folder into this list
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
        ,'folders_base': data_elsevier_folder
        ,'doc-rel-name': doc_rel_name
        ,'doc-root-xpath': doc_root_xpath
        ,'use-db': use_db
        ,'d-node-params': repr(d_node_params)
        ,'od-rel-datacolumns': repr(od_rel_datacolumns)
    })

    # RUN the analysis and collect stats
    #using xml2rdb2 now.
    log_filename, pretty_log = xml2rdb(
        sequence_doc_nodes = sequence_doc_nodes,
        # input_path_list=input_path_list,
        folder_output_base=folder_output_base,
        output_folder_include_secsz=output_folder_include_secsz,
        doc_root_xpath=doc_root_xpath, rel_prefix=rel_prefix,
        doc_rel_name=doc_rel_name, use_db=use_db,
        d_node_params=d_node_params, od_rel_datacolumns=od_rel_datacolumns,
        d_params=d_params,
        d_xml_params=d_xml_params,
        verbosity=verbosity,
        )

    print("{}: Returned from xml2rdb with d_params=:".format(me))

    for key, val in d_params.items():
        print("{}={}".format(key, val))

    print("{}:Done.".format(me))
#end def run()
#
# Flush STDOUT for this print
print("Starting!",flush=True)
sys.stdout.flush()

rel_prefix = 'e2018'
rel_prefix = 'x2018'

run(rel_prefix=rel_prefix, verbosity=2)
print("Done!")
