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

manioc_mets_format_str = """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<!--  METS/mods file designed to describe OAI-PMH (metadataPrefix oai_dc) extracted MetaData -->

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
<mods:identifier type="{source_id_name}">{header_identifier_text}</mods:identifier>
{xml_dc_ids}
<mods:genre authority="{genre_authority}">{genre}</mods:genre>
<mods:language>
<mods:languageTerm type="text">{iso639_2b_text}</mods:languageTerm>
<mods:languageTerm type="code" authority="iso639-2b">{iso639_2b_code}</mods:languageTerm>
</mods:language>

<mods:location>
  <mods:url displayLabel="External Link">{related_url}</mods:url>
</mods:location>

<mods:location>
  <mods:physicalLocation>{physical_location_name}</mods:physicalLocation>
  <mods:physicalLocation type="code">{physical_location_code}</mods:physicalLocation>
</mods:location>

<mods:typeOfResource>text</mods:typeOfResource>
<mods:name type="corporate">
  <mods:namePart>University of Florida</mods:namePart>
  <mods:role>
    <mods:roleTerm type="text">host institution</mods:roleTerm>
  </mods:role>
</mods:name>
<mods:name type="personal">
  <mods:namePart>{personal_creator_name}</mods:namePart>
  <mods:role>
    <mods:roleTerm type="text">{personal_creator_role}</mods:roleTerm>
  </mods:role>
</mods:name>

<mods:originInfo>
<mods:publisher>{publisher}</mods:publisher>
</mods:originInfo>

<!-- subject topics: var mods_subjects may be phrases with no authority info -->
{mods_subjects}
<mods:note displayLabel="Harvest Date">{utc_secs_z}</mods:note>

<mods:recordInfo>
  <mods:recordIdentifier source="sobekcm">{bib_vid}</mods:recordIdentifier>
  <mods:recordContentSource>{content_source_name}</mods:recordContentSource>
</mods:recordInfo>
<mods:titleInfo>
  <mods:title>{mods_title}</mods:title>
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
    <sobekcm:Tickler>{sha1_mets_v1}</sobekcm:Tickler>
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
        <sobekcm:statement code="{physical_location_code}">{physical_location_name}</sobekcm:statement>
        </sobekcm:Source>
    </sobekcm:bibDesc>
</METS:xmlData>
</METS:mdWrap>
</METS:dmdSec>
<METS:structMap ID="STRUCT1" > <METS:div /> </METS:structMap>
</METS:mets>
"""
# end manioc_mets_format_str

'''
The caller must avoid calling the node_writer for records that are error records or
special records (like 'delete' records), which are not suitable for writing.
That is the caller must check for 'error' nodes or any characteristicof the node_record that
makes the record invalid for writing, or makes some of the values that the node_writer
expects from it to be invalid.
NOTE: manioc_mets_format_str is assumed pre-defined now --not an argument in the manioc_node_writer definition
Consider: write a separate log of the bad input node_records, but just skip them when encountered,
or give a 'strict' option to raise an exception.
The caller must also check whether the record is new or an update and caclulate and
provide the appropriate bib_vid for the node_writer to use.
'''

