'''
phd.py - Persistent Hierarchical Data
'''
import sys, os, os.path, platform,inspect

def get_path_modules(verbosity=0):
  env_var = 'HOME' if platform.system().lower() == 'linux' else 'USERPROFILE'
  path_user = os.environ.get(env_var)
  path_modules = '{}/git/citrus/modules'.format(path_user)
  if verbosity > 1:
    print("Assigned path_modules='{}'".format(path_modules))
  return path_modules
sys.path.append(get_path_modules())

import etl
from rdb2xml_configs.marctsf2xml import d_nodes_map

from collections import OrderedDict
import lxml

'''
A OrderedRelation object (PRO) represents a datastore of one or multiple named relations.

Each relation is represented by an ordered set of rows of column values where the first part
(of depth-quantity columns) of the column values are ordered indexes into the parent hierarchy of
nested containing relations. The rows are ordered within a relation/file by
the asending integer values of the ordered indexes, with last index varying
fastest throughout a sequence of the relation's rows.
The first index of a set would represent the index into the root relation of a hierarchical
set of relations.

Each relation may have a sequential row generator (here, a simple file reader) to generate the
sequence of ordered rows.
This simplest implementation simply cycles through a static file of rows/lines, each with tab
separated text values that represent a row, where the rows have been pre-ordered correctly by
its index columns, for example, through a pre-sort process.

Other versions of this object, not really much more complex versions, would have generators to
deliver a sequence of ordered rows that are stored in a database.
Internally, they could construct an sql query with the
appropriate order-by clauses and let the datase do the sorting in real-time at time of invocation.
Perhaps separate versions would be created for separate databases that use different language to
represent queries, or which have different ways to connect to them or retrieve data from queries.

In the first implementation of the simple file-reader object, assuming the rows have already been
sorted, this object is extremely simple, but it separates a chunk of functionality from calling
applications, so different versions of this can be implemented cleanly to handle different
data sources.

'''

