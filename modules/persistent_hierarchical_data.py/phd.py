'''
phd.py - Persistent Hierarchical Data
'''
import lxml

'''
A HierarchicalRelation object (HRO) must have a parent Persistent Hierarchical Data object.

Notes:
A parent PHD object should create all of its HierarchicalRelation objects
into a self.some_collection (eg a list) and pass its self as the phd argument to
the creation of each HRO, to guarantee all objects in its list use the same phd.
That way, the phd object can easlily store some common data that is
accessed by each HRO object (wihtout having to pass various parameters when
a HRO is created), for example a folder for input or outputs that is used by
individual HROs.

The phd must also assure that each hierarchical relation is  created with
its correct parent relation and relation name.

'''

class HierarchicalRelation:

    def __init__(self, phd=None, parent_relation=None, relation_name=None):
        me = inspect.stack()[0][3]
        required_args = [phd, parent_relation, relation_name]
        if not all(required_args):
            raise ValueError("{}:Missing some required_args values in {}"
                .format(repr(me,required_args)))
        self.phd = phd
        self.parent_relation = parent_relation
        self.relation_name = relation_name
        self.d_row_previous = None
        self.d_row = {} #Dictionary of values for a row of this relation

        # Retrieve the field names (to create ordered_siblings d_row generators)
        input_file_name = '{}{}.tsf'.format(phd.folder, relation_name)
        with open(input_file_name) as input_tsf:
            for line in input_tsf:
                self.fields = line.split('\t')
                if (phd.verbosity > 0):
                    print("{}:Relation {} has {} fields={}."
                        .format(me,relation_name,len(self.fields),repr(self.fields)))
                break #ignore 'extra' lines rather than concatenate them or report error
        return

        '''
        Method sequence_siblings():
        This is a generator function that yields the sibling rows (with respect to parent lineage)
        rows in this relation, in order, that belong to the the current lineage of parents.

        If d_row_previous is None, it gets the next d_row from

        '''
        def ordered_siblings(self):


            pass



''' PHD - Persistent Hierarchical Data
<params name=xml_mining_map_root>
This is an lxml root node of a mining map configuration.
Method __init__ uses this to create the linkages between the indicated data node hierarchy.

For derived objects with relational database-based stores, where it is possible to pre-check,
the derived version of this method may also raise an Exception if the mining map claims a child
relation that is not really a child relation, as can be inferred by relational database primary
key constraints.

For the generic 'tsf' type file based object stores,
this basic __init__ assumes the first N data columns
define the hierarchical lineage ids, in sorted order, for any given row,
where N is the nesting depth of the relation given in the mining map.
</params>

'''

'''

class PHD():

    def __init__(self, xml_mining_map_root=None):
        me = '__init__'
        required_args = [xml_mining_map_root]
        if not all(required_args):
            raise ValueError("{}:Missing some required_args values in {}"
                .format(repr(me,required_args)))
        self.h_relations = []

        # Get mining parameters from xml string
        pass
