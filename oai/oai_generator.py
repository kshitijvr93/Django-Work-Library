'''
Program oai_generator supports reading from a configured oai feed and producing saved output files.

zenodo was used as a test base, and others like miami-merrick, and more may be added as this approach
will be refined with experience... 20170804

Strings like oai_mets_format_str are python format string templates
designed to use to create a mets file for ufdc from an oai (zenodo) response to a ListRecords
request.

The format variables used in the string are designed
to be generated by crosswalking xml values that are parsed from an oai
response source.

This is initially used to translate 'zenodo' MD records from their OAI-PMH
feed to mets for UFDC SobekCM ingestion.
'''
#Get local pythonpath of modules from 'citrus' main project directory
import sys, os, os.path, platform

# Note: expanduser depends on HOME and USERPROFILE vars that may get changed by
# Automatic updates, (this happened to me, causing much angst) so be explicit.
env_var = 'HOME' if platform.system().lower() == 'linux' else 'USERPROFILE'
path_user = os.environ.get(env_var)

print("Using path_user='{}'".format(path_user))

# For this user, add this project's modules to sys.path
path_modules = '{}/git/citrus/modules'.format(path_user)
print("Using path_modules='{}'".format(path_modules))
sys.path.append(path_modules)

print("using sys.path='{}'".format(sys.path))

import etl
from lxml.etree import tostring
import xml.etree.ElementTree as ET

zenodo_mets_format_str = '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<!--  METS/mods file designed to describe a Zenodo OAI-PMH extracted MD  -->

<METS:mets OBJID="{bib_vid}"
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

<METS:metsHdr CREATEDATE="{create_date}" ID="{bib_vid}"
  LASTMODDATE="{last_mod_date}" RECORDSTATUS="COMPLETE">

<METS:agent ROLE="CREATOR" TYPE="ORGANIZATION">
  <METS:name>IUF, University of Florida</METS:name>
</METS:agent>

<METS:agent ROLE="CREATOR" OTHERTYPE="SOFTWARE" TYPE="OTHER">
  <METS:name>Marshal API Harvester 0.1</METS:name>
</METS:agent>

<METS:agent ROLE="CREATOR" TYPE="INDIVIDUAL">
  <METS:name>{agent_creator_individual_name}</METS:name>
  <METS:note>{agent_creator_individual_note}</METS:note>
</METS:agent>
</METS:metsHdr>

<METS:dmdSec ID="DMD1">
<METS:mdWrap MDTYPE="MODS" MIMETYPE="text/xml" LABEL="MODS Metadata">
<METS:xmlData>

<mods:mods>
{description}
</mods:abstract>

<mods:accessCondition>{rights_text}</mods:accessCondition>
<mods:identifier type="zenodo">{identifier}</mods:identifier>
<mods:genre authority="{genre_authority}">{genre}</mods:genre>
<mods:identifier type="doi">{doi}</mods:identifier>
<mods:language>
<mods:languageTerm type="text">eng</mods:languageTerm>
<mods:languageTerm type="code" authority="iso639-2b">eng</mods:languageTerm>
</mods:language>

<mods:location>
  <mods:url displayLabel="External Link">{related_url}</mods:url>
</mods:location>
<mods:location>
  <mods:physicalLocation>University of Florida</mods:physicalLocation>
  <mods:physicalLocation type="code">UF</mods:physicalLocation>
</mods:location>

<mods:typeOfResource>text</mods:typeOfResource>
<mods:name type="corporate">
  <mods:namePart>University of Florida</mods:namePart>
  <mods:role>
    <mods:roleTerm type="text">host institution</mods:roleTerm>
  </mods:role>
</mods:name>
<mods:name type="personal">
  <mods:namePart>{creator}</mods:namePart>
  <mods:role>
    <mods:roleTerm type="text">creator</mods:roleTerm>
  </mods:role>
</mods:name>

<!-- subject topics: var mods_subjects may be phrases with no authority info -->
{mods_subjects}
<mods:note displayLabel="Harvest Date">{utc_secs_z}</mods:note>

<mods:recordInfo>
  <mods:recordIdentifier source="sobekcm">{bib_vid}</mods:recordIdentifier>
  <mods:recordContentSource>Zenodo</mods:recordContentSource>
</mods:recordInfo>
<mods:titleInfo>
  <mods:title>{title}</mods:title>
</mods:titleInfo>
</mods:mods>
</METS:xmlData>

</METS:mdWrap>
</METS:dmdSec>

<METS:dmdSec ID="DMD2">
<METS:mdWrap MDTYPE="OTHER" OTHERMDTYPE="SOBEKCM" MIMETYPE="text/xml" LABEL="SobekCM Custom Metadata">

