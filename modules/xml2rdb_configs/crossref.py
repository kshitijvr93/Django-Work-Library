def sql_mining_params():

    od_rel_datacolumns = OrderedDict([
        ('cross_doi', OrderedDict([
            ('doi',''),
            ('issn',''),
            ('url',''),
            ('archive',''),
            ('container_title',''),
            ('restriction',''),
            ('created_date_time',''),
            ('deposited_date_time',''),
            ('indexed_date_time',''),
            ('issue',''),
            ('issued_date',''),
            ('member',''),
            ('original_title',''),
            ('page_range',''),
            ('prefix',''),
            ('online_date',''),
            ('print_date',''),
            ('publisher',''),
            ('reference_count',''),
            ('score',''),
            ('short_container_title',''),
            ('short_title',''),
            ('source',''),
            ('subtitle',''),
            ('title',''),
            ('type',''),
            ('volume',''),
        ])),
        ('cross_author', OrderedDict([
            ('name',''),
            ('family',''),
            ('given',''),
            ('affiliation_name',''),
            ('affiliation_uf',''),
            ('orcid',''),
        ])),
        ('cross_link', OrderedDict([
            ('url',''),
            ('content_type',''),
            ('content_version',''),
            ('intended_application',''),
        ])),
        ('cross_license', OrderedDict([
            ('url',''),
            ('content_version',''),
            ('delay_in_days',''),
            ('start_date',''),
        ])),
        ('cross_subject', OrderedDict([
            ('term',''),
        ])),
        ('cross_funder', OrderedDict([
            ('funder_doi',''),
            ('funder_id',''),
            ('doi_asserted_by',''),
            ('name',''),
        ])),
        ('cross_award', OrderedDict([
            ('code_id',''),
        ])),
    ])

