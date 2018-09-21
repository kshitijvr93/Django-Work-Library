'''
20171025 - discarding this approach. rather using relation names as the embedded paths
in another prototpye, marcxml_mets2.py... as of 20171025

marcxml_mets.py
rdb2xml configuration to transform marcxml to sobekcm-loadable mets file
'''
# database connection

#
# NOTE: when this map is used, it may already have od_row of data from the main
# db table populated.
# NOTE: this process itself may also have some data associated with it that
# may appear # in the od_row and also the resulting xml file:
# (after development of initial prototype)
# 'utc_secs': eg "2017-10-25T10:06:50Z"
# 'record_status': 'PARTIAL' # needs research on other possible values
# 'creator' : login id
# 'bibid'
#
# Note about list_tag_dict: this is similar to xml2rdb xpaths object, but here
# it is a list of 2-tuples
# of a tag name and a dict of params for building that tag
# This is required to suppor multiple appearances of one tag within another.
# Compare the conversion done by xml2rdb, where there a findall() lxml method is used
# to always find 1 or more (a list) tags internally, and so no list datatype appears in its
# mining map.
#
def prolog(od_row )
    material_type = od_row.get('material_type','MIXED MATERIAL')
    title = od_row.get('title','(no title)')

    return( ('"<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<!--  {} ({})-->"'.format(title,material_type))

d_node_params = {
    'list_tag_dict' : [(
        "<METS:mets>" , {
            'constant_settings' : '''xmlns:METS="http://www.loc.gov/METS/"
      xmlns:xlink="http://www.w3.org/1999/xlink"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xmlns:mods="http://www.loc.gov/mods/v3"
      xmlns:sobekcm="http://sobekrepository.org/schemas/sobekcm/"
      xmlns:lom="http://sobekrepository.org/schemas/sobekcm_lom"
      xsi:schemaLocation="http://www.loc.gov/METS/
        http://www.loc.gov/standards/mets/mets.xsd
        http://www.loc.gov/mods/v3
        http://www.loc.gov/mods/v3/mods-3-4.xsd
        http://sobekrepository.org/schemas/sobekcm/
        http://sobekrepository.org/schemas/sobekcm.xsd"
        '''
            , 'list_tag_dict' : [
                ('<METS:metsHdr>' , {
                    'constant_settings' : 'RECORDSTATUS="PARTIAL"'
                    ,'attrib_column' {
                        'CREATEDATE': 'create_date'
                        ,'ID': 'bib_vid'
                        ,'LASTMODDATE' : 'create_date'
                    }
                    'list_tag_dict' : [
                        ('<METS:agent>' , {
                            'constant_settings' : 'ROLE="CREATOR" TYPE="ORGANIZATION"'
                            ,'list_tag_dict' : [
                                ('<METS:name>' , {
                                    'inner_content' : 'UF, University of Florida'
                                })
                            ]
                        })
                        ,('<METS:agent>', {
                            'constant_settings' : 'OTHERTYPE="SOFTWARE" ROLE="CREATOR" TYPE="OTHER"'
                            ,'list_tag_dict' : [('<METS:name>' , {
                                'inner_content' : 'UF, University of Florida'
                                })
                            ]
                        })
                        ,('<METS:agent>', {
                            'constant_settings' : 'ROLE="CREATOR" TYPE="INDIVIDUAL"'
                            ,'attrib_column' : {'inner_content': 'user'}
                            ,'list_tag_dict' : [('<METS:name>' , {
                                'inner_content' : 'UF, University of Florida'
                                })
                            ]
                        })
                    ]
                })
                ,('METS:dmdSec': {
                    'constant_settings': 'ID="DMD1"'
                    ,'list_tag_dict' : [
                        ('METS:mdWrap' : {
                            'constant_settings': 'MDTYPE="MODS" MIMETPE="text/ml" LABEL="MODS Metadata"'
                        })
                    ]
                })
            ]
        })
    ]
}