<METS:xmlData>
    <sobekcm:procParam>
    {xml_sobekcm_aggregations}
    {xml_sobekcm_wordmarks}
    <sobekcm:Tickler>{sha1-mets-v1}</sobekcm:Tickler>
    </sobekcm:procParam>
    <sobekcm:bibDesc>
        <sobekcm:BibID>{bibid}</sobekcm:BibID>
        <sobekcm:VID>{vid}</sobekcm:VID>
        <sobekcm:Affiliation>
          <sobekcm:HierarchicalAffiliation>
           <sobekcm:Center>University of Florida</sobekcm:Center>
          </sobekcm:HierarchicalAffiliation>
        </sobekcm:Affiliation>
        <sobekcm:Publisher>
        <sobekcm:Name>Zenodo</sobekcm:Name>
        </sobekcm:Publisher>
        <sobekcm:Source>
        <sobekcm:statement code="ZENODO">Zenodo
        </sobekcm:statement>
        </sobekcm:Source>
    </sobekcm:bibDesc>
</METS:xmlData>

</METS:mdWrap>
</METS:dmdSec>

<METS:structMap ID="STRUCT1" > <METS:div /> </METS:structMap>
</METS:mets>
'''
#
merrick_mets_format_str = '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<!--  METS/mods file designed to describe OAI-PMH extracted MD from Miami-Merrick -->

<METS:mets OBJID="{bib_vid}"
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

<METS:metsHdr CREATEDATE="{create_date}" ID="{bib_vid}"
  LASTMODDATE="{last_mod_date}" RECORDSTATUS="COMPLETE">

<METS:agent ROLE="CREATOR" TYPE="ORGANIZATION">
  <METS:name>IUF, University of Florida</METS:name>
</METS:agent>

<METS:agent ROLE="CREATOR" OTHERTYPE="SOFTWARE" TYPE="OTHER">
  <METS:name>UF Marshal API Harvester 0.2</METS:name>
</METS:agent>

<METS:agent ROLE="CREATOR" TYPE="INDIVIDUAL">
  <METS:name>{agent_creator_individual_name}</METS:name>
  <METS:note>{agent_creator_individual_note}</METS:note>
</METS:agent>
</METS:metsHdr>

<METS:dmdSec ID="DMD1">
<METS:mdWrap MDTYPE="MODS" MIMETYPE="text/xml" LABEL="MODS Metadata">
<METS:xmlData>

<mods:mods>
<mods:abstract>
{description}
</mods:abstract>

<mods:accessCondition>{rights_text}</mods:accessCondition>
<mods:identifier type="miami_merrick_2017">{identifier}</mods:identifier>
{xml_dc_ids}
<mods:genre authority="{genre_authority}">{genre}</mods:genre>
<mods:language>
<mods:languageTerm type="text">eng</mods:languageTerm>
<mods:languageTerm type="code" authority="iso639-2b">eng</mods:languageTerm>
</mods:language>

<mods:location>
  <mods:url displayLabel="External Link">{related_url}</mods:url>
</mods:location>

<mods:location>
  <mods:physicalLocation>University of Miami Libraries</mods:physicalLocation>
  <mods:physicalLocation type="code">iUM</mods:physicalLocation>
</mods:location>

<mods:typeOfResource>text</mods:typeOfResource>
<mods:name type="corporate">
  <mods:namePart>University of Florida</mods:namePart>
  <mods:role>
    <mods:roleTerm type="text">host institution</mods:roleTerm>
  </mods:role>
</mods:name>
<mods:name type="personal">
  <mods:namePart>{creator}</mods:namePart>
  <mods:role>
    <mods:roleTerm type="text">creator</mods:roleTerm>
  </mods:role>
</mods:name>

<!-- subject topics: var mods_subjects may be phrases with no authority info -->
{mods_subjects}
<mods:note displayLabel="Harvest Date">{utc_secs_z}</mods:note>

<mods:recordInfo>
  <mods:recordIdentifier source="sobekcm">{bib_vid}</mods:recordIdentifier>
  <mods:recordContentSource>University of Miami Libraries</mods:recordContentSource>
</mods:recordInfo>
<mods:titleInfo>
  <mods:title>{title}</mods:title>
</mods:titleInfo>
</mods:mods>
</METS:xmlData>

</METS:mdWrap>
</METS:dmdSec>

<METS:dmdSec ID="DMD2">
<METS:mdWrap MDTYPE="OTHER" OTHERMDTYPE="SOBEKCM" MIMETYPE="text/xml" LABEL="SobekCM Custom Metadata">

<METS:xmlData>
    <sobekcm:procParam>
    {xml_sobekcm_aggregations}
    {xml_sobekcm_wordmarks}
    <sobekcm:MainThumbnail>{sobekcm_thumbnail_src}</sobekcm:MainThumbnail>
    <sobekcm:Tickler>{sha1-mets-v1}</sobekcm:Tickler>
    </sobekcm:procParam>
    <sobekcm:bibDesc>
        <sobekcm:BibID>{bibid}</sobekcm:BibID>
        <sobekcm:VID>{vid}</sobekcm:VID>
        <sobekcm:Affiliation>
          <sobekcm:HierarchicalAffiliation>
           <sobekcm:Center>University of Florida</sobekcm:Center>
          </sobekcm:HierarchicalAffiliation>
        </sobekcm:Affiliation>
        <sobekcm:Source>
        <sobekcm:statement code="iUM">University of Miami Libraries</sobekcm:statement>
        </sobekcm:Source>
    </sobekcm:bibDesc>
</METS:xmlData>

</METS:mdWrap>
</METS:dmdSec>

<METS:structMap ID="STRUCT1" > <METS:div /> </METS:structMap>
</METS:mets>
''' # end merrick_mets_format_str
#
################################################3

