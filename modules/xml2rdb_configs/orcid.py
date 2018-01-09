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
Method sql_mining_params

See https://github.com/ORCID/ORCID-Source/tree/master/orcid-model/src/main/resources/record_2.0
and its links for xsd information to assist in creating ORCID db schema and
mining maps.

'''
def sql_mining_params():

    od_rel_datacolumns = OrderedDict([
        # The main parent table for orcid public records
        ('person', OrderedDict([ #
            ('orcid_id',''),    # ./common:orcid-identifier/common:path
            ('preferred_language',''), #./preferences/preferences:locale
            ('givens',''),       # ./person:person/perons:name/personal-details:given_names
            ('family',''),      # ./person:person/perons:name/personal-details:family-name
            ('family_givens',''),# method family_given(['given','family']
            ('person_modified_date',''), # ./person:person/common:last-modified-date
        ])),
        # orcid_xid: has any external ids (xid) for record holders, such as ResearcherID,
        # any others
        ('xid', OrderedDict([ # (./person:person)
            # ./external-identifier:external-identifiers/external-identifier:external-identifier
            ('type',''), # ./common:external-id-type
            ('value',''), # ./common:external-id-value
            ('url',''), # ./common:external-id-url
            ('relationship',''), #./common:external-id-relationship
            ('xid_modified_date',''), #./common:last_modified_date
        ])),
        # orcid_education: education events
        ('education', OrderedDict([ #./activities:activities-summary/activities:educations
                        # ... /activities:education-summary
            ('ed_modified_date',''), # ./common:last-modified-date
            ('department_name',''), # ./education:department-name
            ('role_title',''),      # ./education:role-title
            ('start_date',''), # method() ./common:start-date (year, month,day)
            ('end_date',''),        # method() ./common:start-date/year, month, day
            ('organization_name',''), # ./education:organization/common:name
            ('organization_city',''), # ./education:organization/common:address/common:city
            ('organization_region',''), # ./education:organization/common:address/common:region
            ('organization_country',''), # ./education:organization/common:address/common:country
            ('disambiguated_id',''),# ./education:organization/common:disambiguated-organization
                                 # /common:disambiguated-organization-identifier
            ('disambiguation_source',''),# ./education:organization/common:disambiguated-organization
                                 # /common:disambiguation-source
        ])),
        # orcid_employment: employment events
        ('employment', OrderedDict([ #./activities:activities-summary
                        # /activities:employments/employment:employment-summary
            ('created_date',''), # ./common:created-date
            ('emp_modified_date',''), # ./common:last-modified-date
            ('department_name',''),
            ('role_title',''),      # ./education:role-title
            ('start_date',''), # method() ./common:start-date (year, month,day)
            ('end_date',''),        # method() ./common:start-date/year, month, day
            ('organization_name',''), # ./employment:organization/common:namedef node_

            ('organization_city',''), # ./employment:organization/common:address/common:city
            ('organization_region',''), # ./employment:organization/common:address/common:region
            ('organization_country',''), # ./employment:organization/common:address/common:country
            ('disambiguated_id',''),# ./employment:organization/common:disambiguated-organization
                                 # /common:disambiguated-organization-identifier
            ('disambiguation_source',''),# ./education:organization/common:disambiguated-organization
                                 # /common:disambiguation-source
        ])),
        # orcid_work: works
        ('work', OrderedDict([ #./activities:activities-summary
                        # /activities:works/activities:group
            ('created_date',''), # ./work:work-summary/common:created-modified-date
            ('modified_date',''), # ./work:work-summary/common:last-modified-date
            ('title',''),      # ./work:work-summary/work:title/common:title
            ('type',''),      # ./work:work-summary/work:type
            ('publication_date',''),  # (method on 3 ymd values)
                        #./work:work-summary/common:publication-date
        ])),
        # orcid_work_xid: has any external ids (xid) for works, such as DOI, PCM,
        # any others
        ('work_xid', OrderedDict([ # (...activities:group)
            # ./common:external-ids/common:external-id
            ('type',''), # ./common:external-id-type
            ('value',''), # ./common:external-id-value
            ('url',''), # ./common:external-id-url
            ('relationship',''), #./common:external-id-relationship
         ])),
    ])

#-------------orcid api---------------------------------

    d_node_params1 = {
        #
        # The db_name of this root node is given in a runtime parameter, so
        # db_name is not given for this node.
        #
        'multiple':0,
        'child_xpaths' : {
            "./common:orcid-identifier/common:path" : {
                'attrib_column':{'text':'orcid_id'},
            },
            "./preferences:preferences/preferences:locale" : {
                'attrib_column':{'text':'preferred_language'},
            },
            "./person:person/person:name/personal-details:given-names" : {
                'attrib_column':{'text':'givens'},
            },
            "./person:person/person:name/personal-details:family-name" : {
                'attrib_column':{'text':'family'},
            },
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
