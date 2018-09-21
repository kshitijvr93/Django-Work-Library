import sys, os, os.path, platform
import datetime
from collections import OrderedDict

def register_modules():
    platform_name = platform.system().lower()
    if platform_name == 'linux':
        modules_root = '/home/robert/'
        #raise ValueError("MISSING: Enter code here to define modules_root")
    else:
        # assume rvp office pc running windows
        modules_root="C:\\rvp\\"
    sys.path.append('{}git/citrus/modules'.format(modules_root))
    return
register_modules()
from collections import OrderedDict
from mappers import make_date

'''
#Sample XIS-exported input file with subject keywords has sequence of items like this:
-------
<Thesis n="0000002">
<ADD><D>20170214</D>
<IN>DJV</IN>
</ADD>
<CHG><D>20180629</D>
<IN>win</IN>
</CHG>
<TOPIC>Globalization^Sovereignty^Financial markets^Financial transactions^Currency^Information technology^Financial services^International organizations^Flexible spending accounts^Conceptualization</TOPIC>
<OLDLCSH />
<OLDKW>globalization, sovereignty, uk^Political Science^Florida State University^Cocoa High School (Cocoa, Fla.)^Globalization^Sovereignty^Financial markets^Currency^Financial transactions^Financial services^Information technology^Finance^Flexible spending accounts^Conceptualization</OLDKW>
<GEO>Union County (Florida)</GEO>
<FLORIDIANS>Florida State University^Cocoa High School (Cocoa, Fla.)</FLORIDIANS>
<AU><FNAME>Jamie E</FNAME>
<LNAME>Scalera</LNAME>
</AU>
<TI>Challenging the Sovereign</TI>
<DPUB>2007</DPUB>
<ID>UFE0021053_00001</ID>
</Thesis>
-------

and a simple input pre-process program xis_xml.py will read that input file
and only convert the elements with ^-separated terms to
child <I> (item) elements, eg:

<FLORIDIANS>
  <I>Florida State University</I>
  <I>Cocoa High School (Cocoa, Fla.)</I>
</FLORIDIANS>

and the output of that will be the actual input file to xml2rdb

-------

'''

'''
Method sql_mining_params

'''

