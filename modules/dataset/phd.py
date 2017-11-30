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
from dataset.ordered_relation import OrderedRelation

from collections import OrderedDict
import lxml

#from dataset.ordered_relation import OrderedRelation


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

#end class PHD
