'''
Python 3.6 code, may work with earlier Python 3.x versions

Program rdb2xml  reads strcutured hierarchical relational database data
from a hierarchically-related set of database tables that are rooted in a
main root table.

It also reads a configuration file that defines how fields from the database
tables are to be mapped to one or more utf-8 encoded xml output files.

This program conceptually does  the 'reverse' of what
longer-standing program xml2rdb does.

Each output xml file has xml-coded information pertaining to a single xml
document.

'''
import sys, os, os.path, platform

platform_name = platform.system.lower()
if platform_name == 'linux':
    modules_root = 'tbd'
    raise ValueError("MISSING: Enter code here to define modules_root")
else:
    # assume rvp office pc running windows
    modules_root="C:\\rvp\\"
sys.path.append('{}git/citrus/modules'.format(modules_root))

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
from dataset.ordered_relation import OrderedRelation,OrderedSiblings

'''
Method row_output_visit

Given parameters:
(*) node_index - the index of the current node (it is the depth of
  nesting) into the following parameters for lists of node_names and uuids
  The 'current node' in this method represents a single row in a relation
  that match the hierarchy of node_names (relations) and uuids.

(*) node_names (names of outer parents in nested
  relations where the first node name is the outermost nested relation and
  the last name is for this row row of the current relation), identified in
  uuids[]

(*) uuids[], (the parent nodes and current node is represented by this list
  path of hierarchical uuids from a set of parent database tables, with the
  final uuid identifying a unique row in the current node), and

(*) opened_index: index into node_names indicating the highest level where
  an opening tag has so far been outputted. This way, a recursive call that
  generates the first output for a node can determine the greatest ancestor
  parent that has not yet output its opening tag, and then output those
  tags in proper order, as needed.

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
  last_name, comma, first_name' value. It is used for the 'translation'
  functionality of an ETL process, which may be of limited use since the
  data has already been mapped into the relational database, usually in a
  nice format.
  However, it might be reversed-emulated somehow in future versions for use
  in the rdb2xml direction.

Processing:

The node represents a 'current row', a specific data row in a table/db_name.
(*) If the row has any data to be output (per the below processing), an xml
element opening tag is outputted with the same name as the current row's
table name.

(*) The param od_mining_map may include a key 'od_attribute_column' which
value is a dictionary where each key is an attribute name to output and the
value is a column name in the current row.
Special attribute names are reserved: text_content' indicates tha the rdb
value is to put output as the main content of the current xml elemnt being
output. Other names are the actual xml attribute names to be outputted.

For each entry in od_attribute_column,
....
(1) first check the given 'opening_index' value that somhow indicates not-
yet-outputted parent xml tags and open all the parent tags given in array
'tags'(output their opening tag to the output stream)
consider:  let prior recursive caller just maintain arg tags and put in the
ancestral line of unopened tags.
So in this call, if any value is detected that needs to be output, then
output all openings of any tags, plus this
tag, and clear the tags list to pass down in next recursive call.
To make things simpler, at very start of this method, always append 'this'
tag to the list of tags.


After a recursive call, the tags are included in the return values by the child.
If a child returns the tags list with any tags, then the last tag pertains to
this call instance, meaning no data was found to output for this tag,
and so do not output a closing tag, and DO delete this last tag in the list,
and then return that as part of the return value. This may be a phase 0 or
phase 1 feature.
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
to a recursive call to row_output_visit for that row.

(*) After the 'child_path' processing code, and if any data was output from
this node, as inferred from the return values from the recursive calls (or
the presence of a key in d_rdb_xml) a closing tag is output.

Def rel_row_output_visit()
use this name, same as in xml2rdb except with rel_ prefix.

Compare and contrast some features with established row_output_visit() in
xml2rdb as of 20171026:


Note: if arg output_file is not set one xml file will be created in output folder
when needed named by bar-separated list of composite_ids.

method rel_node_visit()

Arguments:

node - In the mining map, where a dictionary key is a relation name,
   its value is a dictionary called a node.

stack_tags: the list or stack of all parent tags to this one in the context
  of this call in a DAG tree of recursive calls.

composite_ids: the array or ordered indexes into this relations ancestor
  relations.

open_level - the index into stack_tags that identifies the closest ancestor
whose opening tag has been outputted so far. If this call causes any output
to be written, all the opening tags up through this one, the latest, must have
an opening tag written to the output

<param name='d_mining_map'>

This defines child relations to the primary relation, and for each it provides
a mining map of xml elements and attributes to output, along with the source
column data to convert to produce each output attribute value.

</param><param name='d_mining_params'>

  A dictonary of key terms that may be used to define map-related
  parameters, such as keywords to use to indicate output to element
  content rather than to specific xml attributes.

</param>
<param name=relation_name_prefix> todo: honor this and prepend it to input names
of input relation nams found in the mining map to derive the physical filenn
name of the utf8-file holding composite_, numerically sorted rows of
the relation
</param>

'''
class RelationMiner:

  def __init__(self, d_mining_map=None ,d_mining_params=None, output_folder=None,
    zfill_id_count=8, relation_name_prefix='', verbosity=0):
    required_args = [output_folder,d_mining_map, d_mining_params]
    if not all(required_args):
      raise ValueError("Missing some required_args values in {}"
      .format(repr(required_args)))

    self.d_mining_map = d_mining_map
    self.d_mining_params = d_mining_params if d_mining_params is not None else {}
    self.verbosity = verbosity
    self.output_folder = output_folder
    # To id mulitple output files, this is minimum length of the id, left zero-filled
    # It makes for easy file sorting viewing and finding, nicer for a user to deal with.
    self.zfill_id_count = zfill_id_count


  '''
  <summary method_name="row_output">
  Method row_output() given a node and its row values, derive and output xml attribute values
  <notes_20171108>
  NOTE: in future, we might pass actual data values from the input data composite columns as
  the composite ids. But letting the code keep and use simple row counts may suffice for some
  types of data sources, eg, the 'tsf' based dataset.
  <details>

    # Next, we may further require that input data follows a convention to name/identify
    # the sibling id column name.
    # for now, the sequence_ordered_siblings does not 'check' (nor does this code) that its data-based composite
    # ids match this programs simple row-counters that are used as the composite ids.
    # the only requirement on input is that the rows of each relation are ordered per their
    # hierarchically organized ascending composite ids.
    # node['node1_name']  might later be defined by new params relating to the input dataset_source, and
    # its selection method (a more complex node['node1_name'] with relation name plus
    # optional filtering conditions, similar to xpath if not exactly xpath) should return
    # a vector of these ids to reuse
    # perhaps as an additional argument to this mehod
    <example> derivation of a composite node column name and value (the last composite id is the
    sibling id among its siblings)
        name_this_id ='{}_id'.format(node['node1_name'])
    < /example>
    #
  </details>
  -
  </notes_20171108>

  </summary>
  '''
  def row_output(self, node=None, d_row=None, output_file=None, verbosity=0):
    me = 'row_output'

    required_arguments = ['node','d_row','output_file']
    if not all( required_arguments):
      raise ValueError(
        "{}:Not all required_arguments were given: {}".format(me, repr(required_arguments)))

    '''
    Keyword 'element_text' is a special keyword (may make a param later)
    that is used in a d_mining_map dictionary d_field2_field1 as a field2
    key value name to mean that the associated input row column value
    should be copied/written out into the xml output file in  the style of
    the xml tag's element content text rather than as any specific xml
    attribute value
    '''
    # print("{}: node={}".format(me,repr(node)))

    d_field2_field1 = node.get('d_field2_field1',None)

    if d_field2_field1 == None:
      # No mapping to produce output for this node, so just return
      print(">", file=output_file)
      return

    element_text = ''
    for field2, field1 in node['d_field2_field1'].items():
      if field2 == 'element_text':
        element_text = d_row.get(field1,'')
      else:
        value = d_row.get(field1,'')
        if value != '':
          print(' {}="{}"'
                .format(field2,value),end='',file=output_file)

    #Close the xml opening tag
    print(">", file=output_file,end='')

    if element_text != '':
      print("{}".format(element_text), end='', file=output_file)

    return
  #end:def row_output

  def row_children_visit(
    self,
    node=None,
    d_row=None,
    d_name_relation=None,
    composite_ids=None,
    output_file=None,
    verbosity=0 ):
    me = "row_children_visit"

    required_args = [node,  d_name_relation]
    if not all(required_args):
      raise ValueError("{}:Missing some required_args values in {}"
        .format(me,repr(required_args)))

    # On current input node/row, for each child  node relation,
    # recurse to visit it and output its data.
    node_relation_name = node['node1_name']

    depth = 0 if composite_ids is None else len(composite_ids)
    if depth > 0 and output_file is None:
      raise ValueError("Undefined output file")

    if verbosity > 0:
      print("\n{}: STARTING: parent relation={}, depth={}, composite_ids={} "
          .format(me, node_relation_name, depth, repr(composite_ids)))

    child_paths = node.get('child_paths', list())

    if not isinstance(child_paths, list):
      # Note: when start to interpret xml config, such error will be caught
      # elsewhere, when interpretting that config
      msg = "Error: " + msg
      raise ValueError(msg)

    if len(child_paths) > 0:
      for child_position,child_node in enumerate(child_paths):
        child_name_relation = child_node['node1_name']
        child_relation=d_name_relation[child_name_relation]
        child_rows = child_relation.sequence
        if verbosity > 0:
          print("{}: At list position={} child_node='{}', relation_name={},\nof type {}, will seek child_rows"
           .format(me, child_position, repr(child_node), child_name_relation,type(child_node)))

        if child_name_relation  == node_relation_name:
          relation = d_name_relation[node_relation_name]
          # register a 'revisit' so caller can ensure that if this is a depth==1 relation,
          # the output file will not be closed prematurely.
          relation.revisits += 1
          # print("nested xml tag {}".format(child_node['node2_name']))
          # Special convention to support nested xml tags for an input relation
          self.row_output_visit(node=child_node, composite_ids=composite_ids,
            d_row=d_row,d_name_relation=d_name_relation,
            output_file=output_file, verbosity=0)
          relation.revisits -= 1
        else:
          #print("{} seeking xpath={} with node_params={}".format(me,repr(xpath),repr(d_child_mining_map)))
          #children = node.findall(xpath, d_namespaces )
          # CRITICAL: make sure db.sequence() does select with order by the relation_namd_id
          # else hard-to-debug errors may result
          #for row_tuple in child_rows:
          while (1):
            column_values = child_relation.ordered_siblings.findall(composite_ids)
            if column_values is None:
              if verbosity > 0:
                print("No more rows for this sibling group")
              break;
            #TODO: add option to indicate str vs int column id values
            #initial versions: use int - as it implies row ordering
            for cid in range(depth):
              column_values[cid] = int(column_values[cid])

            if verbosity > 0:
              print("{}:=================Got sibling row column_values={}".format(me,column_values))
            sibling_id = column_values[depth]

            if verbosity> 0:
              print("{}: child row  using depth={}, column values={}, sibling_id='{}'"
                .format(me,  depth, repr(column_values), sibling_id))

            # Here, insert check that the parent composite ids of this child row all match
            # the given arguments
            # for cid in composite_ids ...
            for d in range(depth):
              # Consider: future spport of non-integer relation column id types(str vs int)
              if (int(composite_ids[d]) != int(column_values[d])):
                msg = ("{}: Child relation {}, sibling_id {} has parent relation {} with composite_ids={},"
                .format(me,child_name_relation, sibling_id, node_relation_name, repr(composite_ids)))
                msg += ("\nbut composite position={} mismatch: got row column values={}"
                  .format(d,  column_values))
                raise ValueError(msg)

            child_composite_ids = list() if composite_ids is None else list(composite_ids)
            if verbosity > 0:
              print("{}: adding sibling_id={} to child_composite_ids={}".format(me,sibling_id,
                  repr(child_composite_ids)))
            child_composite_ids.append(sibling_id)
            if verbosity > 0:
              print("{}:MAKING recursive call with child_composite_ids={} type={}"
                    .format(me,repr(child_composite_ids), type(child_composite_ids)))
            # create d_row from relation field/value names and column_values
            if verbosity > 0:
              print("{}:child relation={}, fields={},depth={},column_values={}"
                .format(me,child_name_relation, child_relation.fields, depth, column_values))

            d_row = { child_relation.fields[i]:v
                     for  i, v in enumerate(column_values)}

            d_row = { child_relation.fields[i]:column_values[i]
                     for  i in range(depth+1, len(column_values))}
            if verbosity> 0:
              print("===================d_row ={}".format(d_row))

            self.row_output_visit(node=child_node, composite_ids=child_composite_ids,
              d_row=d_row,d_name_relation=d_name_relation,
              output_file=output_file, verbosity=0)

            if verbosity> 0:
              print("{}: back from row_output_visit. Depth is back to {}".format(me,depth))

            # consider: copy column_values to d_row to return to caller...?
            '''
            note: If do do this--- tbd: outdent this to put it in childnode loop?
            if d_child_row is not None and len(d_child_row) > 0:
              for column_name, value in d_child_row.items():
                # Allowing this may be a feature to facilitate re-use of column functions
                # TEST RVP 201611215
                #if column_name in d_row:
                #    raise Exception(
                #        'node.tag={} duplicate column name {} is also in a child xpath={}.'
                #        .format(node.tag,column_name,xpath))
                d_row[column_name] = value
            '''
          #Finished visiting child_rows for this relation/node/sibling group
          if verbosity>0:
            print("{}: Finished visiting all composite_ids={} sibling rows of child relation"
                .format(me,composite_ids,child_name_relation))
      #Finished visting all child nodes/paths for this node
      if verbosity>0:
        print("{}: Finished visiting all child nodes/relations for composite_ids={}"
            .format(me,child_name_relation,composite_ids))
    #End check for some child nodes to visit.
    else:
      if verbosity > 0:
        print("{}:No child nodes - returning with depth={}".format(me,depth))

    if verbosity > 0:
      print("{}: depth={} RETURNING".format(me,depth))
    return
  # end:def row_children_visit

  '''
  future:
  Method row_post_visits(node=None, output_file=None, verbosity=None)

  Having visited all the children of this node/row, wrap up some loose end outputs
  and possibly calculate the return value for the return value of the caller
  (row_output_visit).
  '''
  def row_post_visits(self, node=None, output_file=None, verbosity=None):
    # set up column constants if any
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
  '''
  <summary>Method row_output_visit:
  To support one-big xml file of output vs one per output record,
  row_output_visit always checks output_file, and if None, it will output
    one xml file per primary relation row.

    If none, it constructs the output file name and opens a separate
    output file for each output record/object.

    </summary>
    <param name='node'>
    Either the root value (a dictionary) for the self.d_mining map or the
    dictonary value of a child node in the self.d_mining map.

    </param><param name='composite_ids'>
    The stack of composite_ids (relation_id values) of all parent rows and the
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

    The method arguments of  'composite_ids' and 'd_row' provide the parent
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
     - an inner loop through the node's child_paths is executed, where for each child_node:
    -- the sibling_id of the main relation row is appended to the given
      composite_ids
    -- a new d_row value is appended by appending this sibing row's values
     to the given d_row (they might be used by a recursive call in case a
     child_node node needs to use them to derive some values)
     -- a recursive call is made to row_output_visit for the child node


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

    </20171104 notes>
    <notes date='20171105'>
    Modified row_output_visit processing.
    Maybe change method name to
    node_output_dive() or

    translate_delve_extract() : because it does:
     (a) translate: the given d_row argument values into outputs and outpus them
     (b) delve: into child nodes of given row
          for each child_node, loop to extract sibling rows
          and for each child/sibling row found do:
     (d) recurse: call self at next level for each child_node row!

    Step 1 - context: assume caller has provided arg composite_ids, and it DOES include
    all composite ids for a specific row, and d_row includes the field values for
    this row.

    So in effect the caller has already 'visited' the node because
    it has read and populated the d_row argument with current single rows- value.
    Maybe call the method row_process_delve():

    Here, the given argument node also represents the mapping of this row
    field values -- the mining map or d_node_params is the same as used
    yesterday in fact.

    Step 2: sub-process output:
    given the output_file argument, use the node.d_field2_field1
    map and output the values

    Step 3: sub-process delve
    3a: take the child_paths list and for each child_node :
     use the node.node1_name to get the source object -
      (first cut is just an OreredRelation object, from arg d_name_relation).
    3a1: enter a for loop over the relation.sequence.ordered_siblings()
         for each child's-sibling, invoke again row_output_delve()

    That should about do it... 20171105t0926

    </notes date='20171105'>
    <notes date='20171106'>
    Resolved: first try will be similar to xml2rdb approach.
    Upon entry to this routine, the composite_ids will indicate one unique row,
    aka this object aka this node. Therefore, the caller is in charge of finding this row
    in the input data in the first place and sending the row with column values in as d_row.
    (Though in xml2rdb node_visit_output, the routine does find its own node values from
    lxml node.xxx calls, the important point is that an entry to either routine features a
    unique node/object/row as the key object. The fact that it may have other child
    objects/rows/nodes is beside that point. Code is included also in this method to
    proceed to visit all the child rows of each of the child nodes and invoke the
    next level of recursive calls.

    </notes date='20171106'>
    <notes date='20171107'>
    RE: argument d_name_relation - it is named to get current relation info,
    eg the relation sequences. However, when support filters per sequence,will
    need a tree of sequences because might have two simultanesous filters open on one
    relation, -- or may need a way to fork sequences..
    to hold place in one sequence/file for one fork, then expand the other via a
    child filter, but later come back and resume first sequence...? Maybe not..

    </notes date='20171107'>
    <notes date='20171108' return value is d_row, and ...
    </notes date='20171108'>
    </summary>
    </notes>
    '''
  def row_output_visit(self
    ,node=None ,d_name_relation=None,composite_ids=None ,d_row=None
    ,verbosity=0 ,output_file=None #make this a generic dataset later
    ):
    me = 'row_output_visit'

    # node1_name is the input dataset's relation name for the curent row.
    # For input databases it is a table or relation name,
    # and for input xml (maybe a future input source) it is an element tag name,
    # For input directory of 'tsf' files it is a file name of tab separated
    # ordered values per file line, etc.
    # And node2_name is the output dataset's name for a record or
    # parent group of data

    node1_name = node['node1_name'] # eg a relation name
    relation_name = node1_name
    depth = len(composite_ids)
    relation = d_name_relation[relation_name] if depth > 0 else None

    #The last composite id is this row's orderd sibling id within its sibling
    # group
    sibling_id = composite_ids[depth-1] if depth > 0 else None
    required_args = [node, d_name_relation, d_row]

    if not all(required_args):
      raise ValueError("{}:Missing some required_args values:\n{}"
        .format(me, repr(required_args)))

    if verbosity > 0:
      print("\n{}: STARTING: with args=\n{}".format(me, msg))
      if depth ==1:
        print("++++++++++++++++++{}:for depth 1 got sibling_id = '{}'"
            .format(me,sibling_id))

    output_file_for_each_record = 1

    if ( depth == 1 and output_file_for_each_record == 1
       and relation.revisits == 0
       ):
      # raise ValueError("Test Exit to clean up prints.")
      # fixme: check for sibling_id == '1' is a band-aid for testing, as it comports with
      # THE TEST DATA, but not abribtrary data... so fix this.
      # This node visit and child visits will generate some output data for the
      # main relation, which will produce (in conjunction with deeper calls)
      # its own entire xml output file.
      # Now open the output file for this row of this primary relation.
      output_file_name = (
        '{}{}_{}.xml'.format(self.output_folder,relation_name
        , str(sibling_id).zfill(self.zfill_id_count)))

      # On some Windows platforms, must specify utf-8-sig encoding
      # else errors in cp1252.py in encode or mishandled characters
      output_file = open(output_file_name,mode='w', encoding='utf-8-sig')
      relation.output_file = output_file
      if int(sibling_id) > 16605:
        print("relation.revisits={}, opened file {} for  sibling_id={}"
            .format(relation.revisits, output_file_name, sibling_id))

      if verbosity > 0:
        print("\n{}: *********** Created and Opened output file name={}".format(me,output_file_name))

    xml_tag_name = node['node2_name'] # eg an xml tag name

    # Output the prefix of opening tag for the xml element to be output to the output file
    if output_file is not None:
      if depth > 1:
        print(file=output_file)
      print("<{}".format(xml_tag_name), end='', file=output_file)

    #Output values mapped directly from this input row's column values
    if verbosity> 0:
      print("{}:calling row_output()".format(me))

    return_val = self.row_output(
      node=node, d_row=d_row, output_file=output_file, verbosity=0)

    # Next, call row_children_visit(node=node,verbosity=1)
    if verbosity> 0:
      print("{}: Calling row_children_visit".format(me))

    retval = self.row_children_visit(node=node,composite_ids=composite_ids,
        d_row=d_row,d_name_relation=d_name_relation, output_file=output_file,
        verbosity=verbosity)

    if verbosity > 0:
      print("{}: back from row_children_visit() call...".format(me))

    # future? - Next, call row_post_visit()

    # Now that all output is done for multiple == 1, set d_row = None, otherwise it's
    # presence would upset the caller.
    d_row = None

    msg = ("{}:FINISHED output tag name={},  depth={}, returning d_row={}"
       .format(me, xml_tag_name, depth,repr(d_row)))

    if verbosity> 0:
      print(msg)

    if depth == 1:
        print(file=output_file)

    print("</{}>".format(xml_tag_name), file=output_file,end='') #Close the xml opening tag

    if depth == 1:
        print(file=output_file)

    if (depth == 1 and verbosity > 0):
      print(
       '{}:depth={},output_file_for_each_record = {}, relation.revisits={}'
       .format(me,depth,output_file_for_each_record,relation.revisits))

    if ( depth == 1 and output_file_for_each_record == 1
         and relation.revisits == 0
       ):
       output_file.close()
       if int(sibling_id) > 16605:
        print("relation.revisits={}, Closed sibling_id={}"
            .format(relation.revisits, sibling_id))

    return None
  # end:def row_output_visit