from lxml import etree
import datetime
import requests

'''
Method add_curl_command
create curl command line from info in d_request
useful for diagnostic output.
Store it in d_request['curl_command']
'''
def add_curl_command(d_request):
    curl_options = 'curl -i '
    for key,val in d_request['d_request_headers'].items():
        curl_options += '-H "' + str(key) + ':' + str(val) + '" '
    d_request['curl'] = curl = curl_options + '"' + d_request['url'] +'"'
    #print("Curl={}".format(curl))
    return

'''
<summary>Accept a node_record as an lxml root document and for the given set_spec
write a METS file for the record</summary>

'''
def zenodo_node_writer(node_record=None, namespaces=None, output_folder=None,bib_vid='XX00000000_00001'
  ,set_spec=None,metadata_prefix=None,verbosity=0):
    me = 'zenodo_node_writer'
    required_params = ['set_spec', 'metadata_prefix','node_record','namespaces'
      ,'output_folder','bib_vid']
    if not all(required_params):
      raise ValueError("{}:Some params are not given: {}".format(me,required_params))

    bibid = bib_vid[2:10]
    vid = bib_vid[11:16]

    node_type= node_record.find(".//{*}type", namespaces=namespaces)
    genre = '' if not node_type else node_type.text

    header_identifier_text = ( node_record.find(
      "./{*}header/{*}identifier", namespaces=namespaces).text )
    identifier_normalized = (header_identifier_text
      .replace(':','_').replace('/','_').replace('.','-') )
    print("using bib={}, vid={}, bib_vid={} to output item with zenodo identifier_normalized={}"
          .format(bibid,vid,bib_vid, identifier_normalized))
    #zenodo_string_xml = etree.tostring(node_record, pretty_print=True)

    # Parse the input record and save it to a string
    record_str = etree.tostring(node_record, pretty_print=True, xml_declaration=True,encoding="utf-8")
    print("{}:Got record string={}".format(me,record_str))

    output_folder_xml = output_folder + 'xml/'
    # TO CONSIDER: maybe add a class member flag to delete all preexisting files in this directory?
    # maybe dir for mets too?
    os.makedirs(output_folder_xml, exist_ok=True)
    filename_xml = output_folder_xml + identifier_normalized + './xml'

    with open(filename_xml, mode='w', encoding='utf-8') as outfile_xml:
        print("{}:Writing filename_xml ='{}'".format(me,filename_xml))
        outfile_xml.write(record_str)

    # Set some variables to potentially output into the METS template
    utc_now = datetime.datetime.utcnow()
    utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")

    node_mdf = node_record.find(".//{*}dc", namespaces=namespaces)
    if node_mdf is None:
        # This happens for received 'delete' records
        # Just return None to ignore them pending requirements to process them
        #print ("Cannot find node_mdf for xml tag/node: {*}dc")
        return 0
    else:
      #print("{}: Got node_mdf with tag='{}'",format(node_mdf.tag))
      pass

    node_creator = node_mdf.find(".//{*}creator", namespaces=namespaces)
    dc_creator = '' if node_creator is None else node_creator.text
    dc_creator = etl.escape_xml_text(dc_creator)
    #print("{}:Got creator={}".format(me,dc_creator))

    dc_date_orig = node_mdf.find("./{*}date", namespaces=namespaces).text
    #print("Got dc date orig={}".format(dc_date_orig))
    # Must convert dc_date_orig to valid METS format:
    # If we get only a year, pad it to year-01-01 to make
    # it valid for this field.
    if len(dc_date_orig) < 5:
        dc_date_orig += "01-01"
    dc_date = '{}T12:00:00Z'.format(dc_date_orig)
    #print("Got dc_date='{}'".format(dc_date))

    node_description = node_mdf.find(".//{*}description",namespaces=namespaces)
    # Make an element trree style tree to invoke pattern to remove innter xml
    str_description = tostring(node_description,encoding='unicode',method='text').strip().replace('\n','')
    str_description = etl.escape_xml_text(str_description)

    # Special doctype needed to handle nbsp... copyright
    xml_dtd = '''<?xml version="1.1" encoding="UTF-8" ?><!DOCTYPE naughtyxml [
        <!ENTITY nbsp "&#0160;">
        <!ENTITY copy "&#0169;">
        ]>'''

    xml_description =  '{}<doc>{}</doc>'.format(xml_dtd,str_description)
    print("Got str_description='{}'".format(str_description))
    print("Got xml_description='{}'".format(xml_description))
    print
    if (1 ==2):
        # See: https://stackoverflow.com/questions/19369901/python-element-tree-extract-text-from-element-stripping-tags#19370075
        tree_description = ET.fromstring(xml_description)
        dc_description = etl.escape_xml_text(''.join(tree_description.itertext()))
    else:
        dc_description = etl.escape_xml_text(xml_description)
        print("Using dc_description='{}'".format(dc_description))


    # NOTE:inferred the identifier indexes by pure manual inspection of the merrick
    # ListRecords results

    nodes_identifier = node_mdf.findall(".//{*}identifier", namespaces=namespaces)
    doi = nodes_identifier[0].text
    if len(nodes_identifier) > 1:
        zenodo_id = nodes_identifier[1].text
    related_url = '{}'.format(doi)

    #relation_doi = node_mdf.find(".//{*}relation").text
    nodes_rights = node_mdf.findall(".//{*}rights", namespaces=namespaces)
    rights_text = 'See:'
    for node_rights in nodes_rights:
        rights_text += ' ' + node_rights.text
    rights_text = etl.escape_xml_text(rights_text)

    nodes_subject = node_mdf.findall(".//{*}subject", namespaces=namespaces)
    mods_subjects = ''
    for node_subject in nodes_subject:
        mods_subjects += ('<mods:subject><mods:topic>' + etl.escape_xml_text(node_subject.text)
          + '</mods:topic></mods:subject>\n')

    dc_title = node_mdf.find(".//{*}title", namespaces=namespaces).text
    dc_title = etl.escape_xml_text(dc_title)

    sobekcm_aggregations = ['UFDATASETS']
    xml_sobekcm_aggregations = ''
    for aggregation in sobekcm_aggregations:
        xml_sobekcm_aggregations += (
            '<sobekcm:Aggregation>{}</sobekcm:Aggregation>'
            .format(aggregation))

    # Apply basic input values to METS template variables

    d_var_val = {
        'bib_vid' : bib_vid,
        'create_date' : dc_date,
        'last_mod_date' : utc_secs_z,
        'agent_creator_individual_name': dc_creator,
        'agent_creator_individual_note' : 'Creation via zenodo harvest',
        'identifier' : header_identifier_text,
        'mods_subjects' : mods_subjects,
        'rights_text' : rights_text,
        'utc_secs_z' :  utc_secs_z,
        'title' : dc_title,
        'related_url' : related_url,
        'xml_sobekcm_aggregations' : xml_sobekcm_aggregations,
        'xml_sobekcm_wordmarks' : xml_sobekcm_wordmarks,
        'doi': doi,
        'description' : dc_description,
        'creator' : dc_creator,
        'bibid': bibid,
        'vid': vid,
        'sha1-mets-v1' : '',
        'genre' : 'dataset',
        'genre_authority': 'zenodo',
    }

    # Create mets_str and write it
    mets_str = zenodo_mets_format_str.format(**d_var_val)
    output_folder_mets = output_folder + 'mets/'
    os.makedirs(output_folder_mets, exist_ok=True)

    filename_mets = output_folder_mets  + bib_vid + '.mets.xml'
    fn = filename_mets
    with open(fn, mode='w', encoding='utf-8') as outfile:
        print("{}:Writing METS filename='{}'".format(me,fn))
        outfile.write(mets_str.encode('utf-8'))
    return 1
    #end def zenodo_node_writer

