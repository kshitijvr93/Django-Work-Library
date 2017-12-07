'''
Merge multiple tabls without repoint join column create table 20131022
'''
if (1==1):
    def get_od_col_spec(conn=conn, table=table):
        """
        Return OrderedDict for table with key of column name, value of column type.
        """
        od_column_type = OrderedDict()
        sized_types=["nvarchar","varchar"]
        for result in conn.cursor().columns(table=table):
            #TODO: add support for decimal types here too if ever needed.
            tspec = result.type_name
            if tspec in sized_types:
                tspec = tspec + ("(%d)" % result.column_size)
            if result.is_nullable != "YES":
                tspec =  tspec + " not null"
            else:
                tspec = tspec + " null"
            od_column_type[result.column_name] = tspec
        return od_column_type
    def query_left_join(conn=conn, default_join_column=None, od_table_joincolumn=None):
        """
        Return the sql to do a left-join on join column of multiple tables.
        Parameters:
        ===========
        conn: pyodbc connection
        -----------------------
        -- a connection to a pyodbc database
        default_join_column: string (optional)
        ---------------------------
        -- default column name to use in all table to join on
        -- If this is not given or None, then a join column name must be
           given for each table in od_table_joinname
        od_table_joincolumn: OrdereDict
        -------------------------------
        -- key is a table name. First is the "leftmost" table with which to
           control the left join(s) of all other table(s).
        -- value is either:
          -- a single column name of a column to join on for the table.
          -- or None, in which case the default_join_column will be used
        """
        q_columns = ""
        column_delim = " "
        q_tables = ""
        first_table = 1
        table_delim = " "
        total_columns = 0
        q_join = ""
        for idx,(table,join_column) in enumerate(od_table_joincolumn.items()):
            # Set join_column for this table
            q_columns += '\n' # line separator between columns of diff tables
            if join_column is None:
                if default_join_column is None:
                    raise ValueError(
                      "Table %s has no join column and default is None.")
                join_column = default_join_column
            #print "table ='%s', join_column='%s'" % (table,join_column)
            # Build parts of the select query for this table
            if first_table:
                left_join_column = join_column
                q_tables=("\n %s t%s " % (table,repr(idx)))
                q_join = "  %s" % table
                table_count = 4
            else:
                table_count -= 1
                if table_count == 0:
                    table_count = 4
                    q_join += "\n"
                q_tables += (
                    "\nLEFT JOIN %s t%s ON t0.%s = t%s.%s" %
                    (table, repr(idx), left_join_column, str(idx), join_column))
                q_join += ", %s" % table
            # get column names for this table (ignore types)
            od_col_spec = get_od_col_spec(conn,table)
            # build colnames with tN alias table prefix
            cols_per_line = 4
            count = cols_per_line
            for colname in od_col_spec.keys():
                colname = colname.lower()
                #print ("colname='%s', join_column='%s'" % (colname, join_column))
                if first_table == 0 and colname == join_column:
                    # If join column is same name as in first table, SQL will fail,
                    # and even if it is not, it is a waste of space, so skip it.
                    continue
                total_columns += 1
                q_columns += ("%s t%s.%s" % (column_delim, repr(idx), colname))
                count -= 1
                if count == 0:
                    count = cols_per_line
                    q_columns += "\n"
                column_delim = ","
            # end for colname
            first_table = 0
        # end for idx(table,join_column)
        sql = ("SELECT%s\nFROM %s\n"
               % (q_columns, q_tables))
        return (sql, total_columns)
    # Test
    # TODO: create table school per glue.sas lines 434-438 first..
    # school ds tables to merge:
    # see glue.sas lines 393, 429
    od_school_joincolumn=OrderedDict([
         ('mean_g_bcrxid_items','g_bcrxid_items')
        ,('ttest_school_w','g_bcrxid')
        ,('ttest_school_s','g_bcrxid')
        ,('ttest_school_c','g_bcrxid')
        ,('ttest_school_r','g_bcrxid')
        ,('ttest_school_m','g_bcrxid')
        ])
    #schoolds2 line 430
    od_school2_joincolumn=OrderedDict([
         ('mean_g_bcrxid_items','g_bcrxid_items')
        ,('cascade_district_w','g_bcrxid')
        ,('cascade_district_s','g_bcrxid')
        ,('cascade_district_c','g_bcrxid')
        ,('cascade_district_r','g_bcrxid')
        ,('cascade_district_m','g_bcrxid')
        ])
    # District ds tables to merge: see glue.sas lines 392,
    od_district_joincolumn=OrderedDict([
         ('mean_g_dcrxid_items','g_dcrxid_items')
        ,('cascade_district_w','g_dcrxid')
        ,('cascade_district_s','g_dcrxid')
        ,('cascade_district_c','g_dcrxid')
        ,('cascade_district_r','g_dcrxid')
        ,('cascade_district_m','g_dcrxid')
        ,('ttest_district_w','g_dcrxid')
        ,('ttest_district_s','g_dcrxid')
        ,('ttest_district_c','g_dcrxid')
        ,('ttest_district_r','g_dcrxid')
        ,('ttest_district_m','g_dcrxid')
        ,('peercompare_out','g_dcrxid')
        ])
    (sql, ncol) = query_left_join(conn=conn, od_table_joincolumn=od_district_joincolumn)
    print("total columns = %d" % ncol)
    print("sql='%s'" % sql)
    #
