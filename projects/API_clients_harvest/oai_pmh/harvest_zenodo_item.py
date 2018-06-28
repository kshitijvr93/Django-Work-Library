'''
Program harvest_zenodo_item harvests a particular zenodo item and creates
a test mets file.

String mets_format_str is a python format string template to create a mets
file for ufdc.

It is used for making a METS file from values harvested from API for
zenodo oai_dc xml document.

NOTE: this code is based on Elsevier formatting that also used xslt, but use of
xslt did not add much needed functionality over using simply python 'format()'
functionality and generating some snippets of xml in python code.

This is initially used to translate 'zenodo' MD records from their OAI-PMH
feed to mets for UFDC SobekCM ingestion.
'''
#Get local pythonpath of modules from 'citrus' main project directory

import sys, os, os.path, platform
from lxml.etree import tostring
import xml.etree.ElementTree as ET

# Add the parent Path for misc UF modules

def register_modules():
    platform_name = platform.system().lower()
    if platform_name == 'linux':
        modules_root = '/home/robert/'
        #raise ValueError("MISSING: Enter code here to define modules_root")
    else:
        # assume rvp office pc running windows
        modules_root="C:\\rvp\\"
    sys.path.append(f'{modules_root}')
    sys.path.append(f'{modules_root}git/citrus/modules')
    return platform_name

platform_name=register_modules()
print("sys.path={}".format(repr(sys.path)))

# Import local modules
import etl
from etl import require_arg_names


folder_output_linux='/home/robert/data/'
folder_output_windows='U:/data/'

output_folder = etl.data_folder(linux=folder_output_linux,
    windows=folder_output_windows,
    data_relative_folder='data/outputs/zenodo_mets')

print(f"Using output_folder='{output_folder}'",file=sys.stdout)

mets_format_str = '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
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
  <METS:name>Marshal API Zenodo Harvester 0.2</METS:name>
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

{xml_sobekcm_creators}

<!-- subject topics- These from Elsevier are phrases with no authority info -->
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

from lxml import etree
import datetime
import requests
# provided by a ufdc patron to infer
# that string '1293007' in the original url is a zenodo identifier

'''
xxrequest_uf1=('https://zenodo.org/oai2d?verb=ListRecords'
    '&set=user-genetics-datasets&metadataPrefix=oai_dc')

xrequest_uf1=("https://zenodo.org/oai2d?verb=GetRecord"
  "&identifier=oai:zenodo.org:{}&metadataPrefix=oai_dc"
  .format(zenodo_ids[0]))

msg = ("Using request = {}".format(request_uf1))
'''

'''
d_oai_zenodo['GetRecord'] is special configuration info
to do API calls to zenodo GetRecord API.

'''
d_oai_zenodo = {
    'request_headers': {
            'Accept' : 'application/xml',
     },
    'base_url' : 'https://zenodo.org/oai2d?',
    'metadata_prefixes' : ['oai_dc'],
    'verbs' : { #Using the official OAI-PMH verb names
        'GetRecord': {
            'format_identifier' : (
              '&identifier=oai:zenodo.org:{}')
        },
        'ListRecords': {
            'format_setname' : ('verb=ListRecord&set={}')
        }
    },
}

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

def url_of_zenodo(d_request, dataset_name='user-genetics-datasets', verbosity=0):
    me = "url_of_zenodo"
    if d_request is None:
        raise(ValueError,"d_request is required")
    if verbosity != 0 :
        print(f"{me}:Starting")

    url = d_request['url_format'].format(dataset_name)
    d_request['url'] = url # save for diagnostics
    add_curl_command(d_request)

    return url

def response_of_zenodo(d_request, dataset_name=None, verbosity= 0):
    d_headers = d_request['d_request_headers']
    #todo - pull next line back into url_of_zenodo?
    url = url_of_zenodo(d_request, dataset_name=dataset_name,
        verbosity=verbosity)
    return requests.get(url, headers=d_headers)

def xrequire_arg_names(d_caller_locals, names):
    required_args = [ v for k, v in d_caller_locals.items() if k in names]
    if not all(required_args):
          raise ValueError(
             f"Error: Some required variables in {names!r} not set.")