def manioc_node_writer(bib_vid=None, d_record=None, metadata_prefix=None
        , output_folder=None , verbosity=0):
    me = 'manioc_node_writer'
    rparams = ['d_record', 'bib_vid', 'output_folder','metadata_prefix']
    if not all(rparams):
        raise ValueError("Missing some required params from {}".format(repr(rparams)))

    if metadata_prefix != 'oai_dc':
      raise ValueError("{}: Currently only support metadata_prefix of oai_dc, not '{}''"
                      .format(me,metadata_prefix))

    # 20170815 NOTE
    # cannot get shutil to remove older files properly on windows 7...
    # so if needed must remember to remove them by hand before running this.
    output_folder_xml = '{}{}/xml/'.format(output_folder,metadata_prefix)
    os.makedirs(output_folder_xml,exist_ok=True)

    output_folder_mets = '{}{}/mets/'.format(output_folder,metadata_prefix)
    os.makedirs(output_folder_mets,exist_ok=True)
    rights = 'Your rights: '
    d_mets_template = {
        "genre_authority": "Manioc",
        "physical_location_name":"Manioc",
        "physical_location_code":"MANIOC",
        "rights_text": rights,
        # List of extant SobekCM database wordmark codes to derive xml for mets template
        # eg for miami merrick it was ['UM','DLOC']
        "list_sobekcm_wordmarks" : [],
        # List of extant SobekCM database aggregation codes to derive xml for mets template
        "list_sobekcm_aggregations" : ['ALL', ],

        ###########################################################################
        # Following must be or usually are software derived-supplied
        ###########################################################################

        "agent_creator_individual_name" : None,
        "agent_creator_individual_note" : 'Creation via Manioc OAI  harvest',
        "bibid" : None,
        "create_date" : None,
        "description" : None,
        "harvest_utc_secs_z" : None,
        #Consider using this later...
        "header_identifier_text": "",
        "last_mod_date": None,
        "mods_subjects": None,
        "mods_title": None,
        "personal_creator_name": None,
        "personal_creator_role": None,
        "related_url" : None,
        "sha1_mets_v1" : None,
        "sobekcm_thumbnail_src" : "", # Not used for Manioc...  yet...
        "source_id_name":"manioc_OAI_header_identifier_2017",
        "vid" : None,
        "xml_dc_ids": "",
        "xml_sobekcm_aggregations" : "", # Just puts wrapping around list_sobekcm_aggregtions
        "xml_sobekcm_subjects" : "", # Derived from OAI record metadata
        "xml_sobekcm_wordmarks" : "", # Puts xml wrapping around list_sobekcm_wordmarks
    }

    ok_prefixes = [ 'oai_dc',]
    if metadata_prefix not in ok_prefixes:
        raise ValueError("{}:Paramter metadata_prefix {} is not in {}"
          .format(me,metadata_prefix,repr(ok_prefixes)))

    node_record = d_record['node_record']
    namespaces = d_record['namespaces']
    # Note: node_root and n_batch and node_record_count are also in d_record if needed

    bibid = bib_vid[:10]
    if bib_vid[10:11] != '_':
        raise ValueError("Bad bib_vid format for {}".format(bib_vid))
    vid = bib_vid[11:16]

    node_type= node_record.find(".//{*}dc/{*}type", namespaces=namespaces)
    genre = '' if node_type is None else node_type.text
    genre = etl.escape_xml_text(genre)
    d_mets_template['genre'] = genre

    node_identifier = node_record.find("./{*}header/{*}identifier", namespaces=namespaces)
    header_identifier_text = '' if node_identifier is None else node_identifier.text

    header_identifier_normalized = (header_identifier_text
        .replace(':','_').replace('/','_').replace('.','-'))

    if verbosity > 0:
        print("using bib={}, vid={}, bib_vid={} to output item with "
            "manioc header_identifier_normalized={}"
            .format(bibid,vid,bib_vid, header_identifier_normalized))

    nodes_source = node_record.findall(".//{*}dc/{*}publisher", namespaces=namespaces)
    n = 0 if nodes_source is None else len(nodes_source)

    node_source_text = '' if n == 0 else nodes_source[0].text
    d_mets_template['content_source_name'] = node_source_text

    # From node_record,create the b_xml_record_output
    # Note: the encoding argument is needed to create unicode string from
    # lxml internal representation
    xml_record_str = etree.tostring(node_record, pretty_print=True
          , xml_declaration=True, encoding="utf-8")
    if verbosity > 1:
      print("{}:Got xml_record_str={}".format(me,xml_record_str))

    filename_xml = output_folder_xml + header_identifier_normalized + '.xml'
    if verbosity > 0:
          print("{}:using output_filename_xml={}".format(me,filename_xml))

    #with open(filename_xml, mode='w', encoding='utf-8') as outfile:
    with open(filename_xml, mode='wb') as outfile:
          if verbosity> 0:
              print("{}:Writing filename_xml ='{}'".format(me, filename_xml))
          outfile.write(xml_record_str)

      # Set some variables to potentially output into the METS template
    utc_now = datetime.datetime.utcnow()
    utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")
    d_mets_template['utc_secs_z'] = utc_secs_z

    node_mdp = node_record.find(".//{*}dc", namespaces=namespaces)

    if node_mdp is None:
          # This happens for received 'delete' records
          # Just return to ignore these records pending requirements to process them
          # print ("Cannot find node_mdp for xml tag/node: {*}dc")
          return 0
    else:
        #print("{}: Got node_mdp with tag='{}'",format(node_mdp.tag))
        pass

    #print("{}:got namespaces='{}'".format(me,repr(namespaces)))

    node_creator = node_mdp.find(".//{*}creator", namespaces=namespaces)
    dc_creator = '' if node_creator is None else node_creator.text
    dc_creator = etl.escape_xml_text(dc_creator)
    #print("{}:Got creator={}".format(me,dc_creator))

    node_publisher = node_mdp.find(".//{*}dc/{*}publisher", namespaces=namespaces)
    publisher_text = '' if node_publisher is None else node_publisher.text
    publisher_text = etl.escape_xml_text(publisher_text)
    d_mets_template['publisher'] = publisher_text

    # For manioc, they encode the thumbnail in dc:relation
    node = node_mdp.find(".//{*}relation", namespaces=namespaces)
    node_text = '' if node is None else node.text

    # Skip over the beginning "vignette : " expected in this field
    if len(node_text) >= 10:
      node_text = node_text[11:]
    d_mets_template['sobekcm_thumbnail_src'] = node_text

    node_date = node_mdp.find(".//{*}date", namespaces=namespaces)
    dc_date_orig='1969-01-01'
    if node_date is not None:
          dc_date_orig = node_date.text
    # If we get only a year, (we have had some like this) pad it to year-01-01 to make
    # it valid for this field.
    if len(dc_date_orig) < 5:
          dc_date_orig += "-01-01"
    elif len(dc_date_orig) < 8:
          dc_date_orig += "-01"

    dc_date = '{}T12:00:00Z'.format(dc_date_orig)
    # print("Got dc date orig={}".format(dc_date_orig))
    # Must convert dc_date_orig to valid METS format:

    # Make an element tree style tree to invoke pattern to remove inner xml
    # str_description = etree.tostring(node_description,encoding='unicode',method='text').strip().replace('\n','')

    node_description = node_mdp.find(".//{*}description",namespaces=namespaces)
    str_description = ''
    if (node_description is not None):
          str_description = etl.escape_xml_text(node_description.text)

    if (1 == 1):
          dc_description = str_description
          # avoid charmap codec windows errors:print("Using dc_description='{}'".format(dc_description))

    # Manioc has only one dc:identifier used for related url, so now keep it in the template
    # incase the server response evolves, but for now just stick in a newline value for # the template
    xml_dc_ids = '\n'

    # For manioc, the first dc identifier is the related url of the item
    nodes = node_mdp.findall(
        ".//{*}identifier", namespaces=namespaces)

    related_url_text = '' if nodes is None or len(nodes) == 0 else nodes[0].text
    d_mets_template['related_url'] = related_url_text

    nodes = node_mdp.findall(".//{*}language",namespaces=namespaces)
    lang_code = 'eng' if nodes is None or len(nodes) < 1 else nodes[0].text.lower()
    iso639_2b_code = etl.d_language_639_2b[lang_code]
    d_mets_template['iso639_2b_code'] = iso639_2b_code

    iso639_2b_text = etl.d_langcode_langtext[iso639_2b_code]
    d_mets_template['iso639_2b_text'] = iso639_2b_text

    nodes_rights = node_mdp.findall(".//{*}rights",namespaces=namespaces)
    # Some concatenate rights with our rights text
    rights_text = d_mets_template['rights_text']
    for node_rights in nodes_rights:
          rights_text += '\n' + node_rights.text
    rights_text = etl.escape_xml_text(rights_text)
    d_mets_template['rights_text'] = rights_text

    # Subjects
    nodes_subject = node_mdp.findall(".//{*}subject", namespaces=namespaces)
    mods_subjects = '<mods:subject>'
    for node_subject in nodes_subject:
          subjects = node_subject.text.split(';')
          for subject in subjects:
            subject = subject.strip()
            if len(subject) < 1:
              continue
            mods_subjects += '<mods:topic>' + etl.escape_xml_text(subject) + '</mods:topic>\n'
    mods_subjects += ('</mods:subject>\n')

    tnode = node_mdp.find(".//{*}title", namespaces=namespaces)
    dc_title = '(none)' if tnode is None else etl.escape_xml_text(tnode.text)

    sobekcm_aggregations = d_mets_template['list_sobekcm_aggregations']
    xml_sobekcm_aggregations = ''
    for aggregation in sobekcm_aggregations:
          xml_sobekcm_aggregations += (
              '<sobekcm:Aggregation>{}</sobekcm:Aggregation>'
              .format(aggregation))
    sobekcm_wordmarks = d_mets_template['list_sobekcm_wordmarks']
    xml_sobekcm_wordmarks = ''
    for wordmark in sobekcm_wordmarks:
          xml_sobekcm_wordmarks += (
              '<sobekcm:Wordmark>{}</sobekcm:Wordmark>\n'
              .format(wordmark))

    # Set some template variable values
    d_mets_template['bib_vid'] = bib_vid
    d_mets_template['create_date'] = dc_date
    d_mets_template['last_mod_date'] = utc_secs_z
    d_mets_template['agent_creator_individual_name'] = dc_creator
    d_mets_template['header_identifier_text'] = header_identifier_text
    d_mets_template['mods_subjects'] = mods_subjects
    d_mets_template['mods_title'] = dc_title
    d_mets_template['xml_sobekcm_aggregations'] = xml_sobekcm_aggregations
    d_mets_template['xml_sobekcm_wordmarks'] = xml_sobekcm_wordmarks
    d_mets_template['xml_dc_ids'] = xml_dc_ids
    d_mets_template['description'] = dc_description
    d_mets_template['personal_creator_name'] = dc_creator
    d_mets_template['bibid'] = bibid
    d_mets_template['vid'] = vid
    d_mets_template['sha1_mets_v1'] = ''

    # Create mets_str and write it to mets.xml output file
    mets_str = manioc_mets_format_str.format(**d_mets_template)
    # Nest filename in folder of the bib_vid,
    # because loads in sobek bulder faster this way
    output_folder_mets_item = output_folder_mets  + bib_vid + '/'

    os.makedirs(output_folder_mets_item,exist_ok=True)
    filename_mets = output_folder_mets_item  + bib_vid + '.mets.xml'
    if verbosity > 0:
          print("{}:using output_filename_mets={}".format(me,filename_mets))

    fn = filename_mets
    with open(fn, mode='w', encoding='utf-8') as outfile:
          #print("{}:Writing METS filename='{}'".format(me,fn))
          #outfile.write(mets_str.encode('utf-8'))
          outfile.write(mets_str)
    return 1
#end def manioc_node_writer()

def harvest_manioc(study=None,set_spec=None,bib_vid=None,max_count=0):
  me = 'harvest_manioc'
  rparams=['study','set_spec','bib_vid']
  if not all(rparams):
      raise ValueError("missing some params from {}".format(rparams))

  # Set up output folder
  metadata_prefix = 'oai_dc'
  oai_url = 'http://www.manioc.org/phpoai/oai2.php'
  node_writer = manioc_node_writer

  encoding='ISO_8859_1' #works OK

  output_folder = etl.data_folder(linux='/home/robert/', windows='U:/',
      data_relative_folder='data/outputs/oai/{}/{}/'.format(study,set_spec))

  print("{}:STARTING: oai_url={},encoding='{}',output_folder={}"
         .format(me,oai_url,encoding,output_folder))

  harvester = OAI_Harvester(oai_url=oai_url, server_encoding=encoding
    , node_writer=node_writer, output_folder=output_folder, verbosity=1 )

  print("run_test: CREATED Harvester {} for oai_url={}, set_spec={}.\nHarvesting items now..."
        .format(repr(harvester),oai_url,set_spec))
  harvester.harvest_items(set_spec=set_spec,metadata_prefix=metadata_prefix
                          ,bib_vid=bib_vid,max_count=max_count)
  print("run_test: DONE!")

print("STARTING!")
max_count = 0
bib_vid= 'XX00000000_00001'
set_spec='patrimon'
harvest_manioc(study='manioc',set_spec=set_spec,bib_vid=bib_vid,max_count=max_count)
print("DONE!")
