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
import oai_server
import datetime

#Using this variable to keep d_mets_template definition a bit more readable
rights = "" # Rights statement from UF. Other rights statements in source will be appended to it.

mets_format_str = """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
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
<mods:languageTerm type="text">eng</mods:languageTerm>
<mods:languageTerm type="code" authority="iso639-2b">eng</mods:languageTerm>
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

<!-- subject topics: var mods_subjects may be phrases with no authority info -->
{mods_subjects}
<mods:note displayLabel="Harvest Date">{harvest_utc_secs_z}</mods:note>

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
        <sobekcm:statement code={physical_location_code}>{physical_location_name}</sobekcm:statement>
        </sobekcm:Source>
    </sobekcm:bibDesc>
</METS:xmlData>
</METS:mdWrap>
</METS:dmdSec>
<METS:structMap ID="STRUCT1" > <METS:div /> </METS:structMap>
</METS:mets>
"""
# end mets_format_str

class OAI_Harvester():

    def __init__(self, oai_url=None, bib_vid='XX00000000_00001', format_str=None
            ,output_folder=None,verbosity=0):

        rparams = ['oai_url', 'bib_vid','format_str','output_folder']
        if not all(rparams):
          raise ValueError("Missing some required params from {}".format(repr(rparams)))

        self.bib_vid = bib_vid
        self.oai_url = oai_url
        self.output_folder = output_folder
        self.format_str = format_str
        if verbosity > 0:
          print("OAI_Harvester: verbosity={}".format(verbosity))
        self.oai_server = oai_server.OAI_Server(oai_url=oai_url, verbosity=verbosity)
        return

    def harvest_items(self, set_spec=None, bib_vid=None, metadata_prefix='oai_dc', load_sets=1
          ,max_count=0,verbosity=0):
        rparams = ['set_spec','bib_vid','metadata_prefix']
        if not all(rparams):
          raise ValueError("Missing some required params from {}".format(repr(rparams)))
        bibint = int(bib_vid[2:10])
        d_records = self.oai_server.list_records(set_spec=set_spec ,metadata_prefix=metadata_prefix)
        if d_records is None:
          return
        count_records = 0
        for d_record in d_records :
            count_records += 1
            if max_count > 0 and count_records > max_count:
              break
            # TODO: add code here later to examine some node_record ID values and compare with
            # destination system (eg SobekCM resources) to decide to return an
            # extant bib_vid or a new one. For now just increment bibint part.
            bibint += 1
            bib_vid = bib_vid[0:2] + str(bibint).zfill(8) + '_00001'
            self.manioc_node_writer(bib_vid=bib_vid, d_record=d_record, metadata_prefix=metadata_prefix
                , mets_format_str=self.format_str)
        return

    '''
    The caller must avoid calling the node_writer for records that are error records or
    special records (like 'delete' records), which are not suitable for writing.
    The caller must also check whether the record is new or an update and caclulate and
    provide the bib_vid for the node_writer to use.
    '''
    def manioc_node_writer(self, bib_vid=None, d_record=None, metadata_prefix=None
            , mets_format_str=None, verbosity=0):
        me = 'manioc_node_writer'

        rparams = ['bib_vid', 'd_record', 'mets_format_str']
        if not all(rparams):
            raise ValueError("Missing some required params from {}".format(repr(rparams)))

        d_mets_template = {
            "content_source_name" : "Manioc",
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
            "bib_vid" : None,
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

        node_identifier = node_record.find("./{*}header/{*}identifier", namespaces=namespaces)
        header_identifier_text = '' if node_identifier is None else node_identifier.text

        header_identifier_normalized = (header_identifier_text
            .replace(':','_').replace('/','_').replace('.','-'))

        if verbosity > 0:
            print("using bib={}, vid={}, bib_vid={} to output item with "
                "manioc header_identifier_normalized={}"
                .format(bibid,vid,bib_vid, header_identifier_normalized))

        # Parse the input record and save it to a string
        record_str = etree.tostring(node_record, pretty_print=True, encoding='unicode')
        # print("{}:Got record string={}".format(me,record_str))

        output_folder_xml = self.output_folder + 'xml/'

        # TO CONSIDER: maybe add an argument flag to delete all preexisting
        # files in this directory? maybe dir for mets too?
        os.makedirs(output_folder_xml, exist_ok=True)
        if verbosity > 0:
              print("{}:using output_folder_xml={}".format(me,output_folder_xml))

        filename_xml = output_folder_xml + header_identifier_normalized + '.xml'
        with open(filename_xml, mode='w', encoding='utf-8') as outfile:
              if verbosity> 0:
                  print("{}:Writing filename_xml ='{}'".format(me, filename_xml))
              outfile.write(record_str)

          # Set some variables to potentially output into the METS template
        utc_now = datetime.datetime.utcnow()
        utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")

        node_mdf = node_record.find(".//{*}dc", namespaces=namespaces)

        if node_mdf is None:
              # This happens for received 'delete' records
              # Just return to ignore them pending requirements to process them
              # print ("Cannot find node_mdf for xml tag/node: {*}dc")
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

        node_description = node_mdf.find(".//{*}description",namespaces=namespaces)
        str_description = ''
        if (node_description is not None):
              str_description = etl.escape_xml_text(node_description.text)

        if (1 == 1):
              dc_description = str_description
              # avoid charmap codec windows errors:print("Using dc_description='{}'".format(dc_description))

        nodes_dc_identifier = node_mdf.findall(
            ".//{*}identifier", namespaces=namespaces)

        xml_dc_ids = '\n'
        related_url = ''

        # id type names based on data received in 2017
        # I invented the id_types, based on the data harvested in 2017.
        id_types = ['manioc_set_spec_index', 'manioc_url']
        for i,nid in enumerate(nodes_dc_identifier):
              xml_dc_ids = ('<mods:identifier type="{}">{}</mods:identifier>\n'
                .format(id_types[i], nid.text))
              if (i == 1):
                # per agreement on phone
                related_url = nid.text

        nodes_rights = node_mdf.findall(".//{*}rights",namespaces=namespaces)

        # Some concatenate rights with our rights text
        rights_text = d_mets_template['rights_text']
        for node_rights in nodes_rights:
              rights_text += '\n' + node_rights.text
        rights_text = etl.escape_xml_text(rights_text)
        d_mets_template['rights_text'] = rights_text

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
        v = d_mets_template['bib_vid']
        d_mets_template['bib_vid'] = bib_vid,
        v = d_mets_template['create_date']
        d_mets_template['create_date'] = dc_date
        v = d_mets_template['last_mod_date']
        d_mets_template['last_mod_date'] = utc_secs_z

        v = d_mets_template['agent_creator_individual_name']
        d_mets_template['agent_creator_individual_name'] = dc_creator

        d_mets_template['header_identifier_text'] = header_identifier_text

        v = d_mets_template['mods_subjects']
        d_mets_template['mods_subjects'] = mods_subjects

        v = d_mets_template['mods_title']
        d_mets_template['mods_title'] = dc_title

        v = d_mets_template['related_url']
        d_mets_template['related_url'] = related_url

        v = d_mets_template['xml_sobekcm_aggregations']
        d_mets_template['xml_sobekcm_aggregations'] = xml_sobekcm_aggregations

        v = d_mets_template['xml_sobekcm_wordmarks']
        d_mets_template['xml_sobekcm_wordmarks'] = xml_sobekcm_wordmarks

        v = d_mets_template['xml_dc_ids']
        d_mets_template['xml_dc_ids'] = xml_dc_ids

        v = d_mets_template['description']
        d_mets_template['description'] = dc_description

        v = d_mets_template['personal_creator_name']
        d_mets_template['personal_creator_name'] = dc_creator

        d_mets_template['bibid'] = bibid
        d_mets_template['vid'] = vid
        d_mets_template['sha1_mets_v1'] = ''
        d_mets_template['genre'] = genre

        # Create mets_str and write it to mets.xml output file
        mets_str = mets_format_str.format(**d_mets_template)
        # Nest filename in folder of the bib_vid,
        # because loads in sobek bulder faster this way
        output_folder_mets = self.output_folder + 'mets/' + bib_vid + '/'
        os.makedirs(output_folder_mets, exist_ok=True)

        filename_mets = output_folder_mets  + bib_vid + '.mets.xml'
        fn = filename_mets
        with open(fn, mode='w', encoding='utf-8') as outfile:
              #print("{}:Writing METS filename='{}'".format(me,fn))
              #outfile.write(mets_str.encode('utf-8'))
              outfile.write(mets_str)
        return 1
        #end def manioc_node_writer()
#end class OAI_Harvester

def run_test():

  # Set up output folder
  study = 'manioc'
  set_spec = 'patrimon'
  metadata_prefix = 'oai_dc'
  bib_vid = 'XX00000000_00001'
  oai_url = 'http://www.manioc.org/phpoai/oai2.php'

  output_folder = etl.data_folder(linux='/home/robert/', windows='U:/',
      data_relative_folder='data/outputs/oai/{}/{}/'.format(study,set_spec))

  print("STARTING: run_test: study={},oai_url={},output_folder={}".format(study,oai_url,output_folder))

  harvester = OAI_Harvester(oai_url=oai_url, bib_vid='XX00000000_00001', format_str=mets_format_str
    ,output_folder=output_folder,verbosity=1 )

  print("run_test: CREATED Harvester {}: Harvesting items now....".format(repr(harvester)))
  harvester.harvest_items(set_spec=set_spec,metadata_prefix=metadata_prefix,bib_vid=bib_vid,max_count=100)
  print("run_test: DONE!")

run_test()