class OAI_Harvester(object):

    def __init__(self, d_oai=None,  output_folder=None, verbosity=None):

      require_arg_names(locals(), ['d_oai', 'output_folder'])

      # All URL requests we send to the OAI-PMH server start with base_url part
      self.d_oai = d_oai
      self.base_url = d_oai['base_url']
      self.output_folder = output_folder

      self.response_type = None
      # Later: can use API with verb metadataFormats to get them.
      # Now use the first listed metadata_prefix
      #
      self.metadata_prefixes = d_oai['metadata_prefixes']
      self.preferred_metadata_prefix = d_oai['metadata_prefixes'][0]

      self.verbosity = verbosity # default verbosity

      self.basic_verbs = [
         # see http://www.oaforum.org/tutorial/english/page4.htm
         'GetRecord', 'Identify',
         'ListIdentifiers', 'ListMetaDataFormats', 'ListRecords' , 'ListSets'
      ]

# end def

    def url_list_records(self, set_spec=None, metadata_prefix=None):
        url = (f"{self.base_url}?ListRecords&set={set_spec}"
            "&metadataPrefix={metadata_prefix}")
        return request.get(url)

    '''
    method get_record():

    For consistency with some other methods, return nodes_record[] list of records
    nodes, but from this method, that value it will always have length of 1

    sample request url to get a single record from zenodo:
    https://zenodo.org/oai2d?verb=GetRecord&identifier=oai:zenodo.org:164231&metadataPrefix=oai_dc

    This generates and sends the request url, saves the resulting xml
    in self.xml, parses it and saves self.node_root and self.nodes_record
    and self.namespaces for the xml document for further processing.
    For example node_record_process() is designed to do further processing.


    '''
    def get_record(self, identifier=None, metadata_prefix=None):

        self.response_type = 'get_record'
        prefixes = self.d_oai['metadata_prefixes']
        if metadata_prefix is None:
            metadata_prefix = prefixes[0]
        elif metadata_prefix not in prefixes:
            raise ValueError(
              f"Given metadata_prefix {metadata_prefix} is not in {prefixes}")

        base_url = self.d_oai['base_url']
        format_id = self.d_oai['verbs']['GetRecord']['format_identifier']
        identifier_part = format_id.format(identifier)

        url = ( f"{base_url}verb=GetRecord{identifier_part}"
                f"&metadataPrefix={metadata_prefix}")

        if self.verbosity > 0:
            print(f"metadata_prefix='{metadata_prefix}'")
            msg = f"get_record: using url='{url}'"
            print(msg)
            sys.stdout.flush()

        self.response_type = 'get_record' #python style naming
        self.request_url = url
        self.response = requests.get(url)
        self.response_xml = self.response.text.encode('utf-8')
        self.node_root = etree.fromstring(self.response_xml)

        self.namespaces={key:value for key,value in
           dict(self.node_root.nsmap).items() if key is not None}

        # str_pretty = etree.tostring(node_root, pretty_print=True)
        self.nodes_record = self.node_root.findall(".//{*}record",
              namespaces=self.namespaces)

        # Exactly one node_record should exist, since we check response_type,
        # it may be overkill to recheck here... but maybe add later if issues.
        self.node_record = self.nodes_record[0]
        return self.nodes_record
    # end def get_record in OAI_Harvester

    '''
    NOTE: This is highly-zenodo-output specific, may be worth teasing out
    common parts to a base class later, but maybe not after looking at a few
    different formats produced from OAI-PMH Servers.

    This is called after th get_record() method to optionally write out saved
    xml for a zenodo item, and to always output a ufdc mets file with the
    zenodo data encoded into it.
    The mets.xml file is designed to be ingested by the sobekcm builder.
    '''
    def node_record_process(self,node_record=None, namespaces=None,
        bibid_str='DS12345678', # format 'XY12345678'
        vid_str='12345',  # format '12345'
        save_xml=False):

        # Caller with node_root can provide overrides for node_record or
        # and namespaces. Eg, before calling, caller can set namespaces  like:
        # namespaces={key:value for key,value in dict(node_root.nsmap).items()
        # if key is not None}
        me = 'node_record_process'

        if self.verbosity > 0:
            print(f"{me}: Using save_xml={save_xml}")

        if node_record is None:
           node_record = self.node_record
        if namespaces is None:
           namespaces = self.namespaces

        #bibid = bib_prefix + str(bibint).zfill(8)
        bib_vid = f"{bibid_str}_{vid_str}"

        node_type= node_record.find(".//{}type", namespaces=namespaces)
        genre = '' if not node_type else node_type.text

        # NOTE: this also appers to be the OAI Server record identifier
        header_identifier = node_record.find("./{*}header/{*}identifier").text

        identifier_normalized = header_identifier.replace(':','_') + '.xml'
        if self.verbosity > 0:
            print(f"using bib_vid={bib_vid} to output item with zenodo "
              "identifier_normalized={identifier_normalized}")

        if save_xml == True:
            # Parse the input record and save it to a string
            record_str = etree.tostring(node_record, pretty_print=True,
                xml_declaration=True, encoding='utf-8')

            save_folder = self.output_folder + '/recieved/'
            os.makedirs(save_folder, exist_ok=True)
            save_file = ( save_folder + identifier_normalized )

            with open(save_file, 'wb') as outfile:
                if self.verbosity > 0:
                    print(f"Writing save_file ='{save_file}'")
                outfile.write(record_str)

        # Set some variables to potentially output into the Zenodo METS
        # output template

        utc_now = datetime.datetime.utcnow()
        utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")

        #Get basic values from input doc
        node_oaidc = node_record.find(".//{*}dc", namespaces=namespaces)

        if node_oaidc is None:
            raise Exception("Cannot find oai_dc:dc node")

        namespaces_oaidc = {key:value for key,value in
            dict(node_oaidc.nsmap).items() if key is not None}

        if self.verbosity > 0:
            print(f"Got oai_dc prefix map='{namespaces_oaidc}'\n\n")

        node_creator = node_oaidc.find(".//dc:creator",
            namespaces=namespaces_oaidc)

        dc_creator = '' if node_creator is None else node_creator.text

        nodes_creator = node_oaidc.findall(
            ".//dc:creator", namespaces=namespaces_oaidc)

        # Handle multiple creators
        dc_creators = []
        for node_creator in nodes_creator:
            dc_creators.append(node_creator.text)


        if self.verbosity > 0:
            print(f"Got creators='{dc_creators}'")
            sys.stdout.flush()

        xml_sobekcm_creators = ''
        for creator in dc_creators:
            xml_sobekcm_creators += (
                f'''
<mods:name type="personal">
  <mods:namePart>{creator}</mods:namePart>
  <mods:role>
    <mods:roleTerm type="text">creator</mods:roleTerm>
  </mods:role>
</mods:name>
                ''')

        dc_date_orig = node_oaidc.find("./dc:date",
            namespaces=namespaces_oaidc).text
        if self.verbosity > 0:
            print("Got dc date orig={}".format(dc_date_orig))
        # Must convert dc_date_orig to valid METS format:
        dc_date = '{}T12:00:00Z'.format(dc_date_orig)
        if self.verbosity > 0:
            print("Got dc_date='{}'".format(dc_date))

        node_description = node_oaidc.find(".//{*}description",
            namespaces=namespaces_oaidc)

        # Make an element tree style tree to invoke pattern to remove innter xml
        # If strip newlines, text with newlines runs together so replace a space
        str_description = (tostring(node_description,encoding='unicode',
            method='text').strip().replace('\n',' '))
        # Special doctype needed to handle nbsp... copyright
        xml_dtd = '''<?xml version="1.1" encoding="UTF-8" ?><!DOCTYPE naughtyxml [
            <!ENTITY nbsp "&#0160;">
            <!ENTITY copy "&#0169;">
            ]>'''
        xml_description =  '{}<doc>{}</doc>'.format(xml_dtd,str_description)
        if self.verbosity > 0:
            print("Got str_description='{}'".format(str_description))
        if self.verbosity > 0:
            print("Got xml_description='{}'".format(xml_description))

        # See: https://stackoverflow.com/questions/19369901/python-element-tree-extract-text-from-element-stripping-tags#19370075
        tree_description = ET.fromstring(xml_description)
        dc_description = etl.escape_xml_text(''.join(tree_description.itertext()))
        #dc_description = xml_description
        if self.verbosity > 0:
            print("Using dc_description='{}'".format(dc_description))

        nodes_identifier = node_oaidc.findall(".//{*}identifier",
            namespaces=namespaces_oaidc)
        #inferred the following indexes by pure manual inspection!
        doi = nodes_identifier[0].text
        zenodo_id = nodes_identifier[2].text
        related_url = '{}'.format(doi)

        #relation_doi = node_oaidc.find(".//{*}relation").text
        nodes_rights = node_oaidc.findall(".//{*}rights",
            namespaces=namespaces_oaidc)
        rights_text = 'See:'
        for node_rights in nodes_rights:
            rights_text += ' ' + node_rights.text

        nodes_subject = node_oaidc.findall(".//{*}subject",
            namespaces=namespaces_oaidc)
        mods_subjects = ''
        for node_subject in nodes_subject:
            mods_subjects += ('<mods:subject><mods:topic>' + node_subject.text
              + '</mods:topic></mods:subject>\n')

        dc_title = node_oaidc.find(".//{*}title").text
        dc_type = node_oaidc.find(".//{*}type").text

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
            'identifier' : header_identifier,
            'mods_subjects' : mods_subjects,
            'rights_text' : rights_text,
            'utc_secs_z' :  utc_secs_z,
            'title' : dc_title,
            'related_url' : related_url,
            'xml_sobekcm_aggregations' : xml_sobekcm_aggregations,
            'doi': doi,
            'description' : dc_description,
            'xml_sobekcm_creators' : xml_sobekcm_creators,
            'bibid': bibid_str,
            'vid': vid_str,
            'type_of_resource' : dc_type,
            'sha1-mets-v1' : '',
            'genre' : 'dataset',
            'genre_authority': 'zenodo',
        }

        # Create mets_str and write it
        mets_str = mets_format_str.format(**d_var_val)

        mets_output_folder = self.output_folder + '/mets_output/'
        item_output_folder = mets_output_folder + '/' + bib_vid
        os.makedirs(item_output_folder, exist_ok=True)
        filename_mets = item_output_folder + '/' + bib_vid + '.mets.xml'

        if self.verbosity > 0:
            print("WRITING METS.XML to {}".format(filename_mets))

        fn = filename_mets
        with open(fn, 'wb') as outfile:
            print("Writing filename='{}'".format(fn))
            outfile.write(mets_str.encode('utf-8'))
        # end with ... outfile

    # end def node_record_process


    def xxgenerator_list_records(self,  metadata_prefix=None, set_spec=None, verbosity=0):
	    pnames = ['metadata_prefix','set_spec',]

	    if not all(set_spec):
	      raise ValueError("Error: Some parameters not set: {}.".format(pnames))

	    if metadata_prefix not in self.metadata_prefixes:
	      raise ValueError("Error: unknown metadata format: {}.".format(metadata_prefix))

	    n_batch = 0;
	    url_list = url_list_records(set_spec=set_spec,metadata_prefix=metadata_prefix)
	    while (url_list is not None):
	      n_batch += 1
	      response = request.get(url_list)
	      xml = response.text.encode('utf-8')

	      try:
	          node_root = etree.fromstring(xml)
	      except Exception as e:
	          print("For batch {}, made url request ='{}'. Skipping batch with Parse() exception='{}'"
	                .format(n_batch, url_list_records, repr(e)))

	          print("Traceback: {}".format(traceback.format_exc()))
	          # Break here - no point to continue because we cannot parse/discover the resumptionToken
	          break
	      # str_pretty = etree.tostring(node_root, pretty_print=True)
	      d_namespaces = {key:value for key,value in dict(node_root.nsmap).items() if key is not None}
	      nodes_record = node_root.findall(".//{*}record", namespaces=d_namespaces)

	      print ("ListRecords request found root tag name='{}', and {} records"
	             .format(node_root.tag, len(nodes_record)))

	      # For every record, write an output file.
	      for node_record in nodes_record:
	          yield node_record

	      node_resumption = node_root.find('.//{*}resumptionToken', namespaces=d_namespaces)
	      url_list = None
	      if node_resumption is not None:
	          # Note: manioc allows no other args than resumption token, so try with all oai servers
	          #url_list = ('{}?verb=ListRecords&set={}&metadataPrefix=oai_dc&resumptionToken={}'
	          #    .format(self.url_base, set_spec, node_resumption.text))
	          url_list = ('{}?verb=ListRecords&resumptionToken={}'
	              .format(self.url_base,  node_resumption.text))
	      if verbosity > 0:
	          print("{}:Next url='{}'".format(me,url_list))
	    # end while url_list is not None
	    return None
	# end def generator_list_records()

