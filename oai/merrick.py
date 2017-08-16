#Get local pythonpath of modules from 'citrus' main project directory
import sys, os, os.path, platform
def get_path_modules(verbosity=0):
  env_var = 'HOME' if platform.system().lower() == 'linux' else 'USERPROFILE'
  path_user = os.environ.get(env_var)
  path_modules = '{}/git/citrus/modules'.format(path_user)
  if verbosity > 1:
    print("Assigned path_modules='{}'".format(path_modules))
  return path_modules
sys.path.append(get_path_modules())

import etl
from lxml import etree
from lxml.etree import tostring
import xml.etree.ElementTree as ET
from oai_utils import OAI_Server, OAI_Harvester
import datetime
import shutil

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

'''
The caller must avoid calling the node_writer for records that are error records or
special records (like 'delete' records), which are not suitable for writing.
That is the caller must check for 'error' nodes or any characteristicof the node_record that
makes the record invalid for writing, or makes some of the values that the node_writer
expects from it to be invalid.
NOTE: merrick_mets_format_str is assumed predefined now...
Consider: write a separate log of the bad input node_records, but just skip them when encountered,
or give a 'strict' option to raise an exception.
The caller must also check whether the record is new or an update and caclulate and
provide the appropriate bib_vid for the node_writer to use.
'''

def merrick_node_writer(d_record=None, namespaces=None, output_folder=None
  , set_spec=None, metadata_prefix=None, bib_vid='XX00000000_00001'
  , verbosity=0):
    me = 'merrick_node_writer'
    required_params = ['d_record','namespaces','output_folder','bib_vid']
    if not all(required_params):
      raise ValueError("{}:Some params are not given: {}".format(me,required_params))

    node_record = d_record['node_record']
    namespaces = d_record['namespaces']
    node_record = d_record['node_record']

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
    print("{}:Made mets_str with len={}, writing to {}".format(me,len(mets_str),filename_mets))
    fn = filename_mets
    with open(fn, mode='w', encoding='utf-8') as outfile:
        outfile.write(mets_str)
        return 1
    #end def merrick_node_writer

def run_test():

  study = 'merrick'
  set_spec = 'asm0085'
  metadata_prefix = 'oai_dc'
  bib_vid = 'XX00000000_00001'
  oai_url = 'http://merrick.library.miami.edu/oai/oai.php'
  node_writer = merrick_node_writer
  encoding='ISO_8859_1' #works OK

  output_folder = etl.data_folder(linux='/home/robert/', windows='U:/',
      data_relative_folder='data/outputs/oai/{}/{}/'.format(study,set_spec))

  print("STARTING: run_test: study={},oai_url={},encoding='{}',output_folder={}"
         .format(study,oai_url,encoding,output_folder))

  harvester = OAI_Harvester(oai_url=oai_url, server_encoding=encoding
    , node_writer=node_writer , output_folder=output_folder, verbosity=1 )

  print("run_test: CREATED Harvester {}: Harvesting items now....".format(repr(harvester)))
  max_count = 0
  harvester.harvest_items(
    set_spec=set_spec, metadata_prefix=metadata_prefix,;bib_vid=bib_vid, max_count=max_count)
  print("run_test: DONE!")

run_test()

print("DONE!")
