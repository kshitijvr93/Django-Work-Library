'''
Python 3.6 code, may work with earlier Python 3.x versions

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

(*) d_mining_map, the 'mining map' starting with the
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

(*) The param od_mining_map may include a key 'od_attribute_column' which value is a dictionary where
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


Note: if arg output_file is not set one xml file will be created in output folder
when needed named by bar-separated list of lineage_ids.

method rel_node_visit()

Arguments:

node - In the mining map, where a dictionary key is a relation name,
   its value is a dictionary called a node.

stack_tags: the list or stack of all parent tags to this one in the context
    of this call in a DAG tree of recursive calls.

lineage_ids: the array or ordered indexes into this relations ancestor
    relations.

open_level - the index into stack_tags that identifies the closest ancestor
whose opening tag has been outputted so far. If this call causes any output
to be written, all the opening tags up through this one, the latest, must have
an opening tag written to the output

<param name='d_mining_map'>

This defines child relations to the primary relation, and for each it provides
a mining map of xml elements and attributes to output, along with the source
column data to convert to produce each output attribute value.

</param><param name='d_map_params'>

  A dictonary of key terms that may be used to define map-related
  parameters, such as keywords to use to indicate output to element
  content rather than to specific xml attributes.

</param>

'''
class RelationMiner:
    def __init__(self, d_mining_map=None
         ,d_map_params=None, verbosity=0):

        required_args = [d_mining_map, d_map_params]
        if not all(required_args):
            raise ValueError("Missing some required_args values in {}"
                .format(repr(required_args)))

        self.d_mining_map = d_mining_map

        self.d_map_params = (
            d_map_params if d_map_params is not None else {})

        self.verbosity = verbosity

    '''
    <param name='dataset_source'>
    This is a dataset_source object that has method
      select_contained_rows(relation_name, lineage_ids).
    See there for more details.

    </param><param name='relation_name_prefix'>
      This is a prefix string to prepend to the primary_relation_name argument
      and to every relation name in self.d_mining_map to identify a relation name
      known by the dataset_source

    </param> <param name='primary_relation_name_suffix'>
      This indicates the primary relation name_suffix in the datasource that
      is associated with the d_mining_map primary relation. The primary relation
      name is constructed from this and the relation_name_prefix parameter.

    </param> <param name='output_folder_name'>
      This is the name of the primary output_folder in the filesystem.
      Considering: Later this argument may be changed or expanded to accept an
      alternate and more general object called datasource_destination that
      abstracts filesysetm objects and various datasets, databases, and other
      output types.

    </param> <param name='output_file_name'>
      This argument is optional by design. If it is not given, then an independent
      filename will be constructed per input row of the primary relation
      and written to the output folder.

    </param> <param name=''>
    </param>
    '''
    def mine(self, dataset_source=None
        , relation_name_prefix=''
        , primary_relation_name=None
        , output_folder=None
        , output_file_name=None
        , zfill_id_count=8
        ,verbosity=0):
        # Register input and output style options
        # and visit all the selected relational nodes in the
        # d_mining_map mining map to mine from dataset_source the values
        # defined in the mining map and to produce output.
        me = 'RelationMiner.mine()'
        required_args = [dataset_source, relation_main
            ,output_folder]
        if not all(required_args):
            raise ValueError("{}:Missing some required_args values in {}"
                .format(repr(me,required_args)))

        self.primary_relation_name = primary_relation_name
        self.output_folder = output_folder
        self.zfill_id_count = zfill_id_count
        # Make sure output folder exists

        self.output_file_name = '' if output_file_name is None else output_file_name
        if self.output_file_name != '':
            # One big output file is required
            with open(
              '{}{}'.format(output_folder,output_file_name),'w') as self.output_file:
                node_visit_output(self, d_mining_map, lineage_ids=lineage_ids)
        else:
            self.output_file = None
            # One output file per primary relation row is required.
            node_visit_output(self, d_mining_map, lineage_ids=lineage_ids )
        return

    '''
    <summary>Method node_visit_output:
    To support one-big xml file of output vs one per output record,
    node_visit_output always checks output_file, and if None, it will output
    one xml file per primary relation row.

    If none, it constructs the output file name and opens a separate
    output file for each output record/object.

    </summary>
    <param name='node'>
    Either the root value (a dictionary) for the self.d_mining map or the
    dictonary value of a child node in the self.d_mining map.

    </param><param name='lineage_ids'>
    The stack of lineage_ids (relation_id values) of all parent rows and the
    current relation  row. This is used in calls to
    dataset_source.select_contained_rows to select the particular rows of interest
    to output to the xml output file(s).

    </param><param name=''>
    </param><param name=''>
    </param>
    <notes>
    The db object was initialized with the same mining_map, and upon init,
    it set up a row-generator for each relation in the map.

    It is implemented as a two-level generator, three-levels if counting the basic
    file row-at-a-time generator, but that is called by the file_db object
    (derived class from the persisitent-data-hierarchy-object)

    where a main generator cycles through a 2d or inner one for the same relation,
    but the inner one has a one-row cache option (not used on first call).
    The inner generator for a relation is also initialized to store the
    parent composite id (the lineage of parent ids for any relation row,
    plus the lineage/sibling id of that relation itself, among rows withthe
    same parent row, forms a rows' composite id).
    The inner generator may use a db-curor for that relation that selects
    all rows of the relation, ordered by the hierarchical composite ids.
    The inner generator simply examines the parent id of each row returned
    by the db-cursor and when the parent id for a cursor-returned row
    returns a value different from the parent_id, it stores the row in a
    one-row cache and returns None and changes that inner generators
    parent id now to the new value so it can return the next set of
    rows with that parent id.
    A relation-row generator is initialized when

    </notes>
    '''
    def node_visit_output(self
        ,node=None
        ,composite_ids=None
        ,d_row=None
        ):
        me = 'node_visit_output()'


        required_args = [node, composite_ids, d_row]

        if not all(required_args):
            raise ValueError("{}:Missing some required_args values in {}"
                .format(me,repr(required_args)))

        node_depth = len(composite_ids)
        # Note: special checks are made whether node_depth is 0, in which case
        # this is the root or top level call, and when it returns, the recursive
        # mining process has completed.

        node1_name = node['node1_name'] # eg a relation name

        if verbosity > 0:
            msg = ("{}:START: verbosity={},node.relation_name={}, lineage_ids={}"
               .format(me, verbosity, node.relation_name, lineage_ids))
            print(msg)

        # This row's sibling id defines its lineage_id
        # Consider: a flexible way to identify the sibling id column name.
        # Perhaps it would be some param info to add to d_map_params.
        # This is 'the way' that xml2rdb names the lineage id columns, and
        # this code is initially developed to work with that, so the column
        # names are constrained to be the ones expected here.
        # It might better be defined by params for dataset_source, and
        # its selection method should return a vector of these ids to resuse
        # perhaps as an additional argument to this mehod

        sibling_id = d_row['{}_id'.format(node.relation_name)]
        composite_ids.append(sibling_id)

        if len(lineage_ids == 1) and self.output_file is None:
            #This node is a row for the primary relation, and
            #no output file is yet defined, so we
            #must open one for this primary relation row.

            file_path_name = (
              '{}{}_{}'.format(self.output_folder,self.primary_relation_name
              , str(sibling_id).zfill(self.zfill_id_count)))
            output_file = open('file_path_name','w')
            raise ValueError('Not all args {} were given.'.format(required_args))

        attribute_text = d_map_params.get('attribute_text','text')
        attribute_innerhtml = d_map_params.get(
            'attribute_innerhtml' ,'attribute_innerhtml')

        d_row = {}; d_attribute_value = {}; content_value = ''

        d_attribute_column = d_mining_map.get('attribute_column', None)
        if d_attr_column is not None:
            # We have some node attributes with associated relational columns
            # eligible for output as xml attributes
            # so we will set them up in d_row key-value pairs.
            if not isinstance(d_attribute_column, dict):
                # detect some sorts of errors/typos in the d_mining_map parsing configuration
                import types
                raise Exception(
                    "d_attribute_column {}, type={} is not dict. stack_tags={}"
                    .format(repr(d_attribute_column
                    ,repr(type(d_attribute_column)),stack_tags))

            #node_text = etree.tostring(node, encoding='unicode', method='text')
            # Must discard tabs, used as bulk load delimiter, else sql server 2008 bulk insert error
            # messages appear, numbered 4832 and 7399, and inserts fail.
            #node_text = node_text.replace('\t',' ').replace('\n',' ').strip()
            #node_text = "" if stringify is None else stringify.strip()

            for attribute_name, column_name in d_attribute_column.items():
                # For every key in attr_column, if it is reserved name in attribute_text,
                # use the node's text value, else seek the key in node.attrib
                # and use its value.

                column_value = ''
                content_value = ''
                if attribute_name == attribute_text:
                    # Special reserved name in attribute_text: it is not really an attribute name,
                    # but this indicates that we shall use the node's content/text for
                    # this attribute
                    content_value = d_row[column_name]
                else:
                    column_value = d_row[column_name]

                #print("setting d_row for column_name={} to value={}".format(column_name,column_value))
                d_attribute_value[column_name] = column_value
        # All attribute values and content for this xml element, if any was found,
        # is ready to be output and stored in d_attribute_value, so output it.

        # First cut, always output the element tag name even if no values found
        # yet for it.
        # Later we might provide an option defer xml tag  output until/unless
        # a value is found in dataset source that belongs within the element.
        print('<{}'.format(node['element_tag_name']))
        # for every attribute value, insert a setting for it
        for attribute, value in d_attribute_value:
            print(' {}={}'.format(attribute, value), file=self.output_file)
        print(' >', file=self.outputfile)

        ################# SECTION - For each child relation recurse to its child nodes ###############

        d_relation_child_nodes = d_mining_map.get('relation_child_nodes', None)

        wrote_some_output = 0

        if d_relation_child_nodes is not None:
            for relation_name, d_child_node in d_relation_child_nodes.items():
                #print("{} seeking xpath={} with node_params={}".format(me,repr(xpath),repr(d_child_mining_map)))
                #children = node.findall(xpath, d_namespaces )
                # CRITICAL: make sure db.sequence() does select with order by the relation_namd_id
                # else hard-to-debug errors may result
                child_rows = db.sequence(relation_name, node_index)
                if (verbosity > 0):
                    print("{}:for relation_name={} found some child rows".format(me,relation_name))
                # TODO:Future: may add a new argument for caller-object that child may use to accumulate, figure,
                # summary statistic
                d_child_row = None
                for d_row in db.select_contained_rows(
                    relation_name, lineage_ids=lineage_ids):
                    # Asssume i always goes in counting order at first, later get it out of the row
                    # index = d_child_row['{}_id'.format(relation_name)
                    d_child_row, child_output = node_visit_output(node=d_child_node
                        , lineage_ids=lineage_ids
                        , d_row=d_row
                        , output_file=output_file
                        , d_map_params = d_map_params
                        , verbosity=verbosity)
                    # Finished visiting a child relation
                    # Register whether any data was output: misc info or new retval should have that.
                    if child_output:
                        made_output = True
                    # so that we can eventually discover whether any  data was output under this relation row
                    # and thus decide whether to output a closing xml tag.

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
        if 'column_constant' in d_mining_map:
            for column, constant in d_mining_map['column_constant'].items():
                d_row[column] = constant
        import types
        d_column_functions = d_mining_map.get('column_function',None)
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

# end class RelationMiner
'''
Method rdb_to_xml: from given xml doc(eg, from an Elsevier full text retrieval apifile),
convert the xml doc for output to relational data and output to relational tab-separated-value (tsv) files.
Excel and other apps allow the '.txt' filename extension for tab-separated-value files.

New twist - now this is rdb_to_xml
'''
def rdb_to_xml(
    tags=None
    ,d_root_node_params=None
    ,d_mining_map=None
    ,output_folder=None
    ,d_map_params=None
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
           "len(d_mining_map)='{}', len od_rel_datacolumns={}."
          .format(me, repr(tags), output_folder, repr(od_relation)
                  ,len(d_mining_map) ,len(od_rel_datacolumns)))
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
    relation_name = node['relation_name']

    # final: row_selection = dataset.cursor_relation(relation_name='record', node_index=[])
    # testing:

    row_selection =  [{'a':'5', 'b':'6'}, { 'a':'8', 'b':'9' }]
    node_index = []
    output_file_name = output_folder + '/rdbtoxml.xml'

    tags = [root_tag]
    node = d_mining_map['start'];

    d_map_params = dict({'attribute_text':'text'})

    # Above was emulation of some args - now star method code prototype
    print("Using output_file={}".format(output_file))

    tag = tags[len(tags) - 1]
    with open(output_file_name, mode='r', encoding='utf-8') as file_out:
        retval = rel_node_visit_output(
            node=od_mining_map
            ,tags=tags
            ,node_index=node_index
            ,d_map_params=d_map_params
            ,output_file=output_file)

    print ("Done!")

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
        'child_xpaths':{doc_root_xpath:d_mining_map}
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
        ,d_mining_map=d_root_params
        ,od_rel_datacolumns=od_rel_datacolumns
        ,output_folder=output_folder
        ,od_parent_index=od_parent_index
        ,node_index=node_index
        ,node=doc_root
        ,d_map_params=d_map_params
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
    , d_mining_map=None
    , od_rel_datacolumns=None
    , output_folder=None
    , use_db=None
    , file_count_first=0
    , file_count_span=1
    , verbosity=0
    , d_map_params=None
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
    elif not (d_mining_map):
        bad = 6
    elif not (output_folder):
        bad = 7
    elif not (od_rel_datacolumns):
        bad = 8
    elif not (use_db):
        bad = 9
    elif d_map_params is None:
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
            , d_mining_map=d_mining_map
            , od_rel_datacolumns=od_rel_datacolumns
            , verbosity=verbosity
            , d_map_params=d_map_params)

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
            d_mining_map=None, od_rel_datacolumns=None,
            d_params=None, file_count_first=0, file_count_span=1,
            d_map_params=None,verbosity=0):
    me = "xml2rdb"
    utc_now = datetime.datetime.utcnow()
    utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")

    print("{}: STARTING at {}".format(me, utc_secs_z))

    if not (input_path_list
            and (rel_prefix or rel_prefix == '')
            and doc_root_xpath and use_db and doc_rel_name
            and d_mining_map and od_rel_datacolumns
            and d_params
            and d_map_params is not None
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
      , d_mining_map=d_mining_map
      , od_rel_datacolumns=od_rel_datacolumns
      , use_db=use_db
      , file_count_first=file_count_first
      , file_count_span=file_count_span
      #, output_name_suffix=output_name_suffix
      , verbosity=verbosity
      , d_map_params=d_map_params
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

    d_map_params = {}
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
        od_rel_datacolumns, d_mining_map = config.sql_mining_params()
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
        d_map_params['attribute_text'] = 'text'

        print("STUDY={}, got {} input files under {}"
              .format(study, len(input_path_list),input_folder))
        # Get SQL TABLE PARAMS (od_rel_datacolumns) and MINING MAP PARAMS
        od_rel_datacolumns, d_mining_map = config.sql_mining_params()
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
        d_map_params['attribute_text'] = 'text'

        print("STUDY={}, got {} input files under {}"
              .format(study, len(input_path_list),input_folder))
        # Get SQL TABLE PARAMS (od_rel_datacolumns) and MINING MAP PARAMS
        od_rel_datacolumns, d_mining_map = config.sql_mining_params()
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
        od_rel_datacolumns, d_mining_map = config.sql_mining_params()
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
        od_rel_datacolumns, d_mining_map = config.sql_mining_params()
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
        od_rel_datacolumns, d_mining_map = config.sql_mining_params()
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
        od_rel_datacolumns, d_mining_map = config.sql_mining_params()

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
        od_rel_datacolumns, d_mining_map = config.sql_mining_params()

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
        od_rel_datacolumns, d_mining_map = config.sql_mining_params()

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
        d_map_params['attribute_text'] = 'attribute_text'
        d_map_params['attribute_innerhtml'] =  'attribute_innerhtml'

        od_rel_datacolumns, d_mining_map = config.sql_mining_params()
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
        d_map_params['attribute_text'] = 'attribute_text'
        d_map_params['attribute_innerhtml'] =  'attribute_innerhtml'

        od_rel_datacolumns, d_mining_map = config.sql_mining_params()
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
        ,'d-node-params': repr(d_mining_map)
        ,'od-rel-datacolumns': repr(od_rel_datacolumns)
    })

    # RUN the analysis and collect stats
    log_filename, pretty_log = xml2rdb(
        input_path_list=input_path_list,
        folder_output_base=folder_output_base,
        doc_root_xpath=doc_root_xpath, rel_prefix=rel_prefix,
        doc_rel_name=doc_rel_name, use_db=use_db,
        d_mining_map=d_mining_map, od_rel_datacolumns=od_rel_datacolumns,
        d_params=d_params, file_count_first=file_count_first, file_count_span=file_count_span,
        d_map_params=d_map_params)

    print("Done.")
#end def run()
#
run('scopus')