def merrick_node_writer(node_record=None, namespaces=None, output_folder=None
  , set_spec=None, metadata_prefix=None, bib_vid='XX00000000_00001'
  , verbosity=0):
    me = 'merrick_node_writer'
    required_params = ['set_spec','metadata_prefix'
        ,'node_record','namespaces','output_folder','bib_vid']
    if not all(required_params):
      raise ValueError("{}:Some params are not given: {}".format(me,required_params))

    bibint = bib_vid[2:10]
    bibid = bib_vid[:10]
    vid = bib_vid[11:16]

    # Consider: also save text from the xml and put in METS notes?
    # <set_spec>,
    # add note for identifier0 vs identifier1... ordering..

    node_type= node_record.find(".//{*}type", namespaces=namespaces)
    genre = '' if node_type is None else node_type.text
    genre = etl.escape_xml_text(genre)

    node_identifier = node_record.find("./{*}header/{*}identifier", namespaces=namespaces)
    header_identifier_text = '' if node_identifier is None else node_identifier.text

    header_identifier_normalized = (header_identifier_text
      .replace(':','_').replace('/','_').replace('.','-'))

    if verbosity > 0:
        print("using bib={}, vid={}, bib_vid={} to output item with "
          "merrick header_identifier_normalized={}"
          .format(bibid,vid,bib_vid, header_identifier_normalized))

    # Parse the input record and save it to a string
    record_str = etree.tostring(node_record, pretty_print=True, encoding='unicode')
    # print("{}:Got record string={}".format(me,record_str))

    output_folder_xml = output_folder + 'xml/'
    # TO CONSIDER: maybe add a class member flag to delete all preexisting
    # files in this directory? maybe dir for mets too?
    os.makedirs(output_folder_xml, exist_ok=True)
    #print("{}:using output_folder_xml={}".format(me,output_folder_xml))

    filename_xml = output_folder_xml + header_identifier_normalized + '.xml'
    with open(filename_xml, mode='w', encoding='utf-8') as outfile:
        #print("{}:Writing filename_xml ='{}'".format(me, filename_xml))
        outfile.write(record_str)

    # Set some variables to potentially output into the METS template
    utc_now = datetime.datetime.utcnow()
    utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")

    node_mdf = node_record.find(".//{*}dc", namespaces=namespaces)

    if node_mdf is None:
        # This happens for received 'delete' records
        # Just return None to ignore them pending requirements to process them
        #print ("Cannot find node_mdf for xml tag/node: {*}dc")
        return 0
    else:
      #print("{}: Got node_mdf with tag='{}'",format(node_mdf.tag))
      pass

    #print("{}:got namespaces='{}'".format(me,repr(namespaces)))

    node_creator = node_mdf.find(".//{*}creator", namespaces=namespaces)
    dc_creator = '' if node_creator is None else node_creator.text
    dc_creator = etl.escape_xml_text(dc_creator)
    #print("{}:Got creator={}".format(me,dc_creator))

    node_date = node_mdf.find("./{*}date", namespaces=namespaces)
    dc_date_orig='1969-01-01'
    if node_date is not None:
        dc_date_orig = node_date.text
    # If we get only a year, pad it to year-01-01 to make
    # it valid for this field.
    if len(dc_date_orig) < 5:
        dc_date_orig += "-01-01"
    elif len(dc_date_orig) < 8:
        dc_date_orig += "-01"

    dc_date = '{}T12:00:00Z'.format(dc_date_orig)
    # print("Got dc date orig={}".format(dc_date_orig))
    # Must convert dc_date_orig to valid METS format:
    dc_date = '{}T12:00:00Z'.format(dc_date_orig)
    #print("{}:Got dc_date='{}'".format(me,dc_date))

    node_description = node_mdf.find(".//{*}description",namespaces=namespaces)
    # Make an element tree style tree to invoke pattern to remove inner xml
    #str_description = etree.tostring(node_description,encoding='unicode',method='text').strip().replace('\n','')
    str_description = ''
    if (node_description is not None):
        #str_description = etree.tostring(node_description,encoding='unicode').strip().replace('\n','')
        str_description = etl.escape_xml_text(node_description.text)

    if (1 ==1):
        dc_description = str_description
        # avoid charmap codec windows errors:print("Using dc_description='{}'".format(dc_description))

    nodes_dc_identifier = node_mdf.findall(
      ".//{*}identifier", namespaces=namespaces)

    xml_dc_ids = '\n'
    related_url = ''
    # id type names based on data received in 2017
    # I invented the id_types, based on the data harvested in 2017.
    id_types = ['merrick_set_spec_index', 'merrick_url']
    for i,nid in enumerate(nodes_dc_identifier):
        xml_dc_ids = ('<mods:identifier type="{}">{}</mods:identifier>\n'
          .format(id_types[i], nid.text))
        if (i == 1):
          related_url = nid.text

    # Create thumbnail src per algorithm provided 20170807 by elliot williams,
    # Digital Initiatives MD Librarian, of Miami-Merrick
    thumbnail_src = 'http://merrick.library.miami.edu/utils/getthumbnail/collection/'
    thumbnail_src += '/'.join(related_url.split('/')[-3:])

    nodes_rights = node_mdf.findall(".//{*}rights",namespaces=namespaces)
    # rights-text per UF email from Laura Perry to rvp 20170713
    rights_text = '''This item was contributed to the Digital Library
of the Caribbean (dLOC) by the source institution listed in the metadata.
This item may or may not be protected by copyright in the country
where it was produced. Users of this work have responsibility for
determining copyright status prior to reusing, publishing or
reproducing this item for purposes other than what is allowed by
applicable law, including any applicable international copyright
treaty or fair use or fair dealing statutes, which dLOC partners
have explicitly supported and endorsed. Any reuse of this item
in excess of applicable copyright exceptions may require
permission. dLOC would encourage users to contact the source
institution directly or dloc@fiu.edu to request more information
about copyright status or to provide additional information about
the item.'''

    # Some list-variable input values
    for node_rights in nodes_rights:
        rights_text += '\n' + node_rights.text
    rights_text = etl.escape_xml_text(rights_text)

    # Subjects
    nodes_subject = node_mdf.findall(".//{*}subject", namespaces=namespaces)
    mods_subjects = '<mods:subject>'
    for node_subject in nodes_subject:
        subjects = node_subject.text.split(';')
        for subject in subjects:
          subject = subject.strip()
          if len(subject) < 1:
            continue
          mods_subjects += '<mods:topic>' + etl.escape_xml_text(subject) + '</mods:topic>\n'
    mods_subjects += ('</mods:subject>\n')

    tnode = node_mdf.find(".//{*}title", namespaces=namespaces)
    dc_title = '(none)' if tnode is None else etl.escape_xml_text(tnode.text)

    tnode = node_mdf.find(".//{*}type", namespaces=namespaces)
    dc_title = '' if tnode is None else etl.escape_xml_text(tnode.text)

    sobekcm_aggregations = ['ALL', 'DLOC1', 'IUM']
    xml_sobekcm_aggregations = ''
    for aggregation in sobekcm_aggregations:
        xml_sobekcm_aggregations += (
            '<sobekcm:Aggregation>{}</sobekcm:Aggregation>'
            .format(aggregation))
    sobekcm_wordmarks = ['UM','DLOC']
    xml_sobekcm_wordmarks = ''
    for wordmark in sobekcm_wordmarks:
        xml_sobekcm_wordmarks += (
            '<sobekcm:Wordmark>{}</sobekcm:Wordmark>\n'
            .format(wordmark))

    # Set some template variable values
    d_var_val = {
        'bib_vid' : bib_vid,
        'create_date' : dc_date,
        'last_mod_date' : utc_secs_z,
        'agent_creator_individual_name': dc_creator,
        'agent_creator_individual_note' : 'Creation via Miami-Merrick OAI  harvest',
        'identifier' : header_identifier_text,
        'mods_subjects' : mods_subjects,
        'rights_text' : rights_text,
        'utc_secs_z' :  utc_secs_z,
        'title' : dc_title,
        'related_url' : related_url,
        'xml_sobekcm_aggregations' : xml_sobekcm_aggregations,
        'xml_sobekcm_wordmarks' : xml_sobekcm_wordmarks,
        'sobekcm_thumbnail_src' : thumbnail_src,
        'xml_dc_ids' : xml_dc_ids,
        'description' : dc_description,
        'creator' : dc_creator,
        'bibid': bibid,
        'vid': vid,
        'sha1-mets-v1' : '',
        'genre' : '',
        'genre_authority': '',
    }

    # Create mets_str and write it to mets.xml output file
    mets_str = merrick_mets_format_str.format(**d_var_val)
    # Nest filename in folder of the bib_vid,
    # because loads in sobek bulder faster this way
    output_folder_mets = output_folder + 'mets/' + bib_vid + '/'
    os.makedirs(output_folder_mets, exist_ok=True)

    filename_mets = output_folder_mets  + bib_vid + '.mets.xml'
    fn = filename_mets
    with open(fn, mode='w', encoding='utf-8') as outfile:
        #print("{}:Writing METS filename='{}'".format(me,fn))
        #outfile.write(mets_str.encode('utf-8'))
        outfile.write(mets_str)
    return 1
    #end def merrick_node_writer

