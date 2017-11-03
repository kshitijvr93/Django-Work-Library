'''
NOTE: this was copied from within file phd.py on 2011101 -- if further testing causes changes, there,
then it should probably be recopied here,, along with some test cases.


A OrderedRelation object (ORO) represents a datastore of one or multiple named relations.

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
    def sequence_ordered_siblings(self, immediate_group_sentinel=None,
        all_rows=None, integer_indexes=True):

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
            print("{}: From all_rows, got row_count={}, column_values={}"
                  .format(me,row_count,column_values))
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
