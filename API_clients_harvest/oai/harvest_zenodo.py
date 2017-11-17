'''
Program harvest_zenodo harvests a particular zenodo collection and creates
some test mets file.

String mets_format_str is a python format string template to create a mets
file for ufdc.

It is used for making a METS file from values harvested from API for
zenodo oai_dc xml document.

NOTE: this code is based on Elsevier formatting that also used xslt, but use of
xslt did not add much functionality over using simply python 'format()'
functionality and generating some snippets of xml in python code.

This is initially used to translate 'zenodo' MD records from their OAI-PMH
feed to mets for UFDC SobekCM ingestion.
'''
#Get local pythonpath of modules from 'citrus' main project directory

import sys, os, os.path, platform

# Add the parent Path for misc UF modules
sys.path.append('{}/git/citrus/modules'.format(os.path.expanduser('~')))
print("sys.path={}".format(repr(sys.path)))

import etl
from lxml.etree import tostring
import xml.etree.ElementTree as ET

'''home_directory = os.path.expanduser('~')
print("Using home_directory='{}'".format(home_directory),file=sys.stdout)
sys.stdout.flush()

local_module_folder = '{}/github/citrus/modules'.format(home_directory)
print("Using local local module folder='{}'".format(local_module_folder))
sys.path.append(local_module_folder) #my current place on UF pc
'''

folder_output_linux='/home/robert/'
folder_output_windows='U:/'

output_folder = etl.data_folder(linux=folder_output_linux, windows=folder_output_windows,
    data_relative_folder='data/outputs/zenodo_mets')

print("Using output_folder='{}'".format(output_folder),file=sys.stdout)

import etl
import os
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
<mods:name type="personal">
  <mods:namePart>{creator}</mods:namePart>
  <mods:role>
    <mods:roleTerm type="text">creator</mods:roleTerm>
  </mods:role>
</mods:name>

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

request_uf1='https://zenodo.org/oai2d?verb=ListRecords&set=user-genetics-datasets&metadataPrefix=oai_dc'