class OAI_Harvester(object):
  '''
  <synopsis name='OAI_Harvester'>
  <summary>OAI_Harvester encapsulates information required to make requests to a
  specific OAI server. It also contains
  (1) a generator method named list_nodes_record() to read the OAI server listRecords
  and parse it into a node_record xml object that is returned
  </summary>
  <param name="node_writer">A function that takes arguments of (1) node_record and
  (2) namespaces (eg, the return values from a call to list_nodes_record() ,
  (3) output_folder, and for other params, see calls to it in this source code.
</param>
  </synopsis>
  '''
  def __init__(self, oai_url=None, output_folder=None,bib_prefix='XX'
      ,bib_zfills=[8,5], bib_last=0, d_crosswalk=None, str_output_format=None
      ,node_writer=None, set_spec=None, metadata_format=None
      ,record_xpath=".//{*}record",verbosity=None):

    required_pnames = ['set_spec','metadata_format','node_writer','oai_url','output_folder',]
    if not all([output_folder, oai_url]):
      raise ValueError("Error: Some parameters not set: {}.".format(required_pnames))
    self.oai_url = oai_url
    self.output_folder = output_folder
    self.bib_prefix = bib_prefix
    self.bib_zfills = bib_zfills
    self.bib_last = bib_last
    self.d_crosswalk = d_crosswalk
    self.str_output_format = str_output_format
    self.node_writer = node_writer
    self.record_xpath = record_xpath
    # namespaces will be reset by each xml file inputted by list_nodes_record()
    self.namespaces = None #will be overwritten when each xml file is input by the list_nodes_record
    self.set_spec = set_spec
    self.metadata_format = metadata_format

    # Later: use API with verb metadataFormats to get them. Now try a one-size-fits-all list
    self.metadata_formats=['oai_dc','oai_qdc']
    self.verbosity = verbosity # default verbosity
    self.basic_verbs = [ # see http://www.oaforum.org/tutorial/english/page4.htm
         'GetRecord', 'Identify'
         , 'ListIdentifiers', 'ListMetaDataFormats', 'ListRecords' , 'ListSets'
    ]
    return

  def url_list_records(self):
    url = ("{}?verb=ListRecords&set={}&metadataPrefix={}"
      .format(self.oai_url,self.set_spec,self.metadata_format))
    return url

  def url_list_sets(self):
    url = ("{}?verb=ListSets&metadataPrefix={}"
      .format(self.oai_url,self.metadata_format))
    return url

  def list_nodes_record(self, verbosity=0):
    pnames = ['metadata_format','set_spec',]
    me = 'list_nodes_record'
    metadata_format = self.metadata_format
    set_spec = self.set_spec

    if not all(set_spec):
      raise ValueError("Error: Some parameters not set: {}.".format(pnames))

    n_batch = 0;
    url_list = self.url_list_records()
    while (url_list is not None):
      n_batch += 1
      if n_batch > 2:
          break
      response = requests.get(url_list)

      print("Using url_list='{}'\nand got response with apparent_encoding='{}', encoding='{}',headers:"
            .format(url_list, response.apparent_encoding, response.encoding))
      for k,v in response.headers.items():
          print("{}:{}".format(k,v))

      response_str = requests.utils.get_unicode_from_response(response)
      encodings = requests.utils.get_encodings_from_content(response_str)
      print("Encoding from unicode response_str='{}'".format(encodings))

      # see http://docs.python-requests.org/en/latest/api/#main-interface
      # It says that one may  set response.encoding before accessing response.text
      # response.encoding = 'utf-8' # utf-8 did not work to interpret accent characters.
      # It seems Miami-Merrick server sends out ISO-8559-1 format
      # Set it explicitly, to match the Miami-Merrick encoding
      # requests' package 'usually' 'detects' this from the server and sets it,
      # but it seems to not work.
      # A fundamental python principle is 'explict is better than  implicit', so set it here.
      # response.encoding = 'ISO-8859-1' # that fails! But next call to encode() seems to work.
      xml_bytes = response.text.encode('ISO-8859-1')
      print("xml_bytes len={}, response.encoding={}".format(len(xml_bytes), response.encoding))
      print("-----------------\n")

      try:
          node_root = etree.fromstring(xml_bytes)
          #node_root = etree.fromstring(response_str) #error: unicode strings not supported
      except Exception as e:
          print("For batch {}, made url request ='{}'.\nSkipping batch with Parse() exception='{}'"
                .format(n_batch, url_list, repr(e)))

          print("Traceback: {}".format(traceback.format_exc()))
          # Break here - no point to continue because we cannot parse/discover the resumptionToken
          break
      # str_pretty = etree.tostring(node_root, pretty_print=True)
      d_namespaces={key:value for key,value in dict(node_root.nsmap).items() if key is not None}
      # Can set self.namespaces here, or could return namespaces in a tuple value from the yield,
      # but this  somehow seems a better way to possibly support future methods
      self.namespaces=d_namespaces
      # NOTE: namespace 'dc' is not explicitly listed in the API response
      #print("{}:got self.namespaces='{}'".format(me,repr(self.namespaces)))

      nodes_record = node_root.findall(self.record_xpath, namespaces=d_namespaces)
      print("From the xml found {} xml tags for records".format(len(nodes_record)))
      print ("ListRecords request found root tag name='{}', and {} records"
             .format(node_root.tag, len(nodes_record)))

      # For every input node/record, yield it so caller can write an output file.
      for node_record in nodes_record:
          yield (d_namespaces, node_record)

      node_resumption = node_root.find('.//{*}resumptionToken', namespaces=d_namespaces)
      url_list = None
      if node_resumption is not None:
          # Note: manioc allows no other args than resumption token, so
          # also do not specify/restate the metadataPrefix with all oai servers
          #url_list = ('{}?verb=ListRecords&set={}&metadataPrefix=oai_dc&resumptionToken={}'
          #    .format(self.url_base, set_spec, node_resumption.text))

          url_list = ('{}?verb=ListRecords&resumptionToken={}'
              .format(self.oai_url,  node_resumption.text))
      if verbosity > 0:
          print("{}:Next url='{}'".format(me,url_list))
    # end while url_list is not None
    return None

  # end def reader_list_records()

  def output_records(self):
    num_records = num_deleted = 0
    bibvid = self.bib_prefix + str(self.bib_last).zfill(self.bib_zfills[0]) + '00001' #may implement vid later
    output_folder_format = '{}/{}/'.format(self.output_folder, self.metadata_format)

    # increment the candiate bib_last integer to offer for the output of the next mets
    self.bib_last += 1

    for (namespaces, node_record) in oai.list_nodes_record():
      bib_vid = self.bib_prefix + str(self.bib_last).zfill(8) + '_00001' #may implement vid later

      # Call crosswalk this xml node's record content to output the record to a file
      # zw = self.node_writer()
      if node_record is None:
            break;
      # save the xml in its own output ... folder ***
      #
      # Call the crosswalk function to read the node_record and write mets file output
      rv = self.node_writer(node_record=node_record ,namespaces=namespaces
          ,output_folder=output_folder_format, bib_vid=bib_vid)

      if rv == 0:
          num_deleted += 1
      # Increment the integer bib_last id candidate for the next mets record.
      # NOTE: some received OAI node_records are for 'delete' ,
      # Later - change the node_writer to return true if it wrote a mets
      # and false if it detected a delete record and so did not write a mets.
      # if rv == 1: # uncomment after finishing testing other things to keep bibids the same in meantime
      self.bib_last += 1
      num_records += 1

    return num_records, num_deleted
  # end def output_records()
