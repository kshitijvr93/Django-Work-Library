'''
elsevier_updates.py

This program has quickly fallen into deprecation.

Rather, xml2rdb can be and is used to translate uf elsevier
harvestd MD info to MAW or other db tables, due to
2018 January improvements to xml2rdb to also do bulk inserts
for mysql and postgresql.

NOTE: Since xml2rdb is still simple to launch/run by hand,
there is no simple utility (yet) embodied in the MAW project
to launch this particular conversion/insertion option.
I'll probably call it 'elsevier_api_to_rdb.py'

This queries Elsevier apis to update the Marshaling Application
Website (MAW) database, aka the UF Library UFDC Marshaling database.

The MAW database itself may reside on another server than the
Marshaling application webserver.
'''

#imports

'''
<summary method_name='elsevier_md_doc_updates'>
This program selects elsevier information from the main "*doc" table that is the
output of an xml2rdb run on elsevier metadata information per configuration
in this project's .../modules/xml2rdb_configs/elsevier.py

The program updates certain marshaling database table columns in its elsevier
items  data table, based on the pii (publisher item identifier) value that is
common to the *doc input table and the marshal database output table.
</summary>

<param name="engine_source_nick_name">
The database engine nick_name that has a set of tables with
Elsevier information, specifically a *doc table. Other potential source
tables may be utilized in the future.
</param>

<params name='elsevier_doc_table_name'>
The table name that has elsevier document information to use to update
MAW table(s).
</param>

<return>
None (or raises exception)
</return>

'''
def elsevier_md_doc_updates(engine_source_nick_name=None,
    elsevier_doc_table_name=None, output_engine_nick_name=None,
    output_table_name=None):



    pass
