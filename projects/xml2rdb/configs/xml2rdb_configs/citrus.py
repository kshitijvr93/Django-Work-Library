#
from collections import OrderedDict
def sql_mining_params():
    '''
    od_rel_datacolumns notations:
    (0) key 'attribute_text' reserves a special 'attribute name' to mean text content of a node
         - may also introduce reserved keyword attribute_innerhtml to mean the whole xml content,
            eg from an lxml etree.tostring() call for the node
         - might later introduce keys for node text prefixes and tails per node, if need arises
    (1) first table, named mods, is the main table, xpath set by caller
    (2) other table names below show first comment is the expected xpath to be used in the mining map.
    (3)

    ====================== to add later... to mining map...

        ('genre', OrderedDict([ # [mods]./mods:genre
            ('authority',''), #@authority
            ('text_content',''), # @text_content
        #
        ('language', None), # [mods]./mods:language - pure wrapper object
        ('language_term', OrderedDict([ # [language]./mods:languageTerm
            ('type',''), # @type ('text' or 'code')
            ('authority',''), # @authority
            ('node_text',''), # @node_text, eg, English for type text, eng for type code
        #
        ('location', None), # [mods]./mods:location - pure wrapper object
        #
        ('physical_location', OrderedDict([ #[location]./mods:physicalLocation
            ('type',''), # @type, eg 'code' or ''
            ('node_text',''), #@node_text, eg UFSPEC or UF Special Collections
            ('url_access',''), #./mods:url@access
            ('url_text',''), #/.mods_url@node_text
        ])),
        ('role', None), # This relation is only the index set for the html tag so no columns

        ('role_term', OrderedDict([ #./mods:roleTerm
            ('type',''), # @type
            ('authority',''), # @authority
            ('text_content',''), #@text_content
        ])),
        #
        ('note', OrderedDict([ #./mods:note
            ('text_content',''), # @text_content
            ('name_part',''), # ./mods:namePart
        ])),
        #
        ('related_item', OrderedDict([ #./mods:relatedItem
            ('type',''), # ./@type
            ('physical_description_extent',''), # ./mods:physicalDescription/mods:extent
            ('part_detail_type') #./mods.part/mods:detail@type
            ('part_caption'), #./mods:part/mods:caption@text_content
            ('part_number'), #/mods:part/mods:number@text_content
        ])),
         -------------------------------------------------------------------------------------------------------------
    '''

    od_rel_datacolumns = OrderedDict([
        # The main parent table
        ('mets', OrderedDict([ # ./METS:mets
            ('bib_vid',''),     # .//mods:mods/mods:recordInfo/mods:recordIdentifier@source
            ('date_issued',''), #.//mods:mods/mods:originInfo/mods:dateIssued
            ('temporal_start',''),
            ('temporal_end',''),
            ('temporal_period',''),
            ('country',''),
            ('state',''),
            ('county',''),
            ('city',''),
            ('coordinates_lat_lng', ''),
            ('abstract',''),    # .//mods:mods/mods:abstract
            #('access_condition',''), #.//mods:mods/mods:accessCondition@node_text
            ('url',''), #.//mods:mods/mods:url@text_content
            ('url_access',''), #.//mods:mod/smods:url@access
            ('original_date_issued',''),
           #('hgeo',''), #.//mods:mods/mods:subject/mods:hierarchicalGeographic@node_innerhtml
        ])),

        #
        ('subject', OrderedDict([ #.//mods:mods/mods:subject
            ('id',''), # ./@ID
            ('authority',''), # @authority
            ('topic',''), # .//mods:mods/mods:topic@text_content
        ])),

        ('hgeo', OrderedDict([ # [subject].//mods:mods/mods:hierarchicalGeographic
            #Note: may change to use separate table hierarchicalGeographic so reverse will
            # keep state, county, city within a single hierarchicalGeographic tag
            ('state',''), # .//mods:mods/mods_hierarchicalGeographic/mods:state
            ('county',''), # .//mods:mods/mods:state
            ('city',''), # .//mods:mods/mods:city
            ('type',''), # .//mods:mods/mods:name@type
            ('name_part',''), # .//mods:mods/mods:namePart
        ])),
    ])

#-------------citrus ufdc mets xml files files---------------------------------

    d_node_params1 = {
        #
        # The db_name of this root node is given in a runtime parameter, so
        # db_name is not given for this node, though the name should be the first table name above.
        #
        'multiple':0,
        'child_xpaths' : {
            ".//mods:recordIdentifier" : {
                'attrib_column':{'attribute_text':'bib_vid'},
            },
            ".//mods:dateIssued" : {
                'attrib_column':{'attribute_text':'date_issued'},
            },
            ".//sobekcm:period" : {
                'attrib_column':{
                    'start':'temporal_start',
                    'end':'temporal_end',
                    'attribute_text':'temporal_period'
                },
            },

            ".//mods:mods/mods:subject/mods:hierarchicalGeographic/mods:country": {
                'attrib_column': {'attribute_text':'country'},
            },

            ".//mods:mods/mods:subject/mods:hierarchicalGeographic/mods:state": {
                'attrib_column': {'attribute_text':'state'},
            },

            ".//mods:hierarchicalGeographic/mods:county": {
                'attrib_column': {'attribute_text':'county'},
            },

             ".//mods:hierarchicalGeographic/mods:city": {
                'attrib_column': {'attribute_text':'city'},
            },

             ".//{*}Coordinates": { # gml:Coordinates, but gml not in mets prefix maps
                'attrib_column': {'attribute_text':'coordinates_lat_lng'},
            },

           ".//mods:mods/mods:abstract" : {
                'attrib_column':{'attribute_text':'abstract'},
            },
            #".//mods:mods/mods:accessCondition" : {
            #    'attrib_column':{'attribute_text':'access_condition'},
            #},
            ".//mods:mods/mods:url" : {
                'attrib_column':{'attribute_text':'url'},
            },
            ".//mods:mods/mods:url" : {
                'attrib_column':{'access':'url_access'},
            },

            # NOTE: due to xml2rdb constraint, must use different child_path string here than
            # for 'date_issued' above.
            # Just repeating the value for easy extract of duplicate column for a spreadsheet where
            # Angie is not supposed to change this original date value.
            ".//mods:mods//mods:dateIssued" : {
                'attrib_column':{'attribute_text':'original_date_issued'},
            },

            ########    Subjects ##########

            ".//mods:mods/mods:subject" : {
                'db_name': 'subject', 'multiple': 1,
                'child_xpaths': {
                    './*': {
                        'attrib_column': {'id':'id'},
                    },
                    './*': {
                        'attrib_column': {'authority':'authority'},
                    },
                    './mods:topic': {
                        'attrib_column': {'attribute_text':'topic'},
                    },
                    "./mods:hierarchicalGeographic" : {
                        'db_name': 'hgeo', 'multiple': 1,
                        'child_xpaths': {
                            './mods:state': {
                                'attrib_column': {'attribute_text':'state'},
                            },
                            './mods:county': {
                                'attrib_column': {'attribute_text':'county'},
                            },
                            './mods:city': {
                                'attrib_column': {'attribute_text':'city'},
                            },
                        },
                    },
                },
            },
        }, #end mods table child expaths

    } # end d_node_params1

    d_node_params = d_node_params1

    return od_rel_datacolumns, d_node_params
#end sql_mining_params()