# end class OAI_Harvester

#
class XmlBibWalker(object):
    ''' DESIGN NOTES - UNDER CONSIDERATION:
    This is considered to separate the writing-side functionality from class OAI_Generator...
    Rather than pass a node_writer and other of the writing-related  parameters to it
    and use OAI_Generator.output_records() to produce output, it may be more useful to have this as
    a separate object -- a good place to also stick bib id management..
    TODO: come back to this later

    Class XmlBibWalker contains  methods and data needed to:
    (1) read the XML root node of an XML object with a required/known schema
    (2) and assign a UF Smathers BIB id to the record (a new one for new-to-UF records
        or a current one for those already in UF - and  other 'lib-marshal'(RedHat host)
        database tables and access methods will be created/employed to  support this management.
        Until then - human inspection and knowledge will be used to provide the last bibid for each
        run...
    (3) and crossWALK the record into a custom output file format (eg METS xml)

    Hence the class name XmlBibWalker.
    The custom handling of the required/known schema is performed by a caller-defined function,
    whose name is given in argument node_writer.
    '''

    def __init__(self, output_folder=None, bib_id_last_str='XX00000000', vid="00001",
        d_crosswalk=None, str_output_template=None, node_writer=None, verbosity=None
        ,bib_prefix_len=2):

      required_pnames = ['node_writer', 'output_folder', 'bib_id_last_str']
      if not all(required_pnames):
          raise ValueError("Error: Some of {} required parameters not set.".format(required_pnames))

      self.output_folder = output_folder

      self.bib_prefix = bib_id_last_str[0:bib_prefix_len];
      self.bibid_places = len(bib_id_last_str) - bib_prefix_len
      self.bibint_last = int(bib_id_last_str[bib_prefix_len:])

      self.d_crosswalk = d_crosswalk
      self.str_output_template = str_output_template
      self.node_writer = node_writer

      # namespaces will be reset by each xml file inputted by list_nodes_record()
      self.namespaces = None #will be overwritten when each xml file is input by the list_nodes_record

      # Later: use API with verb metadataFormats to get them. Now try a one-size-fits-all list
      #
      self.metadata_formats=['oai_dc']
      self.verbosity = verbosity # default verbosity
      self.basic_verbs = [ # see http://www.oaforum.org/tutorial/english/page4.htm
         'GetRecord', 'Identify'
         , 'ListIdentifiers', 'ListMetaDataFormats', 'ListRecords' , 'ListSets'
      ]

      return

      def output_records(self):
          return