class OrderedRelation:

    def __init__(self, order_depth=None,  relation_name=None, folder=None
        ,verbosity=0):

        me= 'OrderedRelation.__init__()'
        required_args = [order_depth, folder, relation_name]
        if not all(required_args):
            raise ValueError("{}:Missing some required_args values in {}"
                .format(me,repr(required_args)))

        self.folder = folder
        self.order_depth = order_depth
        self.relation_name = relation_name
        self.verbosity = verbosity
        self.verbosity = 0 if verbosity is None else int(verbosity)

        # Retrieve the field names (used for ordered_siblings() to create d_row generators)
        # Note: it is required that all rows in a referenced tab-separated valued
        # relation data file are pre-ordered by the first 'order_depth' quantity of columns,
        # which are the ordered ids or composite ids (because their composite
        # value is a unique key for the rows of the relation).
        # In comments about this object, the list of ids of  all but the last
        # composite id is called ancestor_ids, and the last id of a composite is
        # called the sibling_id for a row.

        input_file_name = '{}{}.tsf'.format(self.folder, relation_name)
        if verbosity > 0:
          print("{}: using input_file_name='{}'".format(me,input_file_name))
        with open(input_file_name) as input_tsf:
            for line in input_tsf:
                self.fields = line.strip().split('\t')
                if (self.verbosity > 0):
                    print("{}:Relation {} has {} fields={}."
                        .format(me,relation_name,len(self.fields),repr(self.fields)))
                break #ignore 'extra' lines in tsf file. We need only the first one.
        return
    # end method __init__

    '''
    method sequence_all_rows():

    This returns a sequence (via a generator) of all rows in the relation.

    FUTURE todo: will probably pass to __init__ a new argument, dsr, a data
    source reader object and replace all calls
    in this object to this method to not call open() but to rather call dsr.read() and remove this method.
    This generates a generator for a sequence of rows in this relation.
    '''

    def sequence_all_rows(self):
      me = 'OrderedRelation.sequence_all_rows()'
      data_file_name = '{}{}.txt'.format(self.folder, self.relation_name)
      row_count = 0

      with open(data_file_name, 'r') as input_file:
          for line in input_file:
            row_count += 1
            # Remove last newline and split out field/colum values by tab delimiter.
            column_values = line.replace('\n','').split('\t')
            yield row_count, column_values
      return

    '''
    Method ordered_siblings():

    This is a generator function that yields the subset of contained sibling rows
    (with respect to container lineage) rows in this relation, in order, that
    belong to the the current lineage of ancestors in a depth-first mining
    process.

    It punctuates the generated sequence of rows of sibling rows with a yield of the
    immediate_group_sentinel value, which defaults to None.
    We can add a parameter if needed to use another inter-sibling-group sentinel group
    other than None.

    When the immediate_group_sentinal defaults to None, this implies that
    only when two successive None values are returned has the generated sequence really
    ended.
    '''
    def sequence_ordered_siblings(self, immediate_group_sentinel=None, all_rows=None, integer_indexes=True):
        me = 'sequence_ordered_siblings'
        required_args = [all_rows]
        if not all(required_args):
            raise ValueError("{}:Missing some required_args values in {}"
                .format(me,repr(required_args)))

        ancestor_end_slice = self.order_depth - 1
        column_values_previous = None
        column_values_are_cached = False
        previous_ancestors = None

        for row_count, column_values in all_rows:
          if self.verbosity > 0:
            print("{}: From all_rows, got row_count={}, column_values={}".format(me,row_count,column_values))
          if column_values_are_cached:
            # We will yield the previously cached row
            column_values_are_cached = False
            if self.verbosity > 0:
              print("{}: yielding cached columns={}".format(me,repr(column_values_previous)))
            yield row_count - 1, column_values_previous

          # Continue to yield (within this loop or the next) current row's column values.
          # Save ancestor ordered indexes, used to detect change in sibling group
          if integer_indexes is True:
            current_ancestors = [int(i) for i in column_values[:ancestor_end_slice]]
          else:
            current_ancestors = column_values[:ancestor_end_slice]

          if previous_ancestors is not None and current_ancestors != previous_ancestors:
            # This is the start of a new sibling group. We will cache the values to use
            # in the next loop iteration and reset some housekeeping variables.

            if self.verbosity > 0:
              print("{}: ancestors changed: old={}, new={}"
                    .format(me,previous_ancestors,current_ancestors))

            column_values_previous = column_values
            column_values_are_cached = True
            if self.verbosity > 1:
                print('{}: Relation {}, line {} had first of new set of sibling rows: {}'
                  .format(me,self.relation_name,row_count,repr(column_values)))

            # Check for proper ordering of rows
            if current_ancestors < previous_ancestors:
              raise ValueError(
                "{}:Relation={},line {}, bad order. current_ancestors={}, previous_ancestors={}"
                .format(me,self.relation_name,row_count,
                repr(current_ancestors), repr(previous_ancestors)))
            # We yield now to signal the caller that the prior group of siblings has ended
            previous_ancestors = current_ancestors
            if self.verbosity > 0:
              print("{}: SAVED previous_ancestors={}".format(me,repr(previous_ancestors)))
            yield immediate_group_sentinel
          else:
            if previous_ancestors is None:
              previous_ancestors = current_ancestors
            # Current ancestors are same as previous, so
            # these current values belong to the current sibling group of rows
            if self.verbosity > 0:
              print("{}: yielding current group columns={}".format(me,repr(column_values_previous)))
            yield row_count, column_values
        # end for row_count, column_values in self.sequence_all_rows()

        # Send a final immediate_group_sentinel so the caller can easily detect the end of
        # the last group of immediate relatives or siblings
        yield immediate_group_sentinel
      # Note the python generator service will send a final None upon returning to let the
      # caller know the sequence has ended.
  # end def sequence_ordered_siblings : this returns a generator object


#end class OrderedRelation


''' PHD - Persistent Hierarchical Data
<params name=xml_mining_map_root>
This is an lxml root node of a mining map configuration.
Method __init__ uses this to create the linkages between the indicated data node
hierarchy.

For derived objects with relational database-based stores, where it is possible
to pre-check, the derived version of this method may also raise an Exception
if the mining map claims a child relation that is not really a child
relation, as can be inferred by relational database primary key constraints.

For the generic 'tsf' type file based object stores,
this basic __init__ assumes the first N data columns
define the partially ordered (poset) lineage ids, in sorted order, for any given row,
where N is the nesting depth of the relation given in the mining map.
</params>

'''

