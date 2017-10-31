'''
phd.py - Persistent Hierarchical Data
'''
import lxml

'''
A HierarchicalRelation object (HRO) must have a container Persistent
Hierarchical Data object.

Notes:
A container PHD object should create all of its HierarchicalRelation objects
into a self.some_collection (eg a list) and pass its self as the phd
argument to the creation of each HRO, to guarantee all objects in its list
use the same phd.
That way, the phd object can easlily store some common data that is
accessed by each HRO object (wihtout having to pass various parameters when
a HRO is created), for example a folder for input or outputs that is used by
individual HROs.

The phd must also assure that each hierarchical relation is  created with
its correct container relation and relation name.

'''

class HierarchicalRelation:

    def __init__(self, phd=None, container_relation=None, relation_name=None
        ,verbosity=0):
        me = inspect.stack()[0][3]
        required_args = [container_relation, relation_name]
        if not all(required_args):
            raise ValueError("{}:Missing some required_args values in {}"
                .format(repr(me,required_args)))
        if (phd is not None):
            pass
        self.phd = phd
        self.verbosity = verbosity
        self.container_relation = container_relation
        self.relation_name = relation_name
        self.d_row_previous = None
        self.d_row = {} #Dictionary of values for a row of this relation

        # Retrieve the field names (used for ordered_siblings() to create d_row generators)
        # Note: in future, may change to let phd provide d_rows as an argument to
        # facilitate expanding to new types of data sources
        # Note: it is required that all rows in a relation data file are pre-ordered by
        # the hierarchical ids.

        input_file_name = '{}{}.tsf'.format(phd.folder, relation_name)
        with open(input_file_name) as input_tsf:
            for line in input_tsf:
                self.fields = line.split('\t')
                if (phd.verbosity > 0):
                    print("{}:Relation {} has {} fields={}."
                        .format(me,relation_name,len(self.fields),repr(self.fields)))
                break #ignore 'extra' lines rather than concatenate them or report error

        return
    # end method __init__

	'''
    method sequence_rows():

	FUTURE todo: will probably pass to __init__ a new argument, dsr, a data source reader object and replace all calls
	in this object all calls to this method to rather call dsr.read() and remove this method.
	This generates a generator for a sequence of rows in this relation.
	'''

	def sequence_all_rows(self):
	    data_file_name =  '{}{}.txt'.format(self.phd.folder, self.relation_name)
	    with open(data_file_name, 'r') as input_file:
	        for line in input_file:
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
            self.container_ids = d_row_temp[:self.depth]
            if self.verbosity > 0:
                print('{}: Relation {} first of new set of sibling rows: {}'
                      .format(me,self.relation_name,repr(d_row_temp)))
            yield d_row_temp
        else:
            #Get relation rows from sequence_all_rows
            for d_row in self.sequence_all_rows():
                if d_row is None:
                    break
                # If any container sibling_ids changed, we have a new container
                if ( self.container_ids is not None
                    and d_row[:self.depth] != self.container_ids[:self.depth] ):
                    if self.verbosity > 0:
                        print("New ancestors: old {} vs new {}"
                          .format(self.container_ids, d_row[:self.depth])))
                    self.d_row_previous = d_row
                    yield None
                yield d_row

        return



        pass

#end class HierarchicalRelation



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
define the hierarchical lineage ids, in sorted order, for any given row,
where N is the nesting depth of the relation given in the mining map.
</params>

'''


class PHD():

    def __init__(self, folder=None, xml_mining_map_root=None):
        me = '__init__'
        required_args = []
        if len(required_args) != 0 and not all(required_args):
            raise ValueError("{}:Missing some required_args values in {}"
                .format(repr(me,required_args)))
        self.h_relations = []
        # test a marc txt file
        self.folder = 'hard coded folder to relations .txt files...'

        # Get mining parameters from xml string
        pass

    def add_relation(relatnion_name=relation_name)
        pass


#end class PHD

def testme(d_mining_map=None):
    required_args = []
    if len(required_args) != 0 and not all(required_args):
        raise ValueError("{}:Missing some required_args values in {}"
            .format(repr(me,required_args)))
    # This is configured to produce xml output files based on a set of approx
    # 16k marc input records, represented in a set of .txt files, each with its
    # per-line tab-delimited field name order represented in a .tsf file with
    # the same prefix. Thos prefixes are node or relation names, and they
    # are referenced in d_mining_map

    phd = PHD()

    # Folder with relational .txt files and .tsf files describing marc xml
    # data for ccila project circa 20170707
    input_folder = etl.data_folder(linux="/home/robert/", windows="U:/",
        data_relative_folder='data/outputs/xml2rdb/ccila')

    phd.h_relations[0] = HierarchicalRelation()

    i = 0
    while (1):
        i += 1
        if i > 3 :
            break
        while d_row = phd.h_relation.sequence_all_rows():
            print("d_row={}".format(repr(d_row)))