#end class XMLCrossWalker
#studies
studies = ['zenodo','merrick']
# Set study config for thus run

study = 'zenodo'
study = 'merrick/chc5017'
study = "manioc/patrimon"

if study == 'zenodo':
  oai_url = 'https://zenodo.org/oai2d'
  set_spec='user-genetics-datasets'
  metadata_format="oai_dc"

  output_folder = etl.data_folder(linux='/home/robert/', windows='U:/',
        data_relative_folder='data/outputs/oai/{}/{}/'.format(study,set_spec))
  print("Study = {}, set_spec={}, base_output_folder={}".format(study,set_spec,output_folder))

  oai = OAI_Harvester(oai_url=oai_url, output_folder=output_folder, bib_prefix="DS"
      ,node_writer=zenodo_node_writer, record_xpath=".//{*}record")

  num_records, num_deleted = oai.output_records()
  print("oai.output_records() returned num_records={}".format(num_records))

elif study.startswith("manioc/"):
  oai_url = 'http://www.manioc.org/phpoai/oai2.php'
  parts = study.split('/')
  study = parts[0]
  set_spec = parts[1]

  # Set one last to test it
  metadata_format="oai_qdc"
  metadata_format="oai_dc"

  output_folder = etl.data_folder(linux='/home/robert/', windows='U:/',
      data_relative_folder='data/outputs/oai/{}/{}/'.format(study,set_spec))
  print("Study = {}, set_spec={}, base_output_folder={}".format(study,set_spec,output_folder))

  oai = OAI_Harvester(oai_url=oai_url, output_folder=output_folder, bib_prefix="CX"
      ,node_writer=merrick_node_writer, set_spec=set_spec
      ,metadata_format=metadata_format, record_xpath=".//{*}record")

  num_records, num_deleted = oai.output_records()
else:
    raise ValueError('ERROR: unknown study={}'.format(study))


print("Generator got info for {} total records, {} deleted. DONE."
      .format(num_records, num_deleted))