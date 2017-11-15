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
import sys

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
        with open(input_file_name,mode='r',encoding='utf-8') as input_tsf:
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

    def sequence_column_values(self):
      me = 'OrderedRelation.sequence_column_values()'
      data_file_name = '{}{}.txt'.format(self.folder, self.relation_name)
      #print("{}:----------------Opening data_file_name='{}'".format(me,data_file_name))

      with open(data_file_name, 'r', encoding='utf-8-sig',errors='replace') as input_file:
          for line in input_file:
            # Remove last newline and split out field/colum values by tab delimiter.
            column_values = line.replace('\n','').split('\t')
            yield column_values
      return

    def sequence_all_rows(self):
      me = 'OrderedRelation.sequence_all_rows()'
      data_file_name = '{}{}.txt'.format(self.folder, self.relation_name)
      row_count = 0
      #print("{}----------------Opening data_file_name='{}'".format(me,data_file_name))

      with open(data_file_name, 'r', encoding='utf-8-sig',errors='replace') as input_file:
          for line in input_file:
            row_count += 1
            # Remove last newline and split out field/colum values by tab delimiter.
            column_values = line.replace('\n','').split('\t')
            yield row_count, column_values

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

class OrderedSiblings:
  '''
  This uses OrderedRelation as a member.
  It might be better to base it on OrderdRelation later...but this way we can have multiple sequences
  open on the same relation.
  NOTE: all parent_id  values and row column values are strings.
  '''
  def __init__(self, ordered_relation=None,verbosity=0):
    required_args = [ordered_relation]
    if not all(required_args):
      raise ValueError("Missing some required_args values in {}"
      .format(repr(required_args)))

    self.ordered_relation = ordered_relation
    #self.all_rows = ordered_relation.sequence_all_rows()
    self.column_values = ordered_relation.sequence_column_values()
    self.verbosity = verbosity

    #self.next_result = next(self.all_rows)
    #self.next_row = self.next_result[1]
    self.next_row = next(self.column_values)

    self.parent_depth = 0
    if ordered_relation.order_depth > 1:
       self.parent_depth = ordered_relation.order_depth - 1
    self.next_parent_ids = [int(x) for x in self.next_row[:self.parent_depth]]
  # end: def __init__

  def findall(self, parent_ids=None):
    '''
    Given :

    <param name='parent_ids'> the parent composite id values to use to group the
    siblings in this relation.
    </param>

    <processing>
    Every relation has a self.parent_depth value preassigned, and the root or hierarchical relation,
    has a parent ids depth/length of 0, with no parent ids.
    This method always returns a None value between rows that have a different parent id, otherwise
    it will return either
    (1) the first row column values after its previous call returned None, or
    (2) the next data row that has the same parent_ids as the previously returned row.
    This behavior allows a caller to provide the parent ids to loop through the next desired set
    of 'sibling rows' it requires, and also detect the end of a 'sibling group' of child relation rows
    by observing the "None" return value that this method returns in its next invocation after it returns
    the last row of a sibling group of rows.

    So, if len(parent_ids) == 0, then this relation is the primary
    relation, and each successive call to findall with the same parent_ids
    will simply alternate between:
    (1) returning the next successive row from the underlying tsv data file, and
    (2) returning None.
    After it has returned the last row of child row data, all successive calls
    with the same parent ids will return None.

    In short, return None if no rows remain in a sibling group, else return next
    child sibling row's column_values[]

    </processing>

    Return the parent's next ordered sibling row in this relation.
    Return None if there is no next sibling for the parent.

    EXCEPTIONS:
    (1) Invalid Parents exception due to wrong parent generation/depth: -- see code comments.

    (2) Invalid Parents due to input data integrity exception:
    Raise an exception if the parent_ids are greater than the sibling ids.
    This is an error because it indicates that the parent_ids for the next sibling row must have
    been skipped/not found and so therefore not used to retrieve the sibling row, and so that
    sibling row was abandoned (not called for, not picked up) by its proper parent.
    xml2rdb should produce perfect integer-id-sorted tsf,tsv files, so this exception might only happen
    if a tsv file was manually un-sorted or a row was deleted from a parent tsv file or inserted into a
    child tsv file.

    '''
    me = 'findall'

    # Consider: register and support mixed string or integer id types, specified per relation.
    # and require input data to be sorted by the apt types.
    # In current method, we require all integer ids and input data sorted by ascending integer ids.
    parent_ids = [int(x) for x in parent_ids]

    if self.parent_depth != len(parent_ids):
        # This findall() call was invoked outside the context of its true parent.
        raise ValueError("Parent_depth={} but len(parent_ids)={}"
                 .format(self.parent_depth,len(parent_ids)))
    if self.verbosity > 0 :
      print("{}:Given parent_ids={}".format(me,repr(parent_ids)))

    if self.parent_depth == 0:
      # Upon instantiation, the first row of this relation was stored in self.next_row
      # And start by storing it it tmp_row

      tmp_row = self.next_row
      if self.next_row is not None:
        # Try to get another row of column values from this relation
        try:
          self.next_row = next(self.column_values)
          self.next_parent_ids = [int(x) for x in self.next_row[:self.ordered_relation.order_depth-1]]
        except StopIteration:
          return None
      else:
        # There is no next row of this sibling group. Just return none
        return None
      #print("{}:returning row={}".format(me,tmp_row))
      return tmp_row

    # If depth was 0, code above returned. Here, depth is > 0
    if parent_ids < self.next_parent_ids:
      # If 'lesser' parent_ids, it is OK for parent to call again later with
      # increasing parent_ids until caller finds this row
      #print("{}:returning None".format(me))
      return None
    elif parent_ids == self.next_parent_ids:
      tmp_row = self.next_row
      if self.next_row is not None:
        # We have not run out of relation rows, so try to get another
        try:
          self.next_row = next(self.column_values)
        except StopIteration:
          return None
        # Store the next row's parent_ids so we can detect bad parents in next call.
        self.next_parent_ids = [int(x) for x in self.next_row[:self.ordered_relation.order_depth-1]]
      else:
        #print("{}:returning None".format(me))
        return None
      #print("{}:returning row={}".format(me,tmp_row))
      return tmp_row
    else:
      # Parent_ids skipped over an available child row  - Fatal Exception:
      raise ValueError("Given parent_ids={}, but next_parent_ids={}. Missing parent abandoned orphans! Fatal Error."
        .format(repr(parent_ids),repr(self.next_parent_ids)))

    return
  # end:def findall

  def findall_old(self, parent_ids=None):
    '''
    Given the parent composite id values, return the parent's next ordered sibling
    row in this relation.
    Return None if there is no next sibling for the parent.
    It is an exception if the next available sibling has an order that preceds
    that of the given parent.
    If there are no composite id values, return the next ordered row of the relaton
    Note: every relation must have a depth, but the root hierarchical relation,
    with a depth of 1, has no parent ids, so just return every row for it.

    Return None if no rows, else return column_values[]
    '''
    me = 'findall_old'
    #todo: formalize type of id!
    parent_ids = [int(x) for x in parent_ids]
    if self.parent_depth != len(parent_ids):
        raise ValueError("Parent_depth={} but len(parent_ids)={}"
                 .format(self.parent_depth,len(parent_ids)))
    if self.verbosity > 0:
      print("{}:Using parent_ids={}".format(me,repr(parent_ids)))

    if self.parent_depth == 0:
      tmp_row = self.next_row
      if self.next_result is not None:
        try:
          self.next_result = next(self.all_rows)
          self.next_row = self.next_result[1]
          self.next_parent_ids = [int(x) for x in self.next_row[:self.ordered_relation.order_depth-1]]
        except StopIteration:
          return None
      else:
        #print("{}:returning None".format(me))
        return None
      #print("{}:returning row={}".format(me,tmp_row))
      return tmp_row

    #todo:Make sure these are ints before comparing , or give int/str order options
    if parent_ids < self.next_parent_ids:
      # If 'lesser' parent_ids, it is OK for parent to call again later with
      # increasing parent_ids until caller finds this row
      #print("{}:returning None".format(me))
      return None
    elif parent_ids == self.next_parent_ids:
      tmp_row = self.next_row
      if self.next_result is not None:
        try:
          self.next_result = next(self.all_rows)
        except StopIteration:
          return None
        self.next_row = self.next_result[1]
        self.next_parent_ids = [int(x) for x in self.next_row[:self.ordered_relation.order_depth-1]]
      else:
        #print("{}:returning None".format(me))
        return None
      #print("{}:returning row={}".format(me,tmp_row))
      return tmp_row
    else:
      # Parent_ids skipped over an available child row  - Fatal Exception:
      raise ValueError("Given parent_ids={}, but next_parent_ids={}. You abandoned orphans! Fatal Error."
        .format(repr(parent_ids),repr(self.next_parent_ids)))

    return

#end:class OrderedSiblings
