# els_bibvid_del
# HISTORY:
# This was run successfully to produce the indicated output. The plan is for it to be submitted to a 'fixed' version of
# the SobekCM 4.9.0 builder (per issue Sobek-159 on the Jira dev site) that will be put temporarily in place
# on the evening of 4/12/2016, specifically to process this output.
# Given (1) a list of (probably elsevier) bib_vids to delete from UFDC and
# (2) an output directory,
# Output in the output directory a sub-directory for each bib_vid that contains a METS file to delete that bib_vid.
# Note that these sub-directories are suitable to be copy-pasted into an 'inbound' folder that a sobekcm 4.9.0
# 'builder' process (modified with Richard Bernardy's Sobek-159 issue fix in his note of 3/5/2016) is
# monitoring for its input and processing.

import datetime
import pytz
import os


str_mets_delete = '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<!--  This record is getting deleted. ( Unknown ) -->
<METS:mets OBJID="{bibid}_{vid}"
  xmlns:METS="http://www.loc.gov/METS/"
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
    http://sobekrepository.org/schemas/sobekcm.xsd">
<METS:metsHdr CREATEDATE="2016-04-08T11:26:01Z" ID="{bibid}_{vid}" LASTMODDATE="2016-04-08T11:26:01Z" RECORDSTATUS="DELETE">
</METS:metsHdr>
<METS:dmdSec ID="DMD1">
<METS:mdWrap MDTYPE="MODS"  MIMETYPE="text/xml" LABEL="MODS Metadata">
<METS:xmlData>
<mods:mods>
<mods:recordInfo>
<mods:recordIdentifier source="sobekcm">{bibid}_{vid}</mods:recordIdentifier>
</mods:recordInfo>
<mods:titleInfo>
<mods:title>This record is getting deleted.</mods:title>
</mods:titleInfo>
</mods:mods>
</METS:xmlData>
</METS:mdWrap>
</METS:dmdSec>
<METS:dmdSec ID="DMD2">
<METS:mdWrap MDTYPE="OTHER"  OTHERMDTYPE="SOBEKCM" MIMETYPE="text/xml" LABEL="SobekCM Custom Metadata">
<METS:xmlData>
<sobekcm:procParam>
</sobekcm:procParam>
<sobekcm:bibDesc>
<sobekcm:BibID>{bibid}</sobekcm:BibID>
<sobekcm:VID>{vid}</sobekcm:VID>
</sobekcm:bibDesc>
</METS:xmlData>
</METS:mdWrap>
</METS:dmdSec>
<METS:structMap ID="STRUCT1" > <METS:div /> </METS:structMap>
</METS:mets>'''

def make_mets_deletes(inp_bibvid_filename=None, out_dir_root=None):

    with open(inp_bibvid_filename,"r") as input_file:
        i = 0
        for line in input_file:
            line = line.replace('\n','')
            i += 1;
            parts = line.split(',')
            itemid = parts[0]
            bib = parts[1]
            vid = parts[2]
            bibvid = "{}_{}".format(bib,vid)
            out_dir_bib = '{}/{}'.format(out_dir_root, bibvid)
            os.makedirs(out_dir_bib, exist_ok=True)
            out_mets_filename = '{}/{}.mets'.format(out_dir_bib,bibvid)
            with open(out_mets_filename,"w") as output_file:
                print(str_mets_delete.format(bibid=bib,vid=vid), file=output_file)

        # end all bib_vids
    pass


inp_bibvid_filename = 'c:/users/lib-adm-podengo/downloads/elsevier/production_items/old_batch_itemid_table.txt'
out_dir_root = 'c:/users/lib-adm-podengo/Downloads/elsevier/output_mets_deletes'


make_mets_deletes(inp_bibvid_filename=inp_bibvid_filename, out_dir_root=out_dir_root)
print("Done")
