###### START SCOPUS INPUT PARAMETERS ########
# 20161205 - Next, revert to using scopus xml files, but first alter satxml to add uf-harvest tag to those

def sql_mining_params():

    od_rel_datacolumns = OrderedDict([
        ('scopus', OrderedDict([
            ('scopus_id',''),
            ('eid',''),
            ('doi',''),
            ('pii',''),
            ('title',''),
            ('creator',''),
            ('publication_name',''),
            ('issn',''),
            ('eissn',''),
            ('cover_year',''),
            ('cover_date',''),
            ('citedby_count',''),
            ('agg_type',''),
            ('subtype',''),
            ('subtype_description',''),
            ('source_id',''),
            ('file_name',''),
            ('uf_harvest',''),
        ])),

        ('scopus_aff', OrderedDict([
            ('name',''),
            ('city',''),
            ('country',''),
        ])),
    ])
#----------------------------------------------
    d_node_params = {
        #
        # The db_name of this root node is given in a runtime parameter, so db_name is
        # not given for this node.
        #
        'multiple':0,
        'child_xpaths' : {
            ".//dc:identifier": {
                'multiple':0,
                'attrib_column': { 'text':'identifier' },
                'column_function': {'scopus_id': make_scopus_id}
            }
            ,".//{*}eid": {
                'multiple':0,
                'attrib_column': { 'text':'eid' },
            }
            ,".//dc:title": {
                'multiple':0,
                'attrib_column': {'text':'title' }
            }
            ,".//dc:creator": {
                'multiple':0,
                'attrib_column': {'text':'creator' }
            }

            ,".//prism:publicationName":{
                'multiple':0,
                'attrib_column':{'text':'publication_name'}
            }
            ,".//prism:issn":{
                'multiple':0,
                'attrib_column':{'text':'issn'}
            }
            ,".//prism:eIssn":{
                'multiple':0,
                'attrib_column':{'text':'eissn'}
            }
            ,".//prism:coverDate":{
                'multiple':0,
                'attrib_column':{'text':'cover_date', 'cover_year':'cover_year'},
                'column_function': {'cover_year': cover_year} #re-use Elsevier's method here
            }
            ,".//prism:doi":{
                'multiple':0,
                'attrib_column':{'text':'doi'},
            }
            ,".//{*}citedby-count":{
                'multiple':0,
                'attrib_column':{'text':'citedby_count'}
            }
            ,".//{*}pii":{
                'multiple':0,
                'attrib_column':{'text':'pii'},
            }

            ,".//prism:aggregationType":{
                'multiple':0,
                'attrib_column':{'text':'agg_type'}
            }
            ,".//{*}subtype":{
                'multiple':0,
                'attrib_column':{'text':'subtype'},
            }
            ,".//{*}subtypeDescription":{
                'multiple':0,
                'attrib_column':{'text':'subtype_description'},
            }
            ,".//{*}source-id":{
                'multiple':0,
                'attrib_column':{'text':'source_id'},
            }
            ,".//{*}affiliation":{
                'db_name':'scopus_aff',
                'multiple':1,
                'child_xpaths' : {
                    ".//{*}affilname":{
                        'multiple':0,
                        'attrib_column':{'text':'name'}
                    },
                    ".//{*}affiliation-city": {
                        'multiple':0,
                        'attrib_column':{'text':'city'}
                    },
                    ".//{*}affiliation-country": {
                        'multiple':0,
                        'attrib_column':{'text':'country'}
                    },
                },
            }
            ,".//{*}uf-harvest":{
                'multiple':0,
                'attrib_column':{'text':'uf_harvest'},
            }
        } # end child_xpaths
    } # end d_node_params

    return od_rel_datacolumns, d_node_params
#end def sql_mining_params