# end class OAI_Harvester

#
#{ Method list_records_to_mets_xml_files
# Query the zenodo api for all records in the given set_spec.
# Under the output folder, create subdir mets_output and under it
# a new mets file for each record received from the zenodo api
def xxlist_records_to_mets_xml_files(d_run_params,
    set_spec='user-genetics-datasets',verbosity=1):
    #
    if verbosity > 0:
        msg = ("{}: getting zenodo records for set_spec='{}'"
            .format(me, set_spec))

    output_folder = d_run_params['output_folder']
    mets_output_folder = output_folder + '/mets_output/'

    os.makedirs(mets_output_folder, exist_ok=True)
    d_request = d_run_params['d_request_zenodo']

    response = response_of_zenodo(d_request, dataset_name=set_spec)

    # Construct a curl command that repesents the sent request, just to
    # provide printed output of this auxiliary info
    curl = d_request['curl']

    # Show the API response and the auxiliary info for a similar curl command
    print("Got response for url={}, curl={}"
        .format(d_request['url'], d_request['curl']))

    # Process the response
    xml = response.text.encode('utf-8')
    print("Response text len={}".format(len(xml)))

    node_root = etree.fromstring(response.text.encode('utf-8'))
    #str_pretty = etree.tostring(node_root, pretty_print=True)
    d_namespaces = {key:value for key,value in dict(node_root.nsmap).items()
        if key is not None}

    nodes_record = node_root.findall(".//{*}record", namespaces=d_namespaces)

    print ("ListRecords request found root tag name='{}', and {} records"
        .format(node_root.tag, len(nodes_record)))
    #print("found str_pretty='{}'".format(str_pretty))
    #testing
    bib_prefix = "DS"
    vid = "00001"

    # One must now manually find the highest bibint in the DS mets files
    # and add 1
    # 20180626 the highest was 9, and 1 is added in the loop below
    start_bibint = bibint = 9
    os.makedirs(output_folder + '/received/', exist_ok=True)

    #  Examine each output record from the OAI command
    for node_record in nodes_record:
        # identifier
        bibint += 1
        bibid = bib_prefix + str(bibint).zfill(8)
        bib_vid = "{}_{}".format(bibid,vid)



        # Set some variable to potentially output into the METS template
        utc_now = datetime.datetime.utcnow()
        utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")

        #Get basic values from input doc

        node_oaidc = node_record.find(".//{*}dc", namespaces=d_namespaces)
        if node_oaidc is None:
            raise Exception("Cannot find oai_dc:dc node")

        namespaces = {key:value for key,value in dict(node_oaidc.nsmap).items()
            if key is not None}

        print("Got oai_dc prefix map='{}'\n\n".format(repr(namespaces)))

        node_creator = node_oaidc.find(".//dc:creator", namespaces=namespaces)
        dc_creator = '' if node_creator is None else node_creator.text

        print("Got creator={}".format(dc_creator))

        dc_date_orig = node_oaidc.find("./dc:date", namespaces=namespaces).text
        print("Got dc date orig={}".format(dc_date_orig))
        # Must convert dc_date_orig to valid METS format:
        dc_date = '{}T12:00:00Z'.format(dc_date_orig)
        print("Got dc_date='{}'".format(dc_date))

        node_description = node_oaidc.find(".//{*}description",namespaces=namespaces)
        # Make an element trree style tree to invoke pattern to remove innter xml
        str_description = tostring(node_description,encoding='unicode',method='text').strip().replace('\n','')
        # Special doctype needed to handle nbsp... copyright
        xml_dtd = '''<?xml version="1.1" encoding="UTF-8" ?><!DOCTYPE naughtyxml [
            <!ENTITY nbsp "&#0160;">
            <!ENTITY copy "&#0169;">
            ]>'''
        xml_description =  '{}<doc>{}</doc>'.format(xml_dtd,str_description)
        print("Got str_description='{}'".format(str_description))
        print("Got xml_description='{}'".format(xml_description))

        # See: https://stackoverflow.com/questions/19369901/python-element-tree-extract-text-from-element-stripping-tags#19370075
        tree_description = ET.fromstring(xml_description)
        dc_description = etl.escape_xml_text(''.join(tree_description.itertext()))
        #dc_description = xml_description
        print("Using dc_description='{}'".format(dc_description))

        nodes_identifier = node_oaidc.findall(".//{*}identifier")
        #inferred the following indexes by pure manual inspection!
        doi = nodes_identifier[0].text
        zenodo_id = nodes_identifier[2].text
        related_url = '{}'.format(doi)

        #relation_doi = node_oaidc.find(".//{*}relation").text
        nodes_rights = node_oaidc.findall(".//{*}rights")
        rights_text = 'See:'
        for node_rights in nodes_rights:
            rights_text += ' ' + node_rights.text

        nodes_subject = node_oaidc.findall(".//{*}subject")
        mods_subjects = ''
        for node_subject in nodes_subject:
            mods_subjects += ('<mods:subject><mods:topic>' + node_subject.text
              + '</mods:topic></mods:subject>\n')

        dc_title = node_oaidc.find(".//{*}title").text
        dc_type = node_oaidc.find(".//{*}type").text

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
            'identifier' : header_identifier,
            'mods_subjects' : mods_subjects,
            'rights_text' : rights_text,
            'utc_secs_z' :  utc_secs_z,
            'title' : dc_title,
            'related_url' : related_url,
            'xml_sobekcm_aggregations' : xml_sobekcm_aggregations,
            'doi': doi,
            'description' : dc_description,
            'creator' : dc_creator,
            'bibid': bibid,
            'vid': vid,
            'type_of_resource' : dc_type,
            'sha1-mets-v1' : '',
            'genre' : 'dataset',
            'genre_authority': 'zenodo',
        }

        # Create mets_str and write it
        mets_str = mets_format_str.format(**d_var_val)

        item_output_folder = mets_output_folder + '/' + bib_vid
        os.makedirs(item_output_folder, exist_ok=True)
        filename_mets = item_output_folder + '/' + bib_vid + '.mets.xml'
        fn = filename_mets
        with open(fn, 'wb') as outfile:
            print("Writing filename='{}'".format(fn))
            outfile.write(mets_str.encode('utf-8'))
        # end with ... outfile
    # end for node_record in nodes_record