#-------------crossref api---------------------------------

    d_node_params1 = {
        #
        # The db_name of this root node is given in a runtime parameter, so db_name is
        # not given for this node.
        #
        'multiple':0,
        'child_xpaths' : {
            "./license" : { # One crossref doi record may have multiple licenses
                'db_name': 'cross_license', 'multiple': 1,
                'child_xpaths': {
                    ".//{*}URL" : {
                        'attrib_column': {'text':'url'},
                    },
                    ".//{*}content-version" : {
                        'attrib_column': {'text':'content_version'},
                    },
                    ".//{*}delay-in-days" : {
                        'attrib_column': {'text':'delay_in_days'},
                    },

                    ".//{*}start/{*}date-parts/item[@id='00000001']" : {
                        'child_xpaths' : {
                            "./item[@id='00000001']":{
                                'attrib_column' : { 'text':'year'},
                            },
                            "./item[@id='00000002']":{
                                'attrib_column' : { 'text':'month'},
                            },
                            "./item[@id='00000003']":{
                                'attrib_column' : { 'text':'day'},
                            },
                        },
                        'column_function': {'start_date': make_date},
                    },
                },
            },

            "./subject" : {
                'db_name': 'cross_subject', 'multiple': 1,
                'child_xpaths': {
                    "./*" : {
                        'attrib_column': {'text':'term'},
                    },
                },
            },

            "./author/item" : {
                'db_name': 'cross_author', 'multiple': 1,
                'child_xpaths': {
                    ".//affiliation//name" : {
                        'attrib_column': {'text':'affiliation_name'},
                    },
                    ".//family" : {
                        'attrib_column': {'text':'family'},
                    },
                    ".//given" : {
                        'attrib_column': {'text':'given'},
                    },
                    ".//orcid" : {
                        'attrib_column': {'text':'orcid'},
                    },
                },
                'column_function': {
                    'name': make_crossref_author_name,
                    'affiliation_uf': (uf_affiliation_by_colname,{'colname':'affiliation_name'}),
                    },
            },
            "./link" : {
                'db_name': 'cross_link', 'multiple': 1,
                'child_xpaths': {
                    ".//URL" : {
                        'attrib_column': {'text':'url'},
                    },
                    ".//content_type" : {
                        'attrib_column': {'text':'content_type'},
                    },
                    ".//content-version" : {
                        'attrib_column': {'text':'content_version'},
                    },
                    ".//intended-application" : {
                        'attrib_column': {'text':'intended_application'},
                    },
                },
            },
            "./funder/item" : {
                'db_name': 'cross_funder', 'multiple': 1,
                'child_xpaths': {
                    "./DOI" : {
                        'attrib_column': {'text':'funder_doi'},
                        'column_function': {'funder_id': funder_id_by_funder_doi},
                    },
                    "./doi-asserted-by" : {
                        'attrib_column': {'text':'doi_asserted_by'},
                    },
                    "./name" : {
                        'attrib_column': {'text':'name'},
                    },
                    "./award" : {
                        'db_name': 'cross_award', 'multiple': 1,
                        'child_xpaths': {
                            "./*" : {
                                'attrib_column': {'text': 'code_id'},
                            },
                        },
                    },
                },
            },

            "./DOI": {
                'multiple':0,
                'attrib_column': { 'text':'doi' },
            },
            "./ISSN": {
                'multiple':0,
                'attrib_column': { 'text':'issn' },
            },
            "./URL": {
                'multiple':0,
                'attrib_column': { 'text':'url' },
            },
            "./archive/item[@id='00000001']": {
                'multiple':0,
                'attrib_column': { 'text':'archive' },
            },
            "./container-title": {
                'multiple':0,
                'attrib_column': { 'text':'container_title' },
            },
            "./content-domain/crossmark-restriction": {
                'multiple':0,
                'attrib_column': { 'text':'restriction' },
            },
            # Note: some xml date-like tags do NOT have tag for date-time, but for these next
            # three that do, just use them and disregard parts for year, month, day.
            "./created/date-time": {
                'multiple':0,
                'attrib_column': { 'text':'created_date_time' },
            },

            "./deposited/date-time": {
                'multiple':0,
                'attrib_column': { 'text':'deposited_date_time' },
            },
            "./indexed/date-time": {
                'multiple':0,
                'attrib_column': { 'text':'indexed_date_time' },
            },
            "./issue": {
                'multiple':0,
                'attrib_column': { 'text':'issue' },
            },
            "./issued/date-parts/item[@id='00000001']": {
                'multiple':0,
                'child_xpaths' : {
                    './{*}item[@id="00000001"]':{ 'multiple':0,
                        'attrib_column':{'text':'issued_year'}},
                    './{*}item[@id="00000002"]':{ 'multiple':0,
                        'attrib_column':{'text':'issued_month'}},
                    './{*}item[@id="00000003"]':{ 'multiple':0,
                        'attrib_column':{'text':'issued_day'}},
                    },
                'column_function': {'issued_date': make_issued_date}
            },
            "./member": {
                'multiple':0,
                'attrib_column': { 'text':'member' },
            }
            ,"./original-title": {
                'multiple':0,
                'attrib_column': { 'text':'original_title' },
            }
            ,"./page": {
                'multiple':0,
                'attrib_column': { 'text':'page_range' },
            }
            ,"./prefix": {
                'multiple':0,
                'attrib_column': { 'text':'prefix' },
            }
            ,"./eid": {
                'multiple':0,
                'attrib_column': { 'text':'eid' },
            }
            ,"./published-online/date-parts/item[@id='00000001']": {
                'multiple':0,
                'child_xpaths' : {
                    './{*}item[@id="00000001"]':{ 'multiple':0,
                        'attrib_column':{'text':'year'}},
                    './{*}item[@id="00000002"]':{ 'multiple':0,
                        'attrib_column':{'text':'month'}},
                    './{*}item[@id="00000003"]':{ 'multiple':0,
                        'attrib_column':{'text':'day'}},
                },
                'column_function': {'online_date': make_date }
            }
            ,"./published-print/date-parts/item[@id='00000001']" : {
                'multiple':0,
                'child_xpaths' : {
                    './{*}item[@id="00000001"]':{ 'multiple':0,
                        'attrib_column':{'text':'year'}},
                    './{*}item[@id="00000002"]':{ 'multiple':0,
                        'attrib_column':{'text':'month'}},
                    './{*}item[@id="00000003"]':{ 'multiple':0,
                        'attrib_column':{'text':'day'}},
                },
                'column_function': {'print_date': make_date}
            }
            ,"./publisher": {
                'multiple':0,
                'attrib_column': { 'text':'publisher' },
            }
            ,"./reference-count": {
                'multiple':0,
                'attrib_column': { 'text':'reference_count' },
            }
            ,"./score": {
                'multiple':0,
                'attrib_column': { 'text':'score' },
            }
            ,"./short-container-title": {
                'multiple':0,
                'attrib_column': { 'text':'short_container_title' },
            }
            ,"./short-title": {
                'multiple':0,
                'attrib_column': { 'text':'short_title' },
            }
            ,"./eid": {
                'multiple':0,
                'attrib_column': { 'text':'eid' },
            }
            ,"./source": {
                'multiple':0,
                'attrib_column': { 'text':'source' },
            }
            ,"./subtitle/item[@id='00000001']": {
                'multiple':0,
                'attrib_column': { 'text':'subtitle' },
            }
            ,"./title": {
                'multiple':0,
                'attrib_column': { 'text':'title' },
            }
            ,"./type": {
                'multiple':0,
                'attrib_column': { 'text':'type' },
            }
            ,"./volume": {
                'multiple':0,
                'attrib_column': { 'text':'volume' },
            }
        } # end child_xpaths

    } # end d_node_params2

    # Interpose a new 'message' tag to support multiple crossref xml response formats:
    # see programs crafatxml and crawdxml for example, that produce these formats
    d_node_params2 = {
        'child_xpaths':{'.//message' : d_node_params1}
    }

    d_node_params = d_node_params1
    return od_rel_datacolumns, d_node_params
#end def sql_mining_params_crossref