def sql_mining_params():

    od_rel_datacolumns = OrderedDict([
        # Main parent for xis_subject data
        ('bibvid', OrderedDict([ #
            ('bibvid',''),    # ./UFDC id
            ('title',''),    # ./UFDC id
            ('author_fname',''),
            ('author_lname',''),
            ('pub_d',''),    # ./UFDC id
            ('add_ymd',''),    # ./common:orcid-identifier/common:path
            ('add_initials',''),    # ./common:orcid-identifier/common:path
            ('change_ymd',''),
            ('change_initials',''),    # ./common:orcid-identifier/common:path
        ])),
        ('topic', OrderedDict([ #
            ('term',''),
            ('keep','y'),
            ('marc','653'),
            ('ind1',' '),
            ('ind2','7'),
        ])),
        ('oldlcsh', OrderedDict([ #
            ('term',''),
            ('keep','n'),
            ('marc','650'),
            ('ind1',' '),
            ('ind2','4'),
        ])),
        # Note: use rel oldnewkw to allow additions, but initially
        # populate it with <oldkw> items that default to keep=n.
        ('oldnewkw', OrderedDict([ #
            ('term',''),
            ('keep','n'),
            ('marc','650'),
            ('ind1',' '),
            ('ind2','4'),
        ])),
        ('geo', OrderedDict([ #
            ('term',''),    # ./UFDC id
            ('keep','y'),
            ('marc','651'),
            ('ind1',' '),
            ('ind2','7'),
        ])),
        ('floridians', OrderedDict([ #
            ('term',''),    # ./UFDC id
            ('keep','y),
            ('marc','600'),
            ('ind1',' '),
            ('ind2','7'),
        ])),

# end -------------od_rel_columns for xis subject terms relations

    d_node_params1 = {
        #
        # The db_name of this root node is given in a runtime parameter, so
        # db_name is not given for this node.
        #
        'multiple':0,
        'child_xpaths' : {
            "./ID" : {
                'attrib_column':{'text':'bibvid'},
            },
            "./ADD/D" : {
                'attrib_column':{'text':'add_ymd'},
            },
            "./ADD/IN" : {
                'attrib_column':{'text':'add_initials'},
            },
            "./CHG/D" : {
                'attrib_column':{'text':'change_ymd'},
            },
            "./CHG/IN" : {
                'attrib_column':{'text':'change_initials'},
            },
            "./AU/FNAME" : {
                'attrib_column':{'text':'au_fname'},
            },
            "./AU/LNAME" : {
                'attrib_column':{'text':'au_Lname'},
            },
            "./TI" : {
                'attrib_column':{'text':'title'},
            },
            "./DPUB" : {
                'attrib_column':{'text':'pub_year'},
            },
            #"./person:person/person:name/personal-details:family-name"{
            #"./person:person/person:name/personal-details:family-name"{
            #    'attrib_column':{'text':'family-given'},
            #},
            "./person:person/common:last-modified-date" : {
                'attrib_column':{'text':'person_modified_date'},
            },
            "./person:person/common:created-modified-date" : {
                'attrib_column':{'text':'person_created_date'},
            },

            ########    EXTERNAL IDENTIFIERS ##########

            "./person:person/external-identifier:external-identifiers/external-identifier:external-identifier" : {
                'db_name': 'xid', 'multiple': 1,
                'child_xpaths': {
                    './common:external-id-type': {
                        'attrib_column': {'text':'type'},
                    },
                    './common:external-id-value': {
                        'attrib_column': {'text':'value'},
                    },
                    './common:external-id-url': {
                        'attrib_column': {'text':'url'},
                    },
                    './common:external-id-relationship': {
                        'attrib_column': {'text':'relationship'},
                    },
                    './common:last-modified-date': {
                        'attrib_column': {'text':'modified_date'},
                    },
                },
            },

            ########    EMPLOYMENT ##########

            "./activities:activities-summary/activities:employments/employment:employment-summary" : {
                'db_name': 'employment',  'multiple': 1,
                'child_xpaths': {
                    './common:last-modified-date': {
                        'attrib_column': {'text':'modified_date'},
                    },
                    './employment:role-title': {
                        'attrib_column': {'text':'role_title'},
                    },
                    './employment:department-name': {
                        'attrib_column': {'text':'department_name'},
                    },

                    './common:start-date': {
                        'multiple':0,
                        'child_xpaths': {
                            './common:year': {
                                'attrib_column': {'text':'year'},
                            },
                            './common:month': {
                                'attrib_column': {'text':'month'},
                            },
                            './common:day': {
                                'attrib_column': {'text':'day'},
                            },
                        },
                        'column_function': {'start_date': make_date},
                    },

                    './common:end-date': {
                        'multiple':0,
                        'child_xpaths': {
                            './common:year': {
                                'attrib_column': {'text':'year'},
                            },
                            './common:month': {
                                'attrib_column': {'text':'month'},
                            },
                            './common:day': {
                                'attrib_column': {'text':'day'},
                            },
                        },
                        'column_function': {'end_date': make_date},
                    },

                    './employment:organization/common:name': {
                        'attrib_column': {'text':'organization_name'},
                    },
                    './employment:organization/common:address/common:city': {
                        'attrib_column': {'text':'organization_city'},
                    },
                    './employment:organization/common:address/common:region': {
                        'attrib_column': {'text':'organization_region'},
                    },
                    './employment:organization/common:address/common:country': {
                        'attrib_column': {'text':'organization_country'},
                    },
                    ('./employment:organization/common:disambiguated-organization'
                        +'/common:disambiguated-organization-identifier') : {
                        'attrib_column': {'text':'disambiguated_id'},
                    },
                    ('./employment:organization/common:disambiguated-organization'
                        +'/common:disambiguation-source') : {
                        'attrib_column': {'text':'disambiguation_source'},
                    },
                },
            },

            #############       EDUCATION     #################

            "./activities:activities-summary/activities:educations/education:education-summary" : {
                'db_name': 'education',  'multiple': 1,
                'child_xpaths': {
                    './common:last-modified-date': {
                        'attrib_column': {'text':'modified_date'},
                    },
                    './education:department-name': {
                        'attrib_column': {'text':'department_name'},
                    },
                    './education:role-title': {
                        'attrib_column': {'text':'role_title'},
                    },

                    './common:start-date': {
                        'multiple':0,
                        'child_xpaths': {
                            './common:year': {
                                'attrib_column': {'text':'year'},
                            },
                            './common:month': {
                                'attrib_column': {'text':'month'},
                            },
                            './common:day': {
                                'attrib_column': {'text':'day'},
                            },
                        },
                        'column_function': {'start_date': make_date},
                    },

                    './common:end-date': {
                        'multiple':0,
                        'child_xpaths': {
                            './common:year': {
                                'attrib_column': {'text':'year'},
                            },
                            './common:month': {
                                'attrib_column': {'text':'month'},
                            },
                            './common:day': {
                                'attrib_column': {'text':'day'},
                            },
                        },
                        'column_function': {'end_date': make_date},
                    },


                    './education:organization/common:name': {
                        'attrib_column': {'text':'organization_name'},
                    },
                    './education:organization/common:address/common:city': {
                        'attrib_column': {'text':'organization_city'},
                    },
                    './education:organization/common:address/common:region': {
                        'attrib_column': {'text':'organization_region'},
                    },
                    './education:organization/common:address/common:country': {
                        'attrib_column': {'text':'organization_country'},
                    },
                    ('./education:organization/common:disambiguated-organization'
                        +'/common:disambiguated-organization-identifier') : {
                        'attrib_column': {'text':'disambiguated_id'},
                    },
                    ('./education:organization/common:disambiguated-organization'
                        +'/common:disambiguation-source') : {
                        'attrib_column': {'text':'disambiguation_source'},
                    },
                },
            },

            ############  WORK #############

            "./activities:activities-summary/activities:works/activities:group/work:work-summary" : {
                'db_name': 'work',  'multiple': 1,
                'child_xpaths': {
                    './common:last-modified-date': {
                        'attrib_column': {'text':'modified_date'},
                    },
                    './work:title/common:title': {
                        'attrib_column': {'text':'title'},
                    },
                    './common:external-ids/common:external-id': {
                        'db_name': 'work_xid', 'multiple':1,
                        'child_xpaths': {
                            './common:external-id-type' : {
                                'attrib_column': {'text':'type'},
                            },
                            './common:external-id-value': {
                                'attrib_column': {'text':'value'},
                            },
                            './common:external-id-url' :{
                                'attrib_column': {'text':'url'},
                            },
                            './common:external-id-relationship' : {
                                'attrib_column': {'text':'relationship'},
                            },
                        },
                    },

                    './work:type': {
                        'attrib_column': {'text':'type'},
                    },
                    './work:title/common:title': {
                        'attrib_column': {'text':'title'},
                    },
                    './work:title/common:title': {
                        'attrib_column': {'text':'title'},
                    },
                    './work:title/common:title': {
                        'attrib_column': {'text':'title'},
                    },
                    './common:publication-date': {
                        'multiple':0,
                        'child_xpaths': {
                            './common:year': {
                                'attrib_column': {'text':'year'},
                            },
                            './common:month': {
                                'attrib_column': {'text':'month'},
                            },
                        },
                        'column_constant': {'day':''},
                        'column_function': {'publication_date': make_date},
                    },
                },
            },
        },

    } # end d_node_params1

    # Interpose a new 'message' tag to support multiple crossref xml response formats:
    # see programs crafatxml and crawdxml for example, that produce these formats
    d_node_params2 = {
        'child_xpaths':{'.//message' : d_node_params1}
    }

    d_node_params = d_node_params1
    return od_rel_datacolumns, d_node_params
#end def sql_mining_params
