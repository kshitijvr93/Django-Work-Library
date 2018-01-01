def make_mock_engines():
    # sqlalchemy engines -
    # recheck sqlalchemy docs occasionally and add here and test to make
    # sure formats are correct and proper support packages are installed
    d_ename_extension = {
      'mysql+pyodbc://./MyDb': {'extension': '_mysql.sql'},
      'sqlite:///:memory:': {'extension': '_sqlite.sql'},
      'postgresql://': {'extension':'_postgresql.sql'},
      'oracle+cx_oracle://': {'extension':'_oracle.sql'},
      'mssql+pyodbc://': {'extension':'_mssql.sql'},
    }

    engines = []
    for engine_name, extension in d_ename_extension.items():
        # https://stackoverflow.com/questions/870925/how-to-generate-a-file-with-ddl-in-the-engines-sql-dialect-in-sqlalchemy
        engine = create_engine(
          engine_name, strategy='mock',
           executor= lambda sql, *multiparams,
           **params:print(sql.compile(dialect=engine.dialect)))
        engines.append(engine)
    return engines
        
