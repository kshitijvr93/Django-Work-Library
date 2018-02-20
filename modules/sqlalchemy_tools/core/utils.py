'''
As of sqlalchemy 1.2.2, scanning google searches, it seems this is the best if
not only apparent way I could find to check if a table exists and then to drop
that table generically for engines psql and MySQL and possible others engines.
'''
def drop_if_exists(engine=None,table_name=None):

    required_params = ['engine','table_name']
    if not all(required_params):
        msg=("Did not get all required params '{}'".format(required_params))
        raise ValueError(msg)

    # If this table exists, drop it from the engine database
    if engine.dialect.has_table(engine, table_name):
        conn = engine.raw_connection()
        cursor = conn.cursor()
        command = "drop table if exists {};".format(table_name)
        try:
            cursor.execute(command)
            conn.commit()
        except Exception as ex:
            msg = ("Table_name={}, drop statement exception='{}'"
                .format(table_name,ex))
            raise ValueError(msg)

        cursor.close()
    return
#def drop_if_exists()
