'''
As of sqlalchemy 1.2.2, scanning google searches, it seems this is the best if
not only apparent way I could find to check if a table exists and then to drop
that table generically for engins psql and MySQL and possible others engines.
'''
def drop_if_exists(engine=None,table_name=None):

    # Drop table if it exists
    if engine.dialect.has_table(engine, table_name):
        conn = engine.raw_connection()
        cursor = conn.cursor()
        command = "drop table if exists {};".format(table_name)
        cursor.execute(command)
        conn.commit()
        cursor.close()
