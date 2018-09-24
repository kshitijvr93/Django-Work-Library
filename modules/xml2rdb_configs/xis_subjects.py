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
#Sample XIS-exported input file with subject keywords, parsed and converted by
helper program: xis_subjects_parse.py has sequence of items like this:
-------
<Thesis n="0000002">
<ADD><D>20170214</D>
<IN>DJV</IN>
</ADD>
<CHG><D>20180629</D>
<IN>win</IN>
</CHG>
<TOPIC><I>Globalization</I><I>Sovereignty</I></TOPIC>
<OLDLCSH><I></I></OLDLCSH>
<OLDKW><I>globalization, sovereignty, uk</I><I>Political Science</I><I>Florida State University</I><I>Cocoa High School (Cocoa, Fla.)</I><I>Globalization</I><I>Sovereignty</I><I>Financial markets</I><I>Currency</I><I>Financial transactions</I><I>Financial services</I><I>Information technology</I><I>Finance</I><I>Flexible spending accounts</I><I>Conceptualization</I></OLDKW>
<GEO><I>Union County (Florida)</I></GEO>
<FLORIDIANS><I>Florida State University</I><I>Cocoa High School (Cocoa, Fla.)</I></FLORIDIANS>
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

and the output of that will be the actual input file to xml2rdb, to be
read as input and procesed with the following config.
The returned tuple of sql_mining_params is the config below.
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
            ('thesis_n',''),
            ('title',''),    # ./UFDC id
            ('author_fname',''),
            ('author_lname',''),
            ('pub_d',''),    # ./UFDC id
            ('add_ymd',''),    # ./common:orcid-identifier/common:path
            ('add_initials',''),    # ./common:orcid-identifier/common:path
            ('change_ymd',''),
            ('change_initials',''),    # ./common:orcid-identifier/common:path
        ])),
        ('term', OrderedDict([ #
            ('source_tag',''),
            ('term',''),
            ('keep','y'),
            ('marc','653'),
            ('ind1',' '),
            ('ind2','7'),
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
            ('keep','y'),
            ('marc','600'),
            ('ind1',' '),
            ('ind2','7'),
        ])),
    ])

# end -------------od_rel_columns for xis subject terms relations

    d_node_params1 = {
        # The db_name of this root node is given in a runtime parameter, so
        # db_name is not given for this node.
        'multiple':0,
        'attrib_column':{'n':'thesis_n_zfill7'},
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
            # TOPIC KEYWORDS
            "./TOPIC/I" : {
                'multiple':1,
                'db_name':'term',
                'attrib_column':{'text':'term'},
                'column_constant':{
                    'source_tag': 'TOPIC',
                    'marc': '653',
                    'indcator1': ' ',
                    'indicator2': '7',
                    'keep': 'y',
                },
            },

            # GEO KEYWORDS
            "./GEO/I" : {
                'multiple':1,
                'db_name':'term',
                'attrib_column':{'text':'term'},
                'column_constant':{
                    'source_tag': 'GEO',
                    'marc': '651',
                    'indcator1': ' ',
                    'indicator2': '7',
                    'keep': 'y',
                },
            },

            # GEO KEYWORDS
            "./OLDKW/I" : {
                'multiple':1,
                'db_name':'term',
                'attrib_column':{'text':'term'},
                'column_constant':{
                    'source_tag': 'OLDKW',
                    'marc': '650',
                    'indcator1': ' ',
                    'indicator2': '4',
                    'keep': 'n',
                },
            },

            # FLORIDIANS KEYWORDS
            "./FLORIDIANS/I" : {
                'multiple':1,
                'db_name':'term',
                'attrib_column':{'text':'term'},
                'column_constant':{
                    'source_tag': 'FLORIDIANS',
                    'marc': '600',
                    'indcator1': ' ',
                    'indicator2': '7',
                    'keep': 'y',
                },
            },

            # OLDLCSH KEYWORDS
            "./OLDLCSH/I" : {
                'multiple':1,
                'db_name':'term',
                'attrib_column':{'text':'term'},
                'column_constant':{
                    'source_tag': 'OLDLCSH',
                    'marc': '600',
                    'indcator1': ' ',
                    'indicator2': '7',
                    'keep': 'y',
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