'''
d_oai_zenodo is configuration info to do API calls to zenodo
The most likely value to be changed by a caller is ['pub_search']['url'],
which is the url to get the oai list of records for a named set of items.

'''
d_oai_zenodo = {
    'pub_search': { # This entry has data used to do a zenodo ListRecords query for a specific dataset
        'd_request_headers': {
            'Accept' : 'application/xml',
        },
        'url_base': 'https://zenodo.org/oai2d?verb=ListRecords&set=user-genetics-datasets&metadataPrefix=oai_dc',
        'start_item_count': 0,
        'result_item_quantity_max': 200, # Max per ORCID docs is 200 ao 20170503
        # See ORCID docs on the solr_query_string options, field and variable names.
        # This is part of a GET URL, so use the %22 and + and any other applicable url-encodings
        'solr_query_string': 'affiliation-org-name:%22University+of+Florida%22',
        'url_format': 'https://pub.orcid.org/v2.0/{}/record',

        'url': '', #Do not edit - just a placeholder, a method will compute this
    },
    'pub_record': {
        'd_request_headers': {
            'Authorization' : 'Bearer c32ea2ba-0efc-45db-b771-eb793879b232',
            'Accept' : 'application/vnd.orcid+xml',
        },
        'url_format': 'https://pub.orcid.org/v2.0/{}/record',
        # Consider:'d_format': {'orcid_id':'',} #User fills in d_format values for str.format_map()
        'url': '', #Do not edit - just a placeholder, a method will compute this
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

def url_of_zenodo(d_search, dataset_name='user-genetics-datasets', verbosity=0):
    me = "url_of_zenodo"
    if d_search is None:
        raise(ValueError,"d_search is required")
    if verbosity != 0 :
        print("{}:Starting".format(me))

    url = d_search['url_format'].format(dataset_name)
    d_search['url'] = url # save for diagnostics
    add_curl_command(d_search)
    return url

def response_of_zenodo(d_search, dataset_name=None, verbosity= 0):
    d_headers = d_search['d_request_headers']
    url = url_of_zenodo(d_search, dataset_name=dataset_name, verbosity=verbosity)
    return requests.get(url, headers=d_headers)

class OAI_Harvester(object):
  def __init__(self, oai_url=None, output_folder=None,verbosity=None):
    pnames = ['oai_url','output_folder',]
    if not all(output_folder, oai_url):
      raise ValueError("Error: Some parameters not set: {}.".format(pnames))
    self.oai_url = oai_url
    self.output_folder = output_folder
    # Later: use API with verb metadataFormats to get them. Now try a one-size-fits-all list
    #
    self.metadata_formats=['oai_dc']
    self.verbosity = verbosity # default verbosity
    self.basic_verbs = [ # see http://www.oaforum.org/tutorial/english/page4.htm
         'GetRecord', 'Identify'
         , 'ListIdentifiers', 'ListMetaDataFormats', 'ListRecords' , 'ListSets'
    ]

    pass

  def url_list_records(self, set_spec=None, metadata_format=None):
    url = ("{}?ListRecords&set={}&metadataPrefix={}"
      .format(self.oai_url,set_spec,metadata_format))
    return request.get(url)

  def generator_list_records(self,  metadata_format=None, set_spec=None, verbosity=0):
    pnames = ['metadata_format','set_spec',]

    if not all(set_spec):
      raise ValueError("Error: Some parameters not set: {}.".format(pnames))

    if metadata_format not in self.metadata_formats:
      raise ValueError("Error: unknown metadata format: {}.".format(metadata_format))

    n_batch = 0;
    url_list = url_list_records(set_spec=set_spec,metadata_format=metadata_format)
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
#  Method list_records_to_mets_xml_files
def list_records_to_mets_xml_files(d_run_params, set_spec='user-genetics-datasets',verbosity=0):
    #
    output_folder = d_run_params['output_folder']
    mets_output_folder = output_folder + '/mets_output/'
    os.makedirs(mets_output_folder, exist_ok=True)

    d_request = d_run_params['d_request_zenodo']

    response = response_of_zenodo(d_request, dataset_name=set_spec)

    # Construct a curl command that repesents the sent request, just to provide printed
    # output of this auxiliary info
    curl = d_request['curl']

    # Show the API response and the auxiliary info for a similar curl command
    print("Got response for url={}, curl={}".format(d_request['url'], d_request['curl']))

    # Process the response
    xml = response.text.encode('utf-8')
    print("Response text len={}".format(len(xml)))

    node_root = etree.fromstring(response.text.encode('utf-8'))
    #str_pretty = etree.tostring(node_root, pretty_print=True)
    d_namespaces = {key:value for key,value in dict(node_root.nsmap).items() if key is not None}

    nodes_record = node_root.findall(".//{*}record", namespaces=d_namespaces)

    print ("ListRecords request found root tag name='{}', and {} records".format(node_root.tag, len(nodes_record)))
    #print("found str_pretty='{}'".format(str_pretty))
    #testing
    bib_prefix = "DS"
    vid = "00001"
    start_bibint = bibint = 0
    os.makedirs(output_folder + '/received/', exist_ok=True)

    #  Examine each output record from the OAI command
    for node_record in nodes_record:
        # identifier
        bibint += 1
        bibid = bib_prefix + str(bibint).zfill(8)
        bib_vid = "{}_{}".format(bibid,vid)

        node_type= node_record.find(".//{}type", namespaces=d_namespaces)
        genre = '' if not node_type else node_type.text

        header_identifier = node_record.find("./{*}header/{*}identifier").text

        identifier_normalized = header_identifier.replace(':','_') + '.xml'
        print("using bib_vid={} to output item with zenodo identifier_normalized={}"
              .format(bib_vid, identifier_normalized))
        #zenodo_string_xml = etree.tostring(node_record, pretty_print=True)

        # Parse the input record and save it to a string
        record_str = etree.tostring(node_record, pretty_print=True, xml_declaration=True)

        filename_received = output_folder + '/received/' + identifier_normalized

        fn = filename_received
        with open(fn, 'wb') as outfile:
            print("Writing filename_received ='{}'".format(fn))
            outfile.write(record_str)

        # Set some variable to potentially output into the METS template
        utc_now = datetime.datetime.utcnow()
        utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")

        #Get basic values from input doc

        node_oaidc = node_record.find(".//{*}dc", namespaces=d_namespaces)
        if node_oaidc is None:
            raise Exception("Cannot find oai_dc:dc node")

        namespaces = {key:value for key,value in dict(node_oaidc.nsmap).items() if key is not None}

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

output_folder = etl.data_folder(linux='/home/robert/', windows='U:/',
        data_relative_folder='data/outputs/zenodo_mets')

d_run_params['output_folder'] = output_folder
set_spec='user-genetics-datasets'

list_records_to_mets_xml_files(d_run_params, set_spec=set_spec)