######################### USER-DEFINED MAPPERS - VALUE DERIVATION METHODS ##########################
'''
NOTE: these methods must all take the single argument of d_row
Any method may use any column value found in d_row, which has values
of all child singleton nodes to the node that uses any derivation function
in the mining map.
'''
import re
def last_first_name(d_row):
    first_name = d_row['given_name'] if 'given_name' in d_row else ''
    last_name = d_row['surname'] if 'surname' in d_row else ''

    return '{}, {}'.format(last_name,first_name)

def uf_affiliation(text_lower=None):
    for match in ['university of florida','univ.fl','univ. fl'
        ,'univ fl' ,'univ of florida'
        ,'u. of florida','u of florida']:
        if text_lower.find(match) != -1:
            #print("Match")
            return '1'
    #end for match
    return '0'

def uf_affiliation_value(d_row):
    if 'name' in d_row:
        text_lower = d_row['name'].lower()
    else:
        text_lower = ''
    return uf_affiliation(text_lower)

def lower_by_colname(d_row,d_params):
    name = d_params.get('colname', None)
    #print("Found colname to use of {}".format(name))
    if name is None:
        raise Exception("Did not find colname paramter")
    if name in d_row:
        text_lower = d_row[name].lower()
        #print("Checking affiliation_name={}".format(text_lower))
    else:
        text_lower=''
    return text_lower

def uf_affiliation_by_colname(d_row,d_params):
    name = d_params.get('colname', None)
    #print("Found colname to use of {}".format(name))
    if name is None:
        raise ValueError("Did not find colname paramter")
    if name in d_row:
        text_lower = d_row[name].lower()
        #print("Checking affiliation_name={}".format(text_lower))
    else:
        text_lower=''
        #print("No given affiliation_name={}".format(text_lower))

    rv = uf_affiliation(text_lower)
    #print("Got uf_affiliation={}".format(rv))
    return rv

def cover_year(d_row):
    if 'cover_date' in d_row:
        # maybe check for length later... but all input data seems good now
        return(d_row['cover_date'][0:4])
    else:
        return ''
    return #need this or pass else highlighting syntax error on next def

def pii_unformatted(d_row):
    if 'fpii' in d_row:
        # maybe check for length later... but all input data seems good now
        return(d_row['fpii'].replace('-','').replace('(','').replace(')','').replace('.',''))
    else:
        return ''

def make_scopus_id(d_row):
    identifier = d_row['identifier'] if 'identifier' in d_row else ''
    scopus_id = ''
    if len(identifier) >= 10:
        scopus_id = identifier[10:]
    return scopus_id

# CRATXML params

def get_date(part_names=None, d_row=None):
    if  part_names is None or d_row is None:
        raise Exception("get_date: Missng part_names. Bad args")
    sep = ''
    result_date = ''
    fills = [4,2,2]
    for i,part_name in enumerate(part_names):
        if part_name in d_row:
            result_date += sep + d_row[part_name].zfill(fills[i])
        else:
            break
        sep = '-'
    return result_date

def date_by_keys_year_month_day(d_row, d_params):
    part_names = []
    for col_key in ['year','month','day']:
        part_names.append(d_params[col_key])
    print("dbkymd: sending part_names='{}'".format(repr(part_names)))
    return get_date(part_names=part_names,d_row=d_row)

def make_issued_date(d_row):
    return get_date(part_names=['issued_year','issued_month','issued_day'],d_row=d_row)

def make_date(d_row, colnames=['year','month','day']):
    return get_date(part_names=colnames, d_row=d_row)

def make_crossref_author_name(d_row):
    family = ''
    given = ''
    if 'family' in d_row:
        family = d_row['family']
    if 'given' in d_row:
        given = d_row['given']
    #print("Got given={} family={}".format(given,family))

    if family and given:
        name = family + ', ' + given
    else:
        name = family + given

    return name

def funder_id_by_funder_doi(d_row):
    funder_id = ''
    funder_doi = d_row.get('funder_doi', '/')
    parts = funder_doi.split('/')
    if len(parts) > 1:
        funder_id = parts[len(parts)-1]
    return funder_id