# } end def list_records_to_xml_files

d_run_params = {
    'output_folder' : 'c:/rvp/elsevier/output_zenodo/' ,
    'd_request_zenodo' : {
        'd_request_headers': {
            'Accept' : 'application/xml',
        },
        'start_item_count': 0,
        'result_item_quantity_max': 200, # Max per ORCID docs is 200 ao 20170503
        # See ORCID docs on the solr_query_string options, field and variable names.
        # This is part of a GET URL, so use the %22 and + and any other applicable url-encodings
        'solr_query_string': 'affiliation-org-name:%22University+of+Florida%22',
        'url_format': 'https://zenodo.org/oai2d?verb=ListRecords&set={}&metadataPrefix=oai_dc',
        'url': '', #Do not edit - just a placeholder, a method will compute this
    }
}

def run(verbosity=0):
    output_folder = etl.data_folder(linux='/home/robert/', windows='U:/',
        data_relative_folder='data/outputs/zenodo_mets')
    if verbosity > 0:
        print("Using output_folder='{}'".format(output_folder))

    harvest = OAI_Harvester(d_oai=d_oai_zenodo, output_folder=output_folder,
        verbosity=verbosity)

    result = harvest.get_record(identifier='1293007')
    harvest.node_record_process(bibid_str='DS00000010', vid_str='00001',
        save_xml=True)

    return "run:Done"

#test run

msg = run(verbosity=1)
print(msg)
sys.stdout.flush()