class PHD():

    def __init__(self, input_folder=None, output_folder=None, xml_mining_map_root=None
        ,verbosity=0 ):
        me = '__init__'
        required_args = [input_folder, output_folder]
        if len(required_args) != 0 and not all(required_args):
            raise ValueError("{}:Missing some required_args values in {}"
                .format(me,repr(required_args)))
        # test a marc txt file
        self.folder = input_folder
        self.relations = []
        self.d_name_relation = {}
        self.d_name_relation =  {}
        self.verbosity = verbosity

        # Get mining parameters from xml string
        pass
    '''
    Method add_relation:
    The first relation added is the root relation by definiton.
    It's parent_name should be '' or None.

    '''
    def add_relation(self, parent_name=None, relation_name=None,verbosity=None):
        me = 'PHD().add_relation()'
        required_args = [relation_name]
        if len(required_args) != 0 and not all(required_args):
            raise ValueError("{}:Missing some required_args values in {}"
                .format(me,repr(required_args)))
        if verbosity is None:
          verbosity = self.verbosity

        rlen = len(self.d_name_relation)
        print("{}:Starting with len of d_name_relation={}".format(me,rlen))
        sys.stdout.flush()

        if len(self.d_name_relation) == 0:
          order_depth = 1
          parent_relation = None
          pass
          # The first-added relation, this one, is defined to be the root of the hierarchy, and
          # no parent check is used. A warning may issue if it not None and not ''
        else:
          # Check that this parent_name is already added. It must be present.
          parent_relation = self.d_name_relation[parent_name]
          order_depth = parent_relation.order_depth + 1
          if parent_name not in self.d_name_relation.keys():
             raise ValueError('relation_name={}, has unknown parent_name={}.'
              .format(relation_name,parent_name))

        # check that the relation name is not a duplicate
        if relation_name in self.d_name_relation.keys():
             raise ValueError('relation_name={}, is duplicated.'
              .format(relation_name))

        #Create the relation as a partially-ordered set and store it with its parent indicated
        relation = OrderedRelation(
          folder=self.folder, order_depth=order_depth, relation_name=relation_name,
          verbosity=verbosity)

        if self.verbosity > 0:
          print("{}:Created and Registered root relation={}, relation_name='{}', order_depth={}"
            .format(me, repr(relation), relation.relation_name, order_depth))

        self.d_name_relation[relation_name] = relation
        return

#end class PHD

def testme(d_nodes_map=None):
    required_args = [d_nodes_map]
    if len(required_args) != 0 and not all(required_args):
        raise ValueError("{}:Missing some required_args values in {}"
            .format(me,repr(required_args)))
    me="testme"
    # This is configured to produce xml output files based on a set of approx
    # 16k marc input records, represented in a set of .txt files, each with its
    # per-line tab-delimited field name order represented in a .tsf file with
    # the same prefix. Thos prefixes are node or relation names, and they
    # are referenced in d_mining_map


    # Folder with relational .txt files and .tsf files describing marc xml
    # data for ccila project circa 20170707
    input_folder = etl.data_folder(
        linux="/home/robert/", windows="C:/users/podengo/",
        data_relative_folder='git/outputs/xml2rdb/ccila/')

    output_folder = etl.data_folder(
        # See xml2rdb.py study 'ccila' definition of folder_output_base
        linux="/home/robert/", windows="C:/users/podengo/",
        data_relative_folder='git/outputs/rdb2xml/ccila/')
    composite_ids = []

    print('{}: using input_folder={}, output_folder={}'
          .format(me, input_folder, output_folder))

    # node_visit_output(d_nodes_map,composite_ids)

    print('{}:Constructing phd = PHD(...)'.format(me))
    phd = PHD(input_folder, output_folder,verbosity=1)
    relation_name='record'
    # NOTE: IMPOSE a requirement to use '' as the parent of the root relation. It should facilitate
    # some diagnostic and error reporting

    parent_child_tuples = [
      ('','record'), ('record','controlfield'),('record','datafield'),('datafield','subfield')
    ]

    for (parent_name, relation_name)  in parent_child_tuples:
      print('{}:calling phd.add_relation(parent_name={},relation_name={})'
            .format(me,parent_name,relation_name))
      phd.add_relation(parent_name, relation_name=relation_name,verbosity=1)

    datafield = phd.d_name_relation['datafield']
    subfield = phd.d_name_relation['subfield']

    all_rows = subfield.sequence_all_rows()
    sibling_rows = subfield.sequence_ordered_siblings(all_rows=all_rows)

    nrow = 0
    for group_count in range(10):
      print("{}: Getting new set {} of sibling rows:".format(me, group_count))
      for row_tuple in sibling_rows:
          if row_tuple is None:
            print("Got row_tuple of None".format(me))
            break;
          row_count = row_tuple[0]
          column_values = row_tuple[1]
          print("{}: got row_count={}, column values={}"
                .format(me,row_count,repr(column_values)))

    print("{}:Done.".format(me))
    return
#####################
print("Calling testme()")
testme(d_nodes_map=d_nodes_map)
print ("Done!")