# end class RelationMiner

# RUN PARAMS AND RUN
import datetime
import pytz
import os
from collections import OrderedDict

def rdb2xml_test():
  me = 'rdb2xml_test'

  import rdb2xml_configs.marctsf2xml as config

  # from dataset.ordered_relation import OrderedRelation
  from dataset.phd import PHD
  import dataset.phd

  d_mining_params = {'attribute_text':'text'}

  input_folder = etl.data_folder(
  linux="/home/robert/git/", windows="C:/rvp/data/",
  data_relative_folder='outputs/xml2rdb/ccila/')

  output_folder = etl.data_folder(
  # See xml2rdb.py study 'ccila' definition of folder_output_base
  linux="/home/robert/", windows="C:/users/podengo/",
  data_relative_folder='git/outputs/rdb2xml/ccila/')
  composite_ids = []
  d_mining_map = config.d_mining_map
  relation_miner = RelationMiner(d_mining_map=d_mining_map,
    d_mining_params=d_mining_params,output_folder=output_folder,
    verbosity=0
    )

  # create test set of relations to mine with rudimentary manual instantiations.
  print('{}:Constructing phd = PHD(...)'.format(me))
  phd = PHD(input_folder, output_folder,verbosity=1)

  # NOTE: Consider to IMPOSE a requirement to use '' as the parent of the
  # root relation.
  # It should facilitate some diagnostic and error reporting


  # Set up the input relation hierarchy via hard coded list
  parent_child_tuples = [
  ('','record'),
  ('record','controlfield'),
  ('record','datafield'),
  ('datafield','subfield')
  ]

  # Set up and perform a test run.
  for (parent_name, relation_name) in parent_child_tuples:
    relation = phd.add_relation(parent_name=parent_name
    , relation_name=relation_name
    ,verbosity=0)

    # add a sequence_ordered_siblings sequence for this relation
    all_rows = relation.sequence_all_rows()
    column_values = relation.sequence_column_values()
    relation.sequence = relation.sequence_ordered_siblings(all_rows=all_rows)
    relation.ordered_siblings = OrderedSiblings(ordered_relation=relation)

    # relation.revisitis is used to track number of nested revisits during
    # execution of the mining map, to make sure depth==1 output files are not
    # closed prematurely
    relation.revisits = 0

    msg=("Added relation '{}'' with sequence={} of type {}, and with parent {}"
      .format(relation_name,repr(relation.sequence),type(relation.sequence),
      parent_name))

    msg += ("and with ordered_siblings of type {}"
      .format(type(relation.ordered_siblings)))

    print('{}:{}'.format(me,msg))

  #Mine this config - visit all nodes and create outputs
  #note todo: add argument for d_name_relation for row_output_visit to use to
  #invoke correct sequence generator

  node_root = {
    'node1_name':'run_context',
    'node2_name':'run_context'
    ,'child_paths': [d_mining_map]
    }

  verbosity = 0
  composite_ids = []
  d_row = {
     'context.bib_id':'ZZ00004567', 'context.row_column1':'test1',
     'context.row_column2':'test2'}

  if verbosity > 0:
    print("{}.Using node_root={}.".format(me,repr(node_root)))
    print("{}:Calling relation_miner.row_output_visit()".format(me))

  # Main call
  relation_miner.row_output_visit(node=node_root
    ,d_name_relation=phd.d_name_relation
    ,composite_ids=composite_ids
    ,d_row=d_row
    ,output_file=None # Use NONE because we default to record-level output files
    ,verbosity=verbosity
    )

  return
#end:def rdb2xml_test():

rdb2xml_test()