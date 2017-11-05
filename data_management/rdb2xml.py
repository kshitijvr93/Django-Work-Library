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
from dataset.ordered_relation import OrderedRelation

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

  def __init__(self, d_mining_map=None ,d_map_params=None, verbosity=0):
    required_args = [d_mining_map, d_map_params]
    if not all(required_args):
      raise ValueError("Missing some required_args values in {}"
      .format(repr(required_args)))

    self.d_mining_map = d_mining_map

    self.d_map_params = d_map_params if d_map_params is not None else {}

    self.verbosity = verbosity

  def mine(self, dataset_source=None
      , relation_name_prefix=''
      , primary_relation_name=None
      , output_folder=None
      , output_file_name=None
      , zfill_id_count=8
      , verbosity=0):

    # Register input and output style options
    # and visit all the selected relational nodes in the
    # d_mining_map mining map to mine from dataset_source the values
    # defined in the mining map and to produce output.
    me = 'RelationMiner.mine()'
    required_args = [dataset_source, relation_main ,output_folder]

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


    # node1_name is the input dataset's group record name:
    # for databasess it is a table or relation name
    # for xml it is an element tag name,
    # for 'tsf' files in a directory it is a file name of tab separated
    # ordered values per file line, etc.
    # And node2_name is the output dataset's name for a record or
    # parent group of data
    <20171104 notes> <summary>
    This method's processing - summary:

    This method is designed to be first called with a node that represents the
    root of an input hierarchical tree of data. The first version/instance is
    designed to do a depth first tour of the rows  in a  hierarchical set of
    relations,
    <move_me todo='add this to docs on OrderedRelation' or the tsf
    derived class of OrderedRelation>
    where the data for each relation is in the same input folder, and each
    relation has 2 associated text input files: relation.tsf and relation.txt.
    File relation.tsf has a single line, which is Tab-Separated Fieldsnames(TSF)
    of the relation, and file realtion.txt is a set of text lines of
    tab-separated values, each representing a row of the relation. Since
    .txt is a common extension used for files of Tab-Separated Values, that
    naming convention used for those files rather than '.tsv'.
    </move_me>

    The method arguments of  'ancestor_ids' and 'd_row' provide the parent
    relation row id information and key-value pairs of the parent rows with
    the key in the form of relation_name.column_name and the value for each
    key is a simple string value.
    Note: Since this is python 3, that string is internally unicode,
    and reads and writes of the data are expected to be using UTF-8 encoding.

    In this method, the sibling rows of the current relation (all rows
    with the same parent row) are visited in a loop.

     - For each sibling row: the following is done:
     (See loop: for row in relation.squence.ordered_siblings: )
     - That retrieve's from the input dataswet the next row's values (field1 values)
     - the node.d_field2_field1 dictionary is enumerated to output field2 values
     that are dervied from  the field1 values of the sibling row.
     - an inner loop through the node's child_nodes is executed, where for each child_node:
    -- the sibling_id of the main relation row is appended to the given
      ancestor_ids
    -- a new d_row value is appended by appending this sibing row's values
     to the given d_row (they might be used by a recursive call in case a
     child_node node needs to use them to derive some values)
     -- a recursive call is made to node_visit_output for the child node


    The given node corresponds to an input relation
    named in the node['node1_name'], and it will produce output
    in node2_name.

    Note the node has a dictionary d_field2_field1
    (or may change name to d__field_output__fields_input to be more explicit
    and allow for multiple inputs to affect output)
    which appears reversed, however
    note that the dictaonry key here is field2 which identifies a unique output,
    however the input field1 value might be of use to several different output fields
    to calculate derived values, and so it appears as the value of the dictionary, as it
    might repeat across dictionary entries..

    When this method is called, the d_row dictionary will have the field values
    of the input dataset's parent relations. Because this

    </summary> </20171104 notes>
    </notes>
    '''
  def node_visit_output(self
    ,node=None
    ,d_name_relation=None
    ,ancestor_ids=None
    ,d_row=None
    ,verbosity=0
    ):
    me = 'node_visit_output()'

    required_args = [node, d_name_relation]
    if not all(required_args):
      raise ValueError("{}:Missing some required_args values in {}"
      .format(me,repr(required_args)))

    # node1_name is the input dataset's group record name:
    # for databasess it is a table or relation name
    # for xml it is an element tag name,
    # for 'tsf' files in a directory it is a file name of tab separated
    # ordered values per file line, etc.
    # And node2_name is the output dataset's name for a record or
    # parent group of data

    node1_name = node['node1_name'] # eg a relation name

    if verbosity > 0:
      msg = (
      "{}: verbosity={},node1_name={}, ancestor_ids={},len(d_row_={})"
      .format(me, verbosity, node1_name, repr(ancestor_ids),len(d_row)))
      print(msg)

    if len(ancestor_ids) == 1 and output_file is None:
      # This node visit and child visits will generate an output forw for the
      # main relation, which will produce its own output file.
      # Now open one the output file for this primary relation row.
      file_path_name = (
      '{}{}_{}'.format(self.output_folder,node1_name
      , str(sibling_id).zfill(self.zfill_id_count)))

      output_file = open('file_path_name','w')

    # Next for loop - cycle through this node's sibling rows
    #TODO: maybe add argument d_name_relation to calculate relation
    #from a relaton name or depth.

    for (row_count, sibling_row) in relation.sequence_ordered_siblings():

     # This row's sibling id, appended to ancestor_ids
     # identifies this row as unique in the dataset w hen composed with  its
     # ancestor_ids (parent ids)
     # Consider: a flexible way to identify the sibling id column name.
     # Perhaps it would be some param info to add to d_map_params.
     # This is 'the way' that xml2rdb names the lineage id columns, and
     # this code is initially developed to work with that, so the column
     # names are constrained to be the ones expected here.
     # It might better be defined by params for dataset_source, and
     # its selection method should return a vector of these ids to resuse
     # perhaps as an additional argument to this mehod

     name_this_id ='{}_id'.format(node['node1_name'])
     sibling_id = int(sibling_row[name_this_id])
     ancestor_ids.append(sibling_id)


    attribute_text = d_map_params.get('attribute_text','text')
    attribute_innerhtml = d_map_params.get(
        'attribute_innerhtml' ,'attribute_innerhtml')

    if(verbosity > 0):
        print("attribute_text={}, attribute_innerhtml-{}"
        .format(attribute_text,attribute_innerhtml))

    d_row = {}; d_attribute_value = {}; content_value = ''
    # d_field2_field1 is keyed by the output column/field name within its
    # parent, and the value is the input d_row{} key/column name to use to
    # retrieve the data value to use.
    d_field2_field1 = d_mining_map.get('d_field2_field1', None)
    if d_field2_field1 is not None:
      # We have some field2 ouptut fields with associated  field1
      # input fields/columns designed for outputting
      # so we will set them up in d_row key-value pairs.

      if not isinstance(d_field2_field1, dict):
        # detect some sorts of errors/typos in the d_mining_map parsing configuration
        raise Exception(
            "d_field2_field1 {}, type={} is not dict. stack_tags={}"
            .format(repr(d_field2_field1
            ,repr(type(d_field2_field1)),stack_tags)))

      #node_text = etree.tostring(node, encoding='unicode', method='text')
      # Must discard tabs, used as bulk load delimiter, else sql server 2008 bulk insert error
      # messages appear, numbered 4832 and 7399, and inserts fail.
      #node_text = node_text.replace('\t',' ').replace('\n',' ').strip()
      #node_text = "" if stringify is None else stringify.strip()

      for attribute_name, column_name in d_field2_field1.items():
        # For every key in attr_column, if it is reserved name in attribute_text,
        # use the node's text value, else seek the key in node.attrib
        # and use its value.

        column_value = ''
        content_value = ''
        if attribute_name == attribute_text:
            # Special reserved name in attribute_text: it is not really
            # an attribute name, but this indicates that we shall use the node's
            # content/text for this attribute
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

      ################# SECTION - On current sibling_row, for each child
      # node relation, recurse to visit it and output its data.

      d_relation_child_nodes = d_mining_map.get('child_nodes', None)
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
            , ancestor=ancestor_ids
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
          # This design allows the child to set up local d_row d_field2_field1 values with names
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
  if not all(required_args):
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

  # Above was emulation of some args - now start method code prototype
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
  tags = rel_node_doc_visit(node=node, tags=tags)

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

  with open(output_file_name, "w", encoding="utf-8") as output_file:

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


# RUN PARAMS AND RUN
import datetime
import pytz
import os
from collections import OrderedDict


def rdb2xml_test():
  me = 'rdb2xml_test'

  import rdb2xml_configs.marctsf2xml as config

  from dataset.ordered_relation import OrderedRelation
  from dataset.phd import PHD
  import dataset.phd

  d_map_params = {'attribute_text':'text'}
  input_folder = etl.data_folder(
  linux="/home/robert/", windows="C:/users/podengo/",
  data_relative_folder='git/outputs/xml2rdb/ccila/')

  output_folder = etl.data_folder(
  # See xml2rdb.py study 'ccila' definition of folder_output_base
  linux="/home/robert/", windows="C:/users/podengo/",
  data_relative_folder='git/outputs/rdb2xml/ccila/')
  composite_ids = []

  relation_miner = RelationMiner(d_mining_map=config.d_nodes_map,
  d_map_params=d_map_params)

  # create test set of relations to mine with rudimentary manual instantiations.
  print('{}:Constructing phd = PHD(...)'.format(me))
  phd = PHD(input_folder, output_folder,verbosity=1)

  relation_name='record'
  # NOTE: IMPOSE a requirement to use '' as the parent of the root relation.
  # It should facilitate
  # some diagnostic and error reporting

  parent_child_tuples = [
  ('','record'),
  ('record','controlfield'),
  ('record','datafield'),
  ('datafield','subfield')
  ]
  d_name_relation = {}

  for (parent_name, relation_name) in parent_child_tuples:
    relation = phd.add_relation(parent_name=parent_name
    , relation_name=relation_name
    ,verbosity=0)
    d_name_relation[relation_name] = relation
    print('{}:Added relation named {} with parent named {}'
      .format(me,relation_name,parent_name))
    ancestor_ids = []
    d_row = {'test':'test',}

    #Mine this config - visit all nodes and create outputs
    #note todo: add argument for d_name_relation for node_visit_output to use to
    #invoke correct sequence generator

    node = config.d_nodes_map

  if 1 > 0:
    print("step x2")
    print("{}.Using node={}.".format(me,repr(node)))

  relation_miner.node_visit_output(node=config.d_nodes_map
    ,d_name_relation=d_name_relation
    ,ancestor_ids=ancestor_ids
    ,d_row=d_row
    ,verbosity=1
    )

  # Set up and perform  a test run.
  # First we test with
  return

#end run_test


rdb2xml_test()
