'''
Flesh this out with experience...as needed.

I needed to do this for one test application that attempted to 'normalize'
certain spreadsheet table names such that they could be used as
database column names (which have stricter requirements on legal characters that
can be used in table column names)

'''

def ss_column_name_normalize(column_name=None):
    column = (
        column.strip().replace('/','_').replace('-','_')
        .replace(' ','_').replace('\t', '_')
        .replace('(','_').replace(')','')
        .replace(u'\u00B5','u') #micro sign
        .replace(u'\u03BC','u') #greek mu
        .replace(u'\u0040','') # commercial at
        .replace(u'\uFF20','') # fullwidth commercial at
        .replace(u'\uFE6B','') # small commercial at
        .replace(u'\u00B0','') # degrees symbol
        )
    return column
