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
from rdb2xml_configs.marctsf2xml import d_mining_map

from collections import OrderedDict
import lxml
from dataset.ordered_relation import OrderedRelation,OrderedSiblings

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
        return relation
      # end:def add_relation

#end class PHD

def testme(d_mining_map=None):
    required_args = [d_mining_map]
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

    # node_visit_output(d_mining_map,composite_ids)

    print('{}:Constructing phd = PHD(...)'.format(me))
    phd = PHD(input_folder, output_folder,verbosity=1)
    relation_name='record'
    relation_name='controlfield'
    # NOTE: IMPOSE a requirement to use '' as the parent of the root relation.
    # It should facilitate some diagnostic and error reporting.

    parent_child_tuples = [
      ('','record'), ('record','controlfield'),('record','datafield'),
      ('datafield','subfield')
    ]

    for (parent_name, relation_name)  in parent_child_tuples:
      print('{}:calling phd.add_relation(parent_name={},relation_name={})'
            .format(me,parent_name,relation_name))
      phd.add_relation(parent_name, relation_name=relation_name,verbosity=0)


    datafield = phd.d_name_relation['datafield']
    controlfield = phd.d_name_relation['controlfield']
    control_ordered_siblings = OrderedSiblings(ordered_relation= controlfield)

    subfield = phd.d_name_relation['subfield']

    all_rows = datafield.sequence_all_rows()
    sibling_rows = subfield.sequence_ordered_siblings(all_rows=all_rows)

    nrow = 0
    for group_count in range(100):
      print("{}: Getting new set {} of sibling rows:".format(me, group_count))
      for index_count, row_tuple in enumerate(sibling_rows):
          if row_tuple is None:
            print("Got row_tuple of None".format(me))
            break;
          row_count = row_tuple[0]
          column_values = row_tuple[1]
          print("{}: got row_count={}, column values={}"
                .format(me,row_count,repr(column_values)))
    parent_ids = ['1']

    print("Calling control_ordered_siblings.next_by_parent_ids(parent_ids={})"
        .format(repr(parent_ids)))
    a = 77
    while (1 == 1):
        next_result = control_ordered_siblings.next_by_parent_ids(parent_ids=parent_ids)
        if next_result is None:
          break;
        print("Got next_result = {}".format(next_result))

    print("{}:Done.".format(me))
    return
#####################
print("Calling testme()")
testme(d_mining_map=d_mining_map)
print ("Done!")
