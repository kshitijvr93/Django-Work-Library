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
A PosetRelation object (PRO) represents a datastore of one or multiple named relations.

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

class PosetRelation:

    def __init__(self, relation_depth=None,  relation_name=None, folder=None
        ,verbosity=0):

        me= 'PosetRelation.__init__()'
        required_args = [relation_depth, folder, relation_name]
        if not all(required_args):
            raise ValueError("{}:Missing some required_args values in {}"
                .format(me,repr(required_args)))

        self.folder = folder
        self.relation_depth = relation_depth
        self.relation_name = relation_name
        self.verbosity = verbosity
        self.d_row_previous = None
        self.d_row = {} #Dictionary of column name-value pairs for a row of this relation
        self.verbosity = 0 if verbosity is None else int(verbosity)

        # Retrieve the field names (used for ordered_siblings() to create d_row generators)
        # Note: in future, may change to let phd provide d_rows as an argument to
        # facilitate expanding to new types of data sources
        # Note: it is required that all rows in a relation data file are pre-ordered by
        # the partially ordered (poset) ids.

        input_file_name = '{}{}.tsf'.format(self.folder, relation_name)
        if verbosity > 0:
          print("{}: using input_file_name='{}'".format(me,input_file_name))
        with open(input_file_name) as input_tsf:
            for line in input_tsf:
                self.fields = line.strip().split('\t')
                if (self.verbosity > 0):
                    print("{}:Relation {} has {} fields={}."
                        .format(me,relation_name,len(self.fields),repr(self.fields)))
                break #ignore 'extra' lines rather than concatenate them or report error
        return
    # end method __init__

    '''
    method sequence_rows():

    FUTURE todo: will probably pass to __init__ a new argument, dsr, a data
    source reader object and replace all calls
    in this object all calls to this method to rather call dsr.read() and remove this method.
    This generates a generator for a sequence of rows in this relation.
    '''

    def sequence_all_rows(self):
      data_file_name = '{}{}.txt'.format(self.folder, self.relation_name)
      line_count = 0
      with open(data_file_name, 'r') as input_file:
          for line in input_file:
            print(line)
            line_count += 1
            if line_count > 10:
              return
            d_rows = line.split('\t')
            yield d_rows
      return

    '''
    Method ordered_siblings():

    This is a generator function that yields the subset of contained sibling rows
    (with respect to container lineage) rows in this relation, in order, that
    belong to the the current lineage of ancestors in a depth-first mining
    process.

    It uses the main sequence_all_rows generated sequence for the relation.
    It yields None when all the siblings of the current ancestors have been
    yielded. Otherwise, it yields d_row, which is next current sibling row
    for the current ancestor relations.

    if self.d_row_previous is not None:
         # save d_row_previous to d_row, setsd_row_previous to None and return d_row
    else: #self.d_row_previous is None
         # Summon the the next row from the sequence_all_rows
         if return_value is None:
             #
    gets the next d_row from data_source
    If the retrieved d_row

    '''
    def sequence_ordered_siblings(self):
        me = 'sequence_ordered_siblings'
        if self.d_row_previous is not None:
            # Here, in the previous call, we cached a previous row that will start a
            # new set of sibling rows contained by a new lineage, so return it.
            d_row_temp = self.d_row_previous
            self.d_row_previous = None
            # reset the container ids
            self.container_ids = d_row_temp[:self.relation_depth]
            if self.verbosity > 0:
                print('{}: Relation {} first of new set of sibling rows: {}'
                      .format(me,self.relation_name,repr(d_row_temp)))
            yield d_row_temp
        else:
            #Get relation rows from sequence_all_rows
            nrows = 0
            for d_row in self.sequence_all_rows():
                nrows += 1
                if d_row is None or nrows > 5:
                    break
                # If any order indexes except this one (ie, containing ancestor ids)
                # changed, we have a new set of siblings
                ancestor_count = self.relation_depth -1
                if ( self.d_row_previous is not None
                    and d_row[:ancestor_count] != self.d_row_previous[:ancestor_count] ):
                    if self.verbosity > 0:
                        print("New ancestors: old {} vs new {}".format(
                          self.d_row_previous[:ancestor_count] , d_row[:ancestor_count]))
                    self.d_row_previous = d_row
                    yield None
                yield d_row
# end def sequence_ordered_siblings : this returns a generator x,
# and caller does for my_row in x: do something...


#end class PosetRelation


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
    def add_relation(self, parent_name=None, relation_name=None):
        me = 'PHD().add_relation()'
        required_args = [relation_name]
        if len(required_args) != 0 and not all(required_args):
            raise ValueError("{}:Missing some required_args values in {}"
                .format(me,repr(required_args)))

        rlen = len(self.d_name_relation)
        print("{}:Starting with len of d_name_relation={}".format(me,rlen))
        sys.stdout.flush()

        if len(self.d_name_relation) == 0:
          relation_depth = 1
          parent_relation = None
          pass
          # The first-added relation, this one, is defined to be the root of the hierarchy, and
          # no parent check is used. A warning may issue if it not None and not ''
        else:
          # Check that this parent_name is already added. It must be present.
          parent_relation = self.d_name_relation[parent_name]
          relation_depth = parent_relation.relation_depth + 1
          if parent_name not in self.d_name_relation.keys():
             raise ValueError('relation_name={}, has unknown parent_name={}.'
              .format(relation_name,parent_name))

        # check that the relation name is not a duplicate
        if relation_name in self.d_name_relation.keys():
             raise ValueError('relation_name={}, is duplicated.'
              .format(relation_name))

        #Create the relation as a partially-ordered set and store it with its parent indicated
        relation = PosetRelation(
          folder=self.folder, relation_depth=relation_depth, relation_name=relation_name,
          verbosity=self.verbosity)

        if self.verbosity > 0:
          print("{}:Created and Registered root relation={}, relation_name='{}', relation_depth={}"
            .format(me, repr(relation), relation.relation_name, relation_depth))

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

    for (parent_name,relation_name)  in parent_child_tuples:
      print('{}:calling phd.add_relation(parent_name={},relation_name={})'
            .format(me,parent_name,relation_name))
      phd.add_relation(parent_name, relation_name=relation_name)

    datafield = phd.d_name_relation['datafield']
    subfield = phd.d_name_relation['subfield']

    i = 0
    while (1):
        i += 1
        if i > 3 :
            break
        sibling_rows = subfield.sequence_ordered_siblings()
        nrow = 0
        for d_row in sibling_rows:
            print("Yes, d_row={}".format(repr(d_row)))
            nrow += 1;
            if (nrow > 10):
              print("Hit nrow limit in testme()")
              break;

    print("Done!")
    print("Done!")

    return
#####################
print ("YO!")
print("Calling testme()")
testme(d_nodes_map=d_nodes_map)
