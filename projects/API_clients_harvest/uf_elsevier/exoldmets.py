# EXOLDMETS- Elsevier Xml Orig-Load-Date to Mets
# tranform Elsevier Xml files created by ealdxml (Elsevier API (Orig) Load Date to XML),
# to METS files
#Get local pythonpath of modules from 'citrus' main project directory
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
print("Using sys.path={}".format(repr(sys.path)))
import etl
from uf_elsevier.utilities import uf_elsevier_item_authors

from sqlalchemy import (
  Boolean, create_engine,
  CheckConstraint, Column, Date, DateTime,
  Float, FLOAT, ForeignKeyConstraint,
  Integer,
  MetaData, Sequence, String,
  Table, Text, UniqueConstraint,
  )
from sqlalchemy.inspection import inspect as inspect
from sqlalchemy.schema import CreateTable
from sqlalchemy.sql import select, and_, or_, not_
import sqlalchemy.sql.sqltypes

# Import slate of databases that this user can use
from sqlalchemy_tools.podengo_db_engine_by_name import get_db_engine_by_name

# First we have some xslt strings used to transform Elsevier documents for submission
# to SobekCM Builder as mets files.
if 1 == 1:
    d_xslt = {}
    ###########################    ENTRY ###################################
    d_xslt['entry'] = '''<?xml version="1.0" ?>
    <xsl:stylesheet version="1.0"
    xmlns="http://www.w3.org/2005/Atom"
    xmlns:sa="http://www.elsevier.com/xml/common/struct-aff/dtd"
    xmlns:ns1="http://webservices.elsevier.com/schemas/search/fast/types/v4"
    xmlns:atom="http://www.w3.org/2005/Atom"
    xmlns:prism="http://prismstandard.org/namespaces/basic/2.0/"
    xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/"
    xmlns:dc="http://purl.org/dc/elements/1.1/"

    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:doc="http://www.elsevier.com/xml/document/schema"
    xmlns:dp="http://www.elsevier.com/xml/common/doc-properties/schema"
    xmlns:cp="http://www.elsevier.com/xml/common/consyn-properties/schema"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:dct="http://purl.org/dc/terms/"
    xmlns:oa="http://vtw.elsevier.com/data/ns/properties/OpenAccess-1/"
    xmlns:cja="http://www.elsevier.com/xml/cja/schema"
    xmlns:ja="http://www.elsevier.com/xml/ja/schema"
    xmlns:bk="http://www.elsevier.com/xml/bk/schema"
    xmlns:ce="http://www.elsevier.com/xml/common/schema"
    xmlns:mml="http://www.w3.org/1998/Math/MathML"
    xmlns:cals="http://www.elsevier.com/xml/common/cals/schema"
    xmlns:tb="http://www.elsevier.com/xml/common/table/schema"
    xmlns:sb="http://www.elsevier.com/xml/common/struct-bib/schema"
    xmlns:xlink="http://www.w3.org/1999/xlink">

<xsl:output encoding="UTF-8" method="xml" omit-xml-declaration="no" indent="yes"/>
<xsl:template match="comment()" priority="5"/>
<xsl:template match="/">
<xsl:comment> XSL-inserted comment ( article ) </xsl:comment>
<METS:mets OBJID="{objid}"
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
<METS:metsHdr CREATEDATE="{{{{create_date}}}}\" ID="{objid}"
  LASTMODDATE="{{{{last_mod_date}}}}" RECORDSTATUS="COMPLETE">
<METS:agent ROLE="CREATOR" TYPE="ORGANIZATION">
 <METS:name>{agent_creator_organization_name}:</METS:name>
</METS:agent>
<METS:agent ROLE="CREATOR" OTHERTYPE="SOFTWARE" TYPE="OTHER">
  <METS:name>{agent_creator_software_name}</METS:name>
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

<mods:abstract lang="en" >
  <xsl:attribute name="displayLabel">Abstract</xsl:attribute>
  <xsl:value-of select="//prism:teaser"/>
</mods:abstract>

<mods:accessCondition>{access_condition}<xsl:value-of select="//ce:copyright/@year"/></mods:accessCondition>

<mods:genre>{genre}</mods:genre>

<mods:identifier type="pii"><xsl:value-of select="//*[local-name() = 'pii']"/></mods:identifier>

<mods:identifier type="doi"><xsl:value-of select="//dc:identifier"/></mods:identifier>

<!-- maybe later - could conflict with issueIdentifier tag
<mods:identifier type="eid"><xsl:value-of select="//*[local-name() = 'eid'"/></mods:identifier>
-->

<mods:identifier type="isbn"><xsl:value-of select="//prism:isbn"/></mods:identifier>
<mods:identifier type="jid"><xsl:value-of select="//cja:item-info/cja:jid"/></mods:identifier>
<mods:identifier type="aid"><xsl:value-of select="//cja:item-info/cja:aid"/></mods:identifier>

<mods:language>
  <mods:languageTerm type="text">{languageTerm_text}</mods:languageTerm>
  <mods:languageTerm type="code" authority="{languageTerm_authority}">{languageTerm_code}</mods:languageTerm>
</mods:language>
<mods:location>
  <mods:url displayLabel="{location_url_displayLabel}">{location_url}</mods:url>
</mods:location>

<mods:location>
  <mods:physicalLocation>University of Florida</mods:physicalLocation>
  <mods:physicalLocation type="code">UF</mods:physicalLocation>
</mods:location>

<mods:typeOfResource>text</mods:typeOfResource>

<mods:name type="corporate">
  <mods:namePart>{host_institution_namePart}</mods:namePart>
  <mods:role>
    <mods:roleTerm type="text">host institution</mods:roleTerm>
  </mods:role>
</mods:name>

{xml-authors}
<!--  comment
-->

<xsl:for-each select="//ce:keywords/ce:keyword">
<mods:subject>
  <mods:topic>
    <xsl:value-of select="normalize-space(ce:text)"/>
  </mods:topic>
</mods:subject>
</xsl:for-each>

<mods:note displayLabel="Reference"><xsl:value-of select="//dct:description"/></mods:note>
<mods:note displayLabel="Open Access Article">
  <xsl:value-of select="//*[local-name() = 'openaccessArticle']"/></mods:note>
<mods:note displayLabel="Open Archive Article">
  <xsl:value-of select="//*[local-name() = 'openArchiveArticle']"/></mods:note>
<mods:note displayLabel="Harvest Date">{{utc_secs_z}}</mods:note>
{xml_mods_notes}

<mods:originInfo>
  <mods:publisher><xsl:value-of select="//dct:publisher"/></mods:publisher>
  <mods:dateIssued><xsl:value-of select="//prism:coverDate"/></mods:dateIssued>
  <mods:copyrightDate><xsl:value-of select="//ce:copyright/@year"/></mods:copyrightDate>
</mods:originInfo>

<mods:recordInfo>
  <mods:recordIdentifier source="sobekcm">{objid}</mods:recordIdentifier>
  <mods:recordContentSource><xsl:value-of select="//dct:publisher"/></mods:recordContentSource>
</mods:recordInfo>

<mods:relatedItem type="original">
  <mods:physicalDescription>
    <mods:extent>Pages <xsl:value-of select="//prism:pageRange"/></mods:extent>
  </mods:physicalDescription>
</mods:relatedItem>

<mods:titleInfo>
  <mods:title><xsl:value-of select="normalize-space(//dc:title)"/></mods:title>
</mods:titleInfo>

<mods:relatedItem type="host">
    <mods:titleInfo>
            <mods:title>
            <xsl:value-of select="//prism:publicationName"/>
            </mods:title>
      </mods:titleInfo>
    <mods:identifier type="ISSN">{issn}</mods:identifier>
      <mods:part>

            <mods:detail type="volume">
                  <mods:number><xsl:value-of select="//prism:volume"/></mods:number>
                  <mods:caption>vol.</mods:caption>
            </mods:detail>
            <mods:detail type="number">
                  <mods:number><xsl:value-of select="//prism:number"/></mods:number>
                  <mods:caption>no.</mods:caption>
            </mods:detail>
            <mods:extent unit="page">
                  <mods:start><xsl:value-of select="//prism:startingPage"/></mods:start>
                  <mods:end><xsl:value-of select="//prism:endingPage"/></mods:end>
            </mods:extent>
            <mods:date><xsl:value-of select="//prism:coverDate"/></mods:date>
      </mods:part>
</mods:relatedItem>
<!-- Start comment
-->

</mods:mods>
</METS:xmlData>
</METS:mdWrap>
</METS:dmdSec>

<METS:dmdSec ID="DMD2">
<METS:mdWrap MDTYPE="OTHER" OTHERMDTYPE="SOBEKCM" MIMETYPE="text/xml" LABEL="SobekCM Custom Metadata">
<METS:xmlData>
    <sobekcm:procParam>
    <!-- Sobekcm Aggregation elements -->
    {xml_sobekcm_aggregations}

    <sobekcm:Tickler>{{{{sha1-mets-v1}}}}</sobekcm:Tickler>
    </sobekcm:procParam>

    <sobekcm:bibDesc>
        <sobekcm:BibID>{bibid}</sobekcm:BibID>
        <sobekcm:VID>{vid}</sobekcm:VID>

        <sobekcm:Affiliation>
        <sobekcm:HierarchicalAffiliation>
        <sobekcm:Center>{host_institution_namePart}</sobekcm:Center>
        </sobekcm:HierarchicalAffiliation>
        </sobekcm:Affiliation>

        <sobekcm:Publisher>
        <sobekcm:Name><xsl:value-of select="//dct:publisher"/></sobekcm:Name>
        </sobekcm:Publisher>

        <sobekcm:Source>
        <sobekcm:statement code="{source_statement_code}">{publisher}</sobekcm:statement>
        </sobekcm:Source>
    </sobekcm:bibDesc>
</METS:xmlData>
</METS:mdWrap>
</METS:dmdSec>

<METS:structMap ID="STRUCT1" > <METS:div /> </METS:structMap>
</METS:mets>

</xsl:template>
</xsl:stylesheet>
''' # end d_xslt['entry'] template

    ############################ TESTED OK = FOLLOWING 'tested'  XSLT ########################################
d_xslt['tested'] = '''<xsl:stylesheet version="1.0"
    xmlns:bk="http://www.elsevier.com/xml/bk/dtd"
    xmlns:ce="http://www.elsevier.com/xml/common/dtd"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns="http://www.elsevier.com/xml/svapi/article/dtd"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:prism="http://prismstandard.org/namespaces/basic/2.0/"
    xmlns:xocs="http://www.elsevier.com/xml/xocs/dtd"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:tb="http://www.elsevier.com/xml/common/table/dtd"
    xmlns:sb="http://www.elsevier.com/xml/common/struct-bib/dtd"
    xmlns:sa="http://www.elsevier.com/xml/common/struct-aff/dtd"
    xmlns:mml="http://www.w3.org/1998/Math/MathML"
    xmlns:ja="http://www.elsevier.com/xml/ja/dtd"
    >

<xsl:output encoding="UTF-8" method="xml" omit-xml-declaration="no" indent="yes"/>
<xsl:template match="comment()" priority="5"/>
<xsl:template match="/">
<xsl:comment> XSL-inserted comment ( TESTED article ) </xsl:comment>

<METS:mets OBJID="{objid}"
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

<METS:metsHdr CREATEDATE="{{{{create_date}}}}" ID="{objid}"
  LASTMODDATE="{{{{last_mod_date}}}}" RECORDSTATUS="COMPLETE">

<METS:agent ROLE="CREATOR" TYPE="ORGANIZATION">
  <METS:name>{agent_creator_organization_name}</METS:name>
</METS:agent>

<METS:agent ROLE="CREATOR" OTHERTYPE="SOFTWARE" TYPE="OTHER">
  <METS:name>{agent_creator_software_name}</METS:name>
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

<mods:accessCondition>{access_condition}<xsl:value-of select="//ce:copyright/@year"/></mods:accessCondition>
<mods:identifier type="pii"><xsl:value-of select="//xocs:pii-unformatted"/></mods:identifier>

<mods:genre authority="{genre_authority}">{genre}</mods:genre>
<mods:identifier type="doi"><xsl:value-of select="//xocs:doi"/></mods:identifier>

<mods:language>
<mods:languageTerm type="text">{languageTerm_text}</mods:languageTerm>
<mods:languageTerm type="code" authority="{languageTerm_authority}">{languageTerm_code}</mods:languageTerm>
</mods:language>
<mods:location>
  <mods:url displayLabel="{location_url_displayLabel}">{location_url}</mods:url>
</mods:location>

<mods:location>
  <mods:physicalLocation>University of Florida</mods:physicalLocation>
  <mods:physicalLocation type="code">UF</mods:physicalLocation>
</mods:location>

<!-- -->
<mods:typeOfResource>text</mods:typeOfResource>

<mods:name type="corporate">
  <mods:namePart><xsl:value-of select="//ce:affiliation/ce:textfn"/></mods:namePart>
  <mods:role>
    <mods:roleTerm type="text">host institution</mods:roleTerm>
  </mods:role>
</mods:name>

{xml-authors}

<!-- subject topics- These from Elsevier are phrases with no authority info -->

<xsl:for-each select="//dcterms:subject">
<mods:subject>
  <mods:topic>
    <xsl:value-of select="normalize-space(.)" />
  </mods:topic>
</mods:subject>
</xsl:for-each>

<mods:note displayLabel="Harvest Date">{{utc_secs_z}}</mods:note>
{xml_mods_notes}

<mods:originInfo>
  <mods:publisher><xsl:value-of select="//prism:publisher"/></mods:publisher>
  <mods:dateIssued><xsl:value-of select="//prism:coverDate"/></mods:dateIssued>
  <mods:copyrightDate><xsl:value-of select="//ce:copyright/@year"/></mods:copyrightDate>
</mods:originInfo>

<mods:recordInfo>
  <mods:recordIdentifier source="sobekcm">{objid}</mods:recordIdentifier>
  <mods:recordContentSource><xsl:value-of select="//prism:publisher"/></mods:recordContentSource>
</mods:recordInfo>

<!-- -->

<mods:relatedItem type="original">
  <mods:physicalDescription>
    <mods:extent>Pages <xsl:value-of select="//prism:pageRange"/></mods:extent>
  </mods:physicalDescription>
</mods:relatedItem>

<mods:titleInfo>
<!-- many elsevier records lack ce:title as of 201603, so revert to dc:title
  <mods:title><xsl:value-of select="normalize-space(//ce:title)"/></mods:title>
-->
  <mods:title><xsl:value-of select="normalize-space(//dc:title)"/></mods:title>
</mods:titleInfo>

<mods:relatedItem type="host">
    <mods:titleInfo>
            <mods:title><xsl:value-of select="//prism:publicationName"/></mods:title>
      </mods:titleInfo>
    <mods:identifier type="ISSN">{issn}</mods:identifier>
      <mods:part>
            <mods:detail type="volume">
                  <mods:number><xsl:value-of select="//prism:volume"/></mods:number>
                  <mods:caption>vol.</mods:caption>
            </mods:detail>
            <mods:detail type="number">
                  <mods:number><xsl:value-of select="//prism:number"/></mods:number>
                  <mods:caption>no.</mods:caption>
            </mods:detail>
            <mods:extent unit="page">
                  <mods:start><xsl:value-of select="//prism:startingPage"/></mods:start>
                  <mods:end><xsl:value-of select="//prism:endingPage"/></mods:end>
            </mods:extent>
            <mods:date><xsl:value-of select="//prism:coverDate"/></mods:date>
      </mods:part>
</mods:relatedItem>

</mods:mods>

</METS:xmlData>
</METS:mdWrap>
</METS:dmdSec>

<METS:dmdSec ID="DMD2">
<METS:mdWrap MDTYPE="OTHER" OTHERMDTYPE="SOBEKCM" MIMETYPE="text/xml" LABEL="SobekCM Custom Metadata">
<METS:xmlData>

    <sobekcm:procParam>

    {xml_sobekcm_aggregations}

    <sobekcm:Tickler>{{sha1-mets-v1}}</sobekcm:Tickler>
    </sobekcm:procParam>

    <sobekcm:bibDesc>
        <sobekcm:BibID>{bibid}</sobekcm:BibID>
        <sobekcm:VID>{vid}</sobekcm:VID>

        <sobekcm:Affiliation>
          <sobekcm:HierarchicalAffiliation>
           <sobekcm:Center><xsl:value-of select="//ce:affiliation/ce:textfn"/></sobekcm:Center>
          </sobekcm:HierarchicalAffiliation>
        </sobekcm:Affiliation>

        <sobekcm:Publisher>
        <sobekcm:Name><xsl:value-of select="//prism:publisher"/></sobekcm:Name>
        </sobekcm:Publisher>

        <sobekcm:Source>
        <sobekcm:statement code="{source_statement_code}"><xsl:value-of select="//prism:publisher"/>
        </sobekcm:statement>
        </sobekcm:Source>

    </sobekcm:bibDesc>

</METS:xmlData>
</METS:mdWrap>
</METS:dmdSec>

<METS:structMap ID="STRUCT1" > <METS:div /> </METS:structMap>

</METS:mets>
</xsl:template>
</xsl:stylesheet>
''' # end d_xslt['tested'] template

def get_d_xslt():
    return d_xslt

'''
This is program 'exoldmets' which is python 3.x code.

Required input parameter 'input_base_directory' is our input directory name.
For background, that is the output directory (a git repo, actually) with
output data from one or more prior separate 'ealdxml' program runs.

See UF elsevier program ealdxml.py for more details.

Program exoldmets.py looks into the subfolder hierarchy of YYYY/MM/DD
directories to find at the lowest level all files named as
'pii_{}.xml'.format(pii), where pii is the 'publisher item identifier (pii)'
used by Elsevier.

The pii file may contain the root xml tag 'failure' in which case we
stop processing for that file.
A 'failure' tag means that an attempt to retrieve the full text for
that pii failed by the precursor program ealdxml.
Such a file is preserved in case we want to review the errors.

Otherwise, the pii file has Elsevier 'full-text' metadata for an article.

Ealdxml will always use the pii to compare it to the marshal database
'item_elsevier_ufdc' table that includes the complete set of Elsevier
pii articles already contained in the target SobekCM system (eg UFDC production
integration test, or a local test database) for the METS files that
ealdxml.py produces.

In the item_elseiver_ufdc table, one of the column values is bibid, with string
values like 'LS00012345_0001'.
If the pii of an input pii file is already in that item_elsevier_ufdc table,
we preserve/reserve and honor the established bibid value for it, and we only
prescribe 'new' bibids to load into UFDC for 'new' pii-identified articles.

--- rest of this docstring is under revision---

Another requirement is to have either an input argument (1) 'commit_hash'
or (2) 'commit_message' for example a string with secsz_start, a UTC time with
a Z suffix, to the resolution of time unit 'seconds', used to query git and find
a single commit_hash for it (if not found or more than 1 is found, it would be a
fatal error)

Once we have a good commit hash, we invoke a git command to find all contained files
that were changed by that commit
(see url
http://stackoverflow.com/questions/424071/how-to-list-all-the-files-in-a-commit)
 $ git show --pretty="format:" --name-only bd61ad98
We use only the pii files in that list that are also under the 'full' sub-folder
that comprise the list of input pii fiiles
to for exoldmets to process.

'''
from collections import OrderedDict
import subprocess

import datetime
import pytz
import os
import sys
# import http.client
import requests
import urllib.parse
import json
import pprint
from pathlib import Path
import hashlib
import csv
#speedup to set large field_size_limit?
csv.field_size_limit(256789)
#import xlrd
import inspect
# import xlwt
import pypyodbc
import etl

class DBConnection():
    def __init__(self, server='lib-sobekdb\\sobekcm',db='SobekDB'):
        self.verbosity = 1
        self.server = server
        self.db = db
        self.outdelim = '\t'
        self.cxs = ("DRIVER={SQL Server};SERVER=%s;"
              "dataBASE=%s;Trusted_connection=yes"
              % (self.server, self.db))
        try:
            # Open the primary cursor for this connection.
            self.conn = pypyodbc.connect(self.cxs)
        except Exception as e:
            print("Connection attempt FAILED with connection string:\n'{}',\ngot exception:\n'{}'"
                 .format(self.cxs,repr(e)))
            raise ValueError("{}: Error. Cannot open connection for {}. Does your user account have permissions?"
                    .format(repr(self), self.cxs))

        if self.conn is None:
            raise ValueError(
              "Cannot connect using pyodbc connect string='%s'"
              % (self.cxs) )
        self.cursor = self.conn.cursor()
        if self.cursor is None:
            raise ValueError(
              "%s: ERROR - Cannot open cursor." % repr(self))

    # query(): given query string, return a tuple of
    # [0] - header string of column names, [1] list of result rows, separated by self.outdelim
    def query(self, query=''):
        cur = self.cursor.execute(query)
        header = ''
        for i, field_info in enumerate(cur.description):
            header += self.outdelim if i > 0 else ''
            header += field_info[0]

        results = []
        for row in cur.fetchall():
            result = ''
            outdelim = ''
            for (i, field_value) in enumerate(row):
                result += outdelim + str(field_value)
                outdelim = self.outdelim
            results.append(result)
        return header, results

    def select(self, query=''):
        return self.query(query)
    def close(self):
        self.conn.close()
#end class DBConnection

'''
Program exoldmets inputs information from xml files.
These input xml files are created by program ealdxml.
The program ealdxml's input is from the Elsevier Full-Text API based on Search API
results for queries for UF-Authored articles.

Exoldmets does, for each xml input file:
-- checks its PII value to see if a UF BibID has been assigned for it, and if
   not, it assigns the next unusued UF BibID  that is not associated with
   a PII value, based on an input parameter. Whoever runs this must be certain
   that the input paramter identifies the first bibid to use and that subsequent ones are available.

-- Program exoldmets also transforms each input xml file in stages.
    First, in stage 1 it uses XSLT to create a precursor mets.xml file that is
  -- also augmented with sobek mets section
  -- and with article metadata transformed for sobekcm consumption by its Builder
     process.
 -- and ...?
 to produce the final mets.xml output file for each article.

Except for the first two lines, the design of output mets files is derived
from observing sobekcm example mets files that are saved in "the resources directory"
archived by FALCE ,formerly FLVC, as of year 2016.

The design is also combined with notions of Elsevier API Search results and
possibly secondary Elsevier Full Text retrieval api results, to represent
'journal articles' for UF Smathers.

The first 2 lines for an output mets.xml file are inserted by the
builder on top of the orignal input mets files picked up by the builder.
These files are meant to be picked up by the Sobek builder, that is, 'ingested'
by the SobekCM builder into the SobekCM database used by the SobekCM Web Server
Application.

Also see: http://www.loc.gov/standards/mods/v3/mods-userguide-examples.html#journal_article
'''

'''
Method get_sobek_dicts():
  return two dicts of SobekCM-specific params with defaults if not given in arguments.

return dict 1: dict d_params_track
 -- keys are param names certain type of values:
 -- These are values, that if they change from load to load, should be tracked, and so the
    sha1_hash for this article should include them ,

return dict 2: dict d_vary
   has values that may vary from load to load, and if so, their variance alone does not merit
   re-submitting such articles to the inbound folder, so the sha1_hash does not include them.

Define basic parameters for elsevier xslt template for SobekCM builder to process.
Should add validations of particular variable values here if promote this function
to a library method.

Here we just support default values for some often-seen well-used xml tags.
This method requires/assumes that this dict is used only with elsevier Full-text API result xml,
as it relies upon that known xml structure.
'''
def get_sobek_dicts(create_date=None
    , last_mod_date=None
    , access_condition=None
    , record_content_source=None
    , agent_creator_organization_name='ELSEVIER,Elsevier B.V.'
    , agent_creator_software_name='UF Elsevier full-text API to METS convertor v0.1'
    , agent_creator_individual_name='UFAD\lib-adm-podengo'
    , agent_creator_individual_note=(
        'Imported from Elsevier full text API v3 of UF authored articles')
    , languageTerm_text='English'
    , languageTerm_code='eng'
    , languageTerm_authority='iso639-2b'
    , location_url=None
    , location_url_displayLabel='Related URL'
    , pii=None
    , issn=None
    , publisher=None
    # For some values, we put in the xsl statement to derive them from input xml...
    # so we can override them regardless of what is in the input XML, if need be.
    , host_institution_namePart=None
    # mods_note is list of lists, subitem 0 is displayLabel, subitem 1 is note
    # value
    # Eg, ['General','A fine item this is!'], ['TamaleMeter','73%']']
    , mods_notes=None
    # Param sobekcm_aggregations must have a value from the target Sobek
    # database table SobekCM_Item_Aggregation, column Code.
    , sobekcm_aggregations=['IELSEVIER','ALL','UFIRG']
    # Param source_statement_code holds ELSEVIER for elsevier, and may be other
    # to-be-defined values for other publishers, which may have an authoritative
    # sobekdb table holding those values in the future?
    , source_statement_code='ELSEVIER'
    ):
    d_params_track = {}
    d_params_vary = {}
    utc_now = datetime.datetime.utcnow()
    # Make date formats with utc time aka Zulu time, hence Z suffix.
    # On 20160209, this is the second 'edtf' format on the first bullet at
    # http://www.loc.gov/standards/datetime/, on the download of the PowerPoint
    # Presentation link: http://www.loc.gov/standards/datetime/edtf.pptx
    # NOTE: this var is used as a value field in an xml file that requires this exact format.
    utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Parameter publisher: default to dct publisher
    if not publisher:
        publisher='{publisher}'
    # Add optional extra mods:note attribute=value.
    # Harvest date and dct citation are always added in the xslt.
    xml_mods_notes = ''
    if mods_notes:
        for note in mods_notes:
            xml_mods_notes += '<mods:note displayLabel={}>{}</mods:note>'.format(note[0],note[1])
        #print("\n\n********************* EXTRA XML_MODS_NOTES={}\n\n".format(xml_mods_notes))

    xml_sobekcm_aggregations = ''
    if sobekcm_aggregations is None:
        sobekcm_aggregations=[]
    else:
        for aggregation in sobekcm_aggregations:
            xml_sobekcm_aggregations += (
                '<sobekcm:Aggregation>{}</sobekcm:Aggregation>'
                .format(aggregation))
    #print("\n\n********************* XML_SOBEKCM_AGGREGATIONS={}\n\n".format(xml_sobekcm_aggregations))

    d_params_track.update({
          'agent_creator_software_name' : agent_creator_software_name
        , 'agent_creator_individual_name' : agent_creator_individual_name
        , 'agent_creator_individual_note' : agent_creator_individual_note
        , 'agent_creator_organization_name' : agent_creator_organization_name
        , 'languageTerm_text' : languageTerm_text
        , 'languageTerm_code' : languageTerm_code
        , 'languageTerm_authority' : languageTerm_authority
        , 'genre_authority' : 'sobekcm'
        , 'genre' : 'article'
        , 'location_url_displayLabel' : location_url_displayLabel
        , 'location_url' : location_url
        , 'host_institution_namePart' : host_institution_namePart
        , 'xml_mods_notes' : xml_mods_notes
        , 'publisher': publisher
        , 'source_statement_code' : source_statement_code
        , 'xml_sobekcm_aggregations' : xml_sobekcm_aggregations
        })

    if create_date is None:
        create_date = utc_secs_z
    if last_mod_date is None:
        last_mod_date = utc_secs_z

    if record_content_source is None:
        record_content_source = 'Elsevier B.V'

    if access_condition is None or access_condition == '':
        # Must add \u00A0 to end to ensure non-breaking space between copyright symbol and year.
        access_condition = (
            'This item is licensed with the Creative Commons Attribution No '
            'Derivatives License.'
            '  This license allows for redistribution, commercial and '
            'non-commercial, as long as '
            'it is passed along unchanged and in whole, with credit to '
            'the author. ©\u00A0')

    d_params_track.update({
       'access_condition' : access_condition
      ,'record_content_source' : record_content_source
      ,'issn': issn
      ,'pii' : pii
      ,'last_mod_date': '{last_mod_date}' #Force second format() evaluation to work OK within double quotes
      # ,'dns' : '{{http://www.w3.org/2005/Atom}}' #default namespace prefix
    })
    d_params_vary.update({
       'create_date' : create_date
      ,'last_mod_date' : last_mod_date
      ,'utc_secs_z': utc_secs_z
    })
    return d_params_track, d_params_vary

#end def get_sobek_dicts()

from lxml import etree
import os
'''
Method uf_affiliation_value

Given an Elsevier-asserted author affiliation name, this method:
returns 1 - if the name identifies the university of florida
returns 0 - otherwise
NB: Elsevier is very good about using one of the substrings sought,
however it will be most often be embedded in other text, hence the
need for this method.

'''
def uf_affiliation_value(name):
    text_lower = name.lower() if name is not None else ''
    #print("Using affil argument text={}".format(repr(text)))
    for match in ['university of florida','univ.fl','univ. fl'
        ,'univ fl' ,'univ of florida'
        ,'u. of florida','u of florida']:
        if text_lower.find(match) != -1:
            #print("Match")
            return 1
    #print("NO Match")
    return 0

'''
Method xslt_transform_format(node_root_input, d_ns, xslt_format_str,
    d_sobek_track=None, d_sobek_vary=None)

Given xslt_format_str and node_root_input, d_sobek_track, d_sobek_vary
 (1) Harvest the author-groups from the article xml file if
     the article is the serial type.
     Create a list of values, one-for-one with authors in each author-group,
     where each value includes the author name and a role type of either author
     or UF author
     Create a string xml_authors that represents the author information in
     xml format.
     Note: the input xslt_format_str will have a variable {xml_authors} into
     which the xml_format info
     will be inserted in the first formatting phase of transformation.

 (2) transform the node_root_input per the xslt_format_str.
     Note: xslt_format_str does have {{xxx}}
     style inserted python formatting syntax, which should be conveyed to
     the output xslt doc.
 (3) make a hash of the new xslt transform
 (4) use python d_sobek_vary to fill in the python-formatted variable
     values with SobekCM-specific information. These are values that we allow
     to change in a future Elsevier
     harvesting run without triggering the code to actually upload the new
     Elsevier record.

RETURN VALUE: d_return()
 d_return={} with key:values of:
   'sha1_hash':
       value is string with the sha1_mets hash value we save for the tracked
       values in mets file
   'str_mets':
       the resulting mets file suitable for saving and despositing in to the
       SobekCM Builder's inbound folder.

   'node_rawtext': node's rawtext
   'failure_message': a message for the failure code or ''
   'log_messages' : warning message
'''

def xslt_transform_format(core_pii='',node_root_input=None, d_ns=None
    ,xslt_format_str=None, d_sobek_track=None, d_sobek_vary=None
    ,verbosity=0):

    me="xslt_transform_format"
    if not all(['node_root_input','d_sobek_track', 'd_sobek_vary', 'd_ns']):
        msg = ("\n***** {}: Bad arguments!\n".format(me))
        raise ValueError(msg)

    d_return = {'sha1_hash':'', 'str_mets':'', 'node_rawtext':''
                , 'failure_message':''};

    if verbosity > 0:
          print("\n\n{}: STARTING... with len(d_ns)='{}'".format(me,len(d_ns)))
    # Extract author-group and author information from node_root_input.

    # If an author has a cross-ref attribute refid that starts with 'af',
    # we accept it as a cross-ref id key.
    # 20161104 Note on pii=S0741521416000811 - it is a poster sesssion with
    # a presented wrapper tag,
    # and within that is a tag collaboration with an author group and authors, and the tag
    # affiliation is within the presented tag, not in the author-group or collaboration tag,
    # with matching ref = aff3 - this algo does not match that, leading to: ISSUE: should we ?
    #
    # The affiliation name of an index is scanned to determine whether it is a UF affiliation,
    # and if so, the author will be assigned the roleterm of (UF author), otherwise just (author)
    #
    xml_authors = ''
    log_messages = []

    # Start by extracting from the article's xml input file, some input file
    # nodes and values.
    node_fulltext = node_root_input.find('.//xocs:rawtext', namespaces=d_ns)
    if node_fulltext is None:
        # fallback: try body tag for full text if xocs:rawtext was empty nothing
        xpath = ".//{*}body"
        node_fulltext = node_root_input.find(xpath, namespaces=d_ns)

    d_return['node_rawtext'] = node_fulltext

    node_pii = node_root_input.find('.//xocs:pii-unformatted', namespaces=d_ns)

    # PII min len of 11 seems like a good check
    if node_pii is not None and len(node_pii.text) > 10:
        pii = node_pii.text
        if (pii != core_pii):
            log_messages.append("xocs:pii is {}, but using core pii ='' next."
              .format(me,pii,core_pii))
            d_return['log_messages'] = log_messages
            pii = core_pii
    else:
        log_messages.append("{}:No xocs:pii found. Trying core pii ='{}' next."
              .format(me,core_pii))
        d_return['log_messages'] = log_messages
        pii = core_pii

    if len(pii) < 10:
        # Note: pii is required for an Elsevier item's mets file, so we can use
        # that to apply future updates or deletions.
        msg = 'core_pii is also bad. No pii value found for input xml file.'
        d_return['failure_message'] = msg
        return d_return

    if verbosity > 0:
        print("{}: using pii={}".format(me,pii))

    node_openaccess = node_root_input.find('.//{*}openaccess', namespaces=d_ns)
    openaccess_suffix = ''
    if node_openaccess is not None:
        openaccess_text = node_openaccess.text
        if verbosity > 1:
            print("{}: Got openaccess='{}'"
                  .format(me,openaccess_text))

    # Start to use d_sobek_track {} to store some input values whose value
    # changes we will want to track

    #Produce the location_url, the seed for the Builder to set the SobekCM_Item.link value
    d_sobek_track.update({ 'location_url' : (
        'http://www.sciencedirect.com/science/article/pii/{}'.format(pii))
        })

    node_serial_item = node_root_input.find('.//xocs:serial-item', namespaces=d_ns)
    if verbosity > 1:
        print("{}: Got node_serial_item='{}'"
              .format(me,rep(node_serial_item)))

    if node_serial_item is not None:
        #We have a serial item. For this type of item we will find any UF Authors
        item_has_uf_author = 0
        xml_authors = ''

        # For each author_group of this doc serial item, assign any UF Authors ...
        # We'll build up a chunk of target XML into a variable to xml-authors to stuff into
        # the output string as format() arguments later.

        for node_ag in node_serial_item.findall('.//ce:author-group', namespaces=d_ns):
            # d_id_aff: key is string for attribute id for an affiliation, value is its lxml node
            d_id_aff = {}
            #print('Got an author group, getting affiliations')

            # Save all child affiliation nodes keyed by their id
            for node_aff in node_ag.findall('./ce:affiliation', namespaces=d_ns):
                #print('Got affiliation ')
                if 'id' in node_aff.attrib:
                    #print("Got affiliation with id={}".format(id))
                    d_id_aff[node_aff.attrib['id']] = node_aff
                else:
                    # use empty string as ID - support author-groups all with single affiliation,
                    # where neither author refid nor affiliation id attributes are needed or used.
                    d_id_aff[''] = node_aff

            xml_authors = ''
            # Generate xml with a list of the authors, also indicating whether each is a UF author.
            #print("Getting authors")
            for node_author in node_ag.findall('./ce:author', namespaces=d_ns):
                #print("got an author")
                is_uf_author = 0
                author_has_ref_aff = None
                node_refs = node_author.findall('./ce:cross-ref', namespaces=d_ns)
                for node_ref in node_refs:
                    #print("got a cross-ref")
                    if 'refid' in node_ref.attrib:
                        refid = node_ref.attrib['refid']
                        #print("got a refid={}".format(refid))
                        if refid.startswith('af') and refid in d_id_aff:
                            author_has_ref_aff = 1
                            if refid not in d_id_aff:
                                print("WARN: Author has refid={}, but no affiliation has that id"
                                     .format(refid))
                            node_aff = d_id_aff[refid]
                            node_text = etree.tostring(node_aff, encoding='unicode', method='text')
                            # Must replace text tabs with spaces, used as bulk load delimiter,
                            # else bulk insert msgs appear 4832 and 7399 and inserts fail.
                            node_text = node_text.replace('\t',' ').replace('\n',' ').strip()
                            #print("Found affiliation={}".format(node_text))
                            # set to 1 if this is a UF affiliation, else set to 0.
                            is_uf_author = uf_affiliation_value(node_text)
                            #print("For this affiliation, is_uf_author={}".format(is_uf_author))
                            if is_uf_author:
                                item_has_uf_author = 1
                                break
                # end node_refs (cross-refs) for this author
                if not author_has_ref_aff:
                    #Still found no affiliation for this author, so use empty string for refid
                    node_aff = d_id_aff.get('',None)
                    if node_aff is not None:
                        node_text = etree.tostring(node_aff, encoding='unicode', method='text')
                        node_text = node_text.replace('\t',' ').replace('\n',' ').strip()
                        is_uf_author = uf_affiliation_value(node_text)
                        #print("For this affiliation, is_uf_author={}".format(is_uf_author))
                        if is_uf_author:
                            item_has_uf_author = 1

                # end 'backup' method for secondary author affiliation assignment found to be
                # sometimes applicable in Elsever-speicific full-text xml files.

                # Here, if we find that is_uf_author is 1, author has a UF affiliation.
                # TODO ALT: Generator can return here: (is_uf_author, node_author)
                role = 'UF author' if is_uf_author == 1 else 'author'
                surname = ''
                given_name = ''
                node = node_author.find('./ce:surname', namespaces=d_ns)
                surname = node.text if node is not None else ''
                node = node_author.find('./ce:given-name', namespaces=d_ns)
                given_name = node.text if node is not None else ''
                xml_authors += '''

                <mods:name type="personal">
                  <mods:namePart>{}, {}</mods:namePart>
                  <mods:role>
                    <mods:roleTerm type="text">{}</mods:roleTerm>
                  </mods:role>
                </mods:name>
                '''.format(etl.escape_xml_text(surname), etl.escape_xml_text(given_name), role)
            # end author loop
        #end author-group loop

        if item_has_uf_author == 0:
            msg = ("Serial Item has NO UF Authors.")
            #print(msg)
            # Reject/refuse to create UF METS file since no uf_author contributed to this article.
            d_return['failure_message'] = msg
            return d_return
    # end clause if node_serial_item is not None - processing authors of serial articles
    else:
      # This is a non-serial, return failure, as we will not host these now
      d_return['failure_message'] = "Non-serial item. Skipping."
      return d_return

    # Note, we are admitting all non-serial articles for now regardless of any uf_authors.
    d_sobek_track['xml-authors'] = xml_authors

    node_desc = node_root_input.find('.//dc:description', namespaces=d_ns)
    if node_desc is None:
        description = ''
    else:
        description = etree.tostring(node_desc, encoding='unicode', method='text')

    if description.startswith('Abstract'):
        #print("Removing startswith 'abstract'")
        description = description[8:]
    if description.startswith('Introduction'):
        description = description[12:]

    # Analysis of sampling of 30K elsevier articles 20160925 show no spanish abstracts
    # so keep english for now. We can reload later if need a language change.
    # Also misc < and > etc in the description must be escaped because we create xml here.

    xml_description = ('<mods:abstract lang="en">'
          + etl.escape_xml_text(description) + '</mods:abstract>')

    #print("Got xml_description='{}'".format(xml_description))
    d_sobek_track['description'] = xml_description

    #--------------------------------------------------------------------------------------------#
    # Perform the first 'python format()-based' round of variable substitution with the xslt xml
    # template itself, on the way to  making a final output file:
    # Apply only the variable values we want to track to detect
    # METS files updates with 'meaningful' changes:
    #--------------------------------------------------------------------------------------------#

    # Create xslt_str2, the pass1 output xslt string of METS with the tracked variables
    xslt_str2 = xslt_format_str.format(**d_sobek_track)

    if verbosity > 0:
      print("{}:Pass1 got formatted xslt_str2, len='{}'".format(me,len(xslt_str2)))

    try:
        # Create tree_xslt from the xslt_str2
        tree_xslt = etree.fromstring(xslt_str2)
    except Exception as e:
        msg = ("Parse error='{}' etree.fromstring(xslt_str2), description='{}',xslt_str2='{}'. Skipping"
              .format(repr(e), description, xslt_str2))
        print(msg)
        d_return['failure_message'] = msg
        return d_return

    try:
        # Make this into an xsl_transform method designed to do an xslt transform for the tree_xslt
        xsl_transform = etree.XSLT(tree_xslt)

    except Exception as e:
        print("Got exception={}".format(repr(e)))
        print("Using xslt_str='{}'".format(xslt_str))
        raise e

    #----------------------------------------------------------------------------------- #
    # Pass 2 or transformation 2 - to produce tree_result_doc

    # Use the xsl_transform method to convert the given node_root_input to
    # tree_result_doc here the xslt functionality is used to insert some
    # scalar values into the tree_result_doc from the input doc.
    tree_result_doc = xsl_transform(node_root_input)
    #----------------------------------------------------------------------------------- #

    # Translate tree_result_doc back to a string that should still contain the
    # python formatted variable syntax and format it with d_sobek values to a
    # result string for the article mets file.
    # Make a sha1 hash on the result_format_str (with the python variable names,
    # not values in the text)
    # so we will not get a 'false alarm' on a change for timestamps and other
    # sobek values.
    # NOTE: lxml etee.tostring is a MISNOMER, it returns bytes, not a string,
    # unless encoding_method is set to 'UNICODE'.
    # But only a string has the format() method, which we need a few code
    # lines below.

    result1_bytes = etree.tostring(
        tree_result_doc, pretty_print=True, xml_declaration=True)

    # Start setting up some d_sobek_vary values that may 'vary' freely (as
    # opposed to track variables) from harvest to harvest for an item without
    # our wanting to ingest the record again on account of their uninteresting changes.
    sha1_mets = hashlib.sha1()
    sha1_mets.update(result1_bytes)
    sha1_hexdigest = sha1_mets.hexdigest()
    d_return['sha1_hash'] = sha1_mets.hexdigest()
    d_sobek_vary['sha1-mets-v1'] = sha1_hexdigest.upper()

    # Decode the utf-8 bytes back to normal python3 string (default output
    # encoding after a decode() call is python3 string encoding( unicode),
    # so we can later use format method
    result1_str = result1_bytes.decode("utf-8")

    # In results2_str , we will use format() to insert d_sobek_track variable values, so now before we do
    # that result1 str, if printed, will reveal the d_sobek_vary variable names appearing, as in: {last_mod_date}
    # print("Using format(**d_sobek_vary) on result1_str='{}'".format(result1_str))
    #-----------------------------------------------------------------------------------#
    # Now, do final 'pass3' to insert 'vary' variable values into the final rendition suitable
    # for outputting, in result2_str_formatted.
    #-----------------------------------------------------------------------------------#

    try:
        str_mets = result1_str.format(**d_sobek_vary)
    except Exception as e:
        print("result1_str='{}' produced a format error with **d_sobek_vary!".format(result1_str))
        raise e

    if verbosity > 0:
      print("{}: returning str_mets with len={}".format(me,len(str_mets)))
    d_return['str_mets'] = str_mets
    return d_return

#end def xslt_transform_format0()

def xslt_transform_format2(core_pii='',node_root_input=None, d_ns=None
    ,xslt_format_str=None, d_sobek_track=None, d_sobek_vary=None
    ,verbosity=0):

    me="xslt_transform_format2"
    if not all(['node_root_input','d_sobek_track', 'd_sobek_vary', 'd_ns']):
        msg = ("\n***** {}: Bad arguments!\n".format(me))
        raise ValueError(msg)

    d_return = {'sha1_hash':'', 'str_mets':'', 'node_rawtext':''
                , 'failure_message':''};

    if verbosity > 0:
          print("\n\n{}: STARTING... with len(d_ns)='{}'".format(me,len(d_ns)))
    # Extract author-group and author information from node_root_input.

    # If an author has a cross-ref attribute refid that starts with 'af',
    # we accept it as a cross-ref id key.
    # 20161104 Note on pii=S0741521416000811 - it is a poster sesssion with
    # a presented wrapper tag,
    # and within that is a tag collaboration with an author group and authors, and the tag
    # affiliation is within the presented tag, not in the author-group or collaboration tag,
    # with matching ref = aff3 - this algo does not match that, leading to: ISSUE: should we ?
    #
    # The affiliation name of an index is scanned to determine whether it is a UF affiliation,
    # and if so, the author will be assigned the roleterm of (UF author), otherwise just (author)
    #
    xml_authors = ''
    log_messages = []

    # Start by extracting from the article's xml input file, some input file
    # nodes and values.
    node_fulltext = node_root_input.find('.//xocs:rawtext', namespaces=d_ns)
    if node_fulltext is None:
        # fallback: try body tag for full text if xocs:rawtext was empty nothing
        xpath = ".//{*}body"
        node_fulltext = node_root_input.find(xpath, namespaces=d_ns)

    d_return['node_rawtext'] = node_fulltext

    node_pii = node_root_input.find('.//xocs:pii-unformatted', namespaces=d_ns)

    # PII min len of 11 seems like a good check
    if node_pii is not None and len(node_pii.text) > 10:
        pii = node_pii.text
        if (pii != core_pii):
            log_messages.append("xocs:pii is {}, but using core pii ='' next."
              .format(me,pii,core_pii))
            d_return['log_messages'] = log_messages
            pii = core_pii
    else:
        log_messages.append("{}:No xocs:pii found. Trying core pii ='{}' next."
              .format(me,core_pii))
        d_return['log_messages'] = log_messages
        pii = core_pii

    if len(pii) < 10:
        # Note: pii is required for an Elsevier item's mets file, so we can use
        # that to apply future updates or deletions.
        msg = 'core_pii is also bad. No pii value found for input xml file.'
        d_return['failure_message'] = msg
        return d_return

    if verbosity > 0:
        print("{}: using pii={}".format(me,pii))

    node_openaccess = node_root_input.find('.//{*}openaccess', namespaces=d_ns)
    openaccess_suffix = ''
    if node_openaccess is not None:
        openaccess_text = node_openaccess.text
        if verbosity > 1:
            print("{}: Got openaccess='{}'"
                  .format(me,openaccess_text))

    # Start to use d_sobek_track {} to store some input values whose value
    # changes we will want to track

    #Produce the location_url, the seed for the Builder to set the SobekCM_Item.link value
    d_sobek_track.update({ 'location_url' : (
        'http://www.sciencedirect.com/science/article/pii/{}'.format(pii))
        })

    node_serial_item = node_root_input.find('.//xocs:serial-item', namespaces=d_ns)
    if verbosity > 1:
        print("{}: Got node_serial_item='{}'"
              .format(me,rep(node_serial_item)))
    ##new

    if node_serial_item is not None:
        #We have a serial item. For this type of item we will find any UF Authors
        item_has_uf_author = 0
        xml_authors = ''

        for is_uf_author, node_author in uf_elsevier_item_authors(
            node_root_input=node_root_input, namespaces=d_ns):

            if is_uf_author:
                    item_has_uf_author = 1
            # end 'backup' method for secondary author affiliation assignment found to be
            # sometimes applicable in Elsever-speicific full-text xml files.

            # Here, if we find that is_uf_author is 1, author has a UF affiliation.
            role = 'UF author' if is_uf_author == 1 else 'author'
            surname = ''
            given_name = ''
            node = node_author.find('./ce:surname', namespaces=d_ns)
            surname = node.text if node is not None else ''
            node = node_author.find('./ce:given-name', namespaces=d_ns)
            given_name = node.text if node is not None else ''

            xml_authors += '''

            <mods:name type="personal">
              <mods:namePart>{}, {}</mods:namePart>
              <mods:role>
                <mods:roleTerm type="text">{}</mods:roleTerm>
              </mods:role>
            </mods:name>
            '''.format(etl.escape_xml_text(surname), etl.escape_xml_text(given_name), role)

        #end is_uf_author group loop

        if item_has_uf_author == 0:
            msg = ("Serial Item has NO UF Authors.")
            #print(msg)
            # Reject/refuse to create UF METS file since no uf_author contributed to this article.
            d_return['failure_message'] = msg
            return d_return
    # end clause if node_serial_item is not None - processing authors of serial articles
    else:
      # This is a non-serial, return failure, as we will not host these now
      d_return['failure_message'] = "Non-serial item. Skipping."
      return d_return

    # Note, we are admitting all non-serial articles for now regardless of any uf_authors.
    d_sobek_track['xml-authors'] = xml_authors

    node_desc = node_root_input.find('.//dc:description', namespaces=d_ns)
    if node_desc is None:
        description = ''
    else:
        description = etree.tostring(node_desc, encoding='unicode', method='text')

    if description.startswith('Abstract'):
        #print("Removing startswith 'abstract'")
        description = description[8:]
    if description.startswith('Introduction'):
        description = description[12:]

    # Analysis of sampling of 30K elsevier articles 20160925 show no spanish abstracts
    # so keep english for now. We can reload later if need a language change.
    # Also misc < and > etc in the description must be escaped because we create xml here.

    xml_description = ('<mods:abstract lang="en">'
          + etl.escape_xml_text(description) + '</mods:abstract>')

    #print("Got xml_description='{}'".format(xml_description))
    d_sobek_track['description'] = xml_description

    #--------------------------------------------------------------------------------------------#
    # Perform the first 'python format()-based' round of variable substitution with the xslt xml
    # template itself, on the way to  making a final output file:
    # Apply only the variable values we want to track to detect
    # METS files updates with 'meaningful' changes:
    #--------------------------------------------------------------------------------------------#

    # Create xslt_str2, the pass1 output xslt string of METS with the tracked variables
    xslt_str2 = xslt_format_str.format(**d_sobek_track)

    if verbosity > 0:
      print("{}:Pass1 got formatted xslt_str2, len='{}'".format(me,len(xslt_str2)))

    try:
        # Create tree_xslt from the xslt_str2
        tree_xslt = etree.fromstring(xslt_str2)
    except Exception as e:
        msg = ("Parse error='{}' etree.fromstring(xslt_str2), description='{}',xslt_str2='{}'. Skipping"
              .format(repr(e), description, xslt_str2))
        print(msg)
        d_return['failure_message'] = msg
        return d_return

    try:
        # Make this into an xsl_transform method designed to do an xslt transform for the tree_xslt
        xsl_transform = etree.XSLT(tree_xslt)

    except Exception as e:
        print("Got exception={}".format(repr(e)))
        print("Using xslt_str='{}'".format(xslt_str))
        raise e

    #----------------------------------------------------------------------------------- #
    # Pass 2 or transformation 2 - to produce tree_result_doc

    # Use the xsl_transform method to convert the given node_root_input to
    # tree_result_doc here the xslt functionality is used to insert some
    # scalar values into the tree_result_doc from the input doc.
    tree_result_doc = xsl_transform(node_root_input)
    #----------------------------------------------------------------------------------- #

    # Translate tree_result_doc back to a string that should still contain the
    # python formatted variable syntax and format it with d_sobek values to a
    # result string for the article mets file.
    # Make a sha1 hash on the result_format_str (with the python variable names,
    # not values in the text)
    # so we will not get a 'false alarm' on a change for timestamps and other
    # sobek values.
    # NOTE: lxml etee.tostring is a MISNOMER, it returns bytes, not a string,
    # unless encoding_method is set to 'UNICODE'.
    # But only a string has the format() method, which we need a few code
    # lines below.

    result1_bytes = etree.tostring(
        tree_result_doc, pretty_print=True, xml_declaration=True)

    # Start setting up some d_sobek_vary values that may 'vary' freely (as
    # opposed to track variables) from harvest to harvest for an item without
    # our wanting to ingest the record again on account of their uninteresting changes.
    sha1_mets = hashlib.sha1()
    sha1_mets.update(result1_bytes)
    sha1_hexdigest = sha1_mets.hexdigest()
    d_return['sha1_hash'] = sha1_mets.hexdigest()
    d_sobek_vary['sha1-mets-v1'] = sha1_hexdigest.upper()

    # Decode the utf-8 bytes back to normal python3 string (default output
    # encoding after a decode() call is python3 string encoding( unicode),
    # so we can later use format method
    result1_str = result1_bytes.decode("utf-8")

    # In results2_str , we will use format() to insert d_sobek_track variable values, so now before we do
    # that result1 str, if printed, will reveal the d_sobek_vary variable names appearing, as in: {last_mod_date}
    # print("Using format(**d_sobek_vary) on result1_str='{}'".format(result1_str))
    #-----------------------------------------------------------------------------------#
    # Now, do final 'pass3' to insert 'vary' variable values into the final rendition suitable
    # for outputting, in result2_str_formatted.
    #-----------------------------------------------------------------------------------#

    try:
        str_mets = result1_str.format(**d_sobek_vary)
    except Exception as e:
        print("result1_str='{}' produced a format error with **d_sobek_vary!".format(result1_str))
        raise e

    if verbosity > 0:
      print("{}: returning str_mets with len={}".format(me,len(str_mets)))
    d_return['str_mets'] = str_mets
    return d_return

#end def xslt_transform_format2()
'''
Method: def article_xml_to_mets_file(source=None, xslt_format_str=None,
    input_file_name=None,
    out_dir_root=None, d_sobek_track=None, d_sobek_vary=None,
    only_oac=False, verbosity=0):

SYNOPSIS: Read an Elsevier input xml file, and if checks pass, create an output METS file.

Arguments:
---------------
-source: the source key name of the xslt initial template in the template dictionary
-input_file_name: used only to construct the METS output file name

(1) Read an elsevier input xml file into the variable input_xml_str
(2) and convert it to a tree input_doc using etree.fromstring,
(3) and convert node_root_input to tree_result_doc
(4) and convert tree_result_doc to result_xmlstr and output it to a new mets output file
    for SobekCM Builder to process.
(5) and create a hash for the new METS file based on its content EXCEPT for values that may change
    like timestamps.

    We don't really need to slow down loading just to update timestamps in METS files if no tracked
    values changed because only their changes are important to track.

Returns d_return{}, with keys and values:
--------------------------------------
* 'log_messages': misc messages

* 'sha1_hash': calculated hash value for outputted METS file or None on failure

* 'failure_message' keys and paraphrased values subject to tweaking:
  '' : if success, otherwise see below
  'api_results_none': if the api fails to provide results
  'api_bad_syntax': if api results cannot be parsed as xml
  'No UF authors':  if article has no UF authors
  'No tracked changes' : if article results have no new Sobek-tracked important changes

  IMPORTANT NOTE:
    If caller receives a failure_message that is not NONE
      No METS file has been created for the article, and no bibvid should be reserved for it.
      SO - the caller should not call pii_reservations.reserve_by_pii() for the article
      for the pii after this method returns. Because we use SobekCM production as the authority of
      pii-bibvid associations, and we will not be trying to load this pii. Complying with this rule
      is not strictly necessary, but it will help to limit the number of 'gaps' in unused bibids in
      production until we change the pii_reservations method x to calculate the next candidate bib.

'''
def article_xml_to_mets_file(source=None, xslt_format_str=None,
    input_file_name=None,
    core_pii=None, #Caller-supplied PII value gleans from the input file's name
    out_dir_root=None, d_sobek_track=None, d_sobek_vary=None,
    only_oac=False, stored_sha1_hexdigest=None, bibvid=None, verbosity=0):

    me="article_xml_to_mets_file"
    #print('{}: using input_file_name={}'.format(me,input_file_name))

    # Return value is tuple of the following three variables. Initialize them.
    log_messages = []
    sha1_mets = None
    mets_failure = None
    d_return = {}
    d_return={'failure_message':'', 'log_messages':'', 'sha1_hash':'' }

    if not all([d_sobek_track, input_file_name, out_dir_root, xslt_format_str,
            d_sobek_vary, source, bibvid]):
        raise ValueError("{}: Bad arguments.".format(me))

    input_file_basename = input_file_name.split('\\')[-1]

    msg = "{}:using input_file_basename={}".format(me,input_file_basename)
    print(msg)
    sys.stdout.flush

    uf_bibid = bibvid[0:10]
    # We ignore the 10th character, the '_'
    vid = bibvid[11:]

    d_sobek_track.update({
          'objid' : bibvid
        , 'bibid' : uf_bibid
        , 'vid'   : vid
        , 'input_file_name': input_file_name
        # , 'tickler': 'sha1-mets-v1'
        })

    # (1) Read an Elsevier article's input xml file to variable input_xml_str
    # correcting newlines and quadrupling up on curlies so later when format()
    # converts two to one, in two separate passes, each { and } will be properly
    # preserved in the output.

    with open (str(input_file_name), "r") as input_file:
        input_xml_str = input_file.read().replace('\n','').replace('{', '{{{{').replace('}', '}}}}')

    # return early if the input file had a <failure> sentinel value, planted
    # by precursor program ealdxml()
    #
    # RETURN on (1) FAILURE to retrieve full text
    if input_xml_str[0:9] == '<failure>':
        msg =("Input_file_name={}, full API retrieval was a '<failure>', with bibid={}"
             .format(input_file_name,uf_bibid))
        log_messages.append(msg)
        print("{}:{}".format(me,msg))
        sys.stdout.flush
        d_return['failure_message'] = ('{}:Input xml file {} shows Elsevier full-text '
            'retrieval by ealdxml failed. Skipping.'.format(me,input_file_name))
        d_return['log_messages'] = log_messages
        return d_return

    # (2) and parse input_xml_str to an lxml tree with root node being node_root_input

    try:
        node_root_input = etree.fromstring(input_xml_str)
        #print("Got node_root_input with tag='{}'".format(node_root_input.tag))
    except Exception as e:
        log_msg = (
            "Skipping exception='{}' in etree.fromstring failure for input_file_name={}"
            .format(repr(e),input_file_name))
        log_messages.append(log_msg)
        d_return['failure_message'] = ("{}:XML Parse failed for input_file '{}'"
            .format(me,input_file_name))
        d_return['log_messages'] = log_messages
        return d_return

    # Create d_ns - dictionary of namespace key or abbreviation name to namespace 'long name' values.
    d_ns = {key:value for key,value in dict(node_root_input.nsmap).items() if key is not None}

    '''
    # Call xslt_transform_format to generate a mets file and a sha1 hash for
    # the xml-based values

    # Creation of a mets file still might be advisable for input to the SobekCM builder's inbound folder
    # (STEP 3) and convert node_root_input to tree_result_doc using xslt transform

    # CHANGE -- NOW also try full xslt and source files
    #print('***** Getting xslt string augmented with default python print formatting variables')

    #print ("For input_file={} using xslt for API source = {}".format(input_file_name,source))
    #############################
    # xslt_transform_until_20160623
    # given an input xml document and xslt_format_string, and d_sobek,
    # (1) compute a sha1_mets hash of the transformed document before filling in the
    #     d_sobek formatting variables
    # (2) compute the final tree_result_doc by filling in the d_sobek variable values
    # return sha1_mets hash and the tree_result_doc

    # NOTE: HERE, before formatting the results, we can compute a 'hash' value for updating.

    # But note if we change any xslt output variable name or anything, even a space at the
    # end of a line in the xslt,
    # then the hash will be be re-computed even with same input from Elsevier on
    # a subsequent run of this program.
    #
    # We want to register a change of article metadata if we change a variable,
    # eg to get title from a different input
    # title element, but we do not want to change any constant output, not even insert
    # a comma or space anywhere, unless required by UFDC, else the hash will
    # change and be used to warrent a re-upload of the METS file to UFDC.
    # But this does not detect changes in the xslt transform itself, which we want to detect,
    # so move this calculatonto be made withn xslt_transform after an xslt transform,
    # but before the d_sobek parameter substitution that includes timestamps
    #print("\nInput filename={}, calling xslt_transform_format...".format(input_file_name))

    #sha1_hexdigest, result_mets_str, node_rawtext, mets_failure = xslt_transform_format(
    '''
    d_results = xslt_transform_format2(core_pii=core_pii
        ,node_root_input=node_root_input, d_ns=d_ns, xslt_format_str=xslt_format_str
        , d_sobek_track=d_sobek_track, d_sobek_vary=d_sobek_vary)

    # Act on special return values
    sha1_hash =  d_results['sha1_hash']
    result_mets_str = d_results['str_mets']
    node_rawtext = d_results['node_rawtext']
    failure_message = d_results['failure_message']

    d_return['failure_message'] = failure_message
    d_return['sha1_hash'] =  sha1_hash

    if sha1_hash == '' or  failure_message != '':
        # This sentinel value means that this xml file had no uf authors
        d_return['log_messages'] = log_messages
        return d_return

    # 20161222- If argument of base_sha1_hexdigest is given, and the same as sha1_hexdigest,
    # we do not output a new mets file.
    #stored_sha1_hexdigest = pii_reservations['stored_sha1_hexdigest']
    if (stored_sha1_hexdigest):
        # SobekCM has a current pii-matching item with a PII, so see if this record's
        # hash matches. If so, no need to create a METS and reload it.
        if (sha1_hash.upper() == stored_sha1_hexdigest.upper()):
            # This is not new info for this bibvid METS file, so call it a
            # failure (to generate new METS file)
            failure_message = ("No change in_sha1 hash, so not making a METS file")
            log_messages.append(failure_message)
            d_return['log_messages'] = log_messages
            d_return['failure_message'] = failure_message
            return d_return

    # Now PROCEED to output the new mets file for loading into SobekCM
    print("{}:Bibvid={}, Writing METS: Different new hexdigest='{}', old='{}'"
        .format(me,bibvid, sha1_hash, stored_sha1_hexdigest))

    if node_rawtext is None:
        msg = ("{}: WARNING: Serial xml file '{}' has no FULL text"
             .format(me,input_file_name))
        print(msg)
        log_messages.append(msg)
        print(msg)
    else:
      if verbosity > 0:
        print("{}: using node_rawtext={}".format(me,node_rawtext))

    if verbosity > 0:
        # Report the article's hexdigest hash value
        log_messages.append(
          "INFO:Article bibid={} has sha1_hexdigest={}"
          .format(str(uf_bibid),sha1_hash))

    # Create METS output directory root if it does not exist
    # The SobekCM Builder, which is meant to consume this output file, seems to prefer (works faster)
    # if you put the xml file into its own directory also named by the bib_vid.
    # Rather, just named by the bib is adequate.
    # out_dir_bib = '{}/{}_{}'.format(out_dir_root, uf_bibid, vid)
    out_dir_bib = '{}/{}_{}'.format(out_dir_root, uf_bibid,vid)

    out_bib_fn = '{}/{}_{}.mets.xml'.format(out_dir_bib, uf_bibid, vid)
    os.makedirs(out_dir_bib, exist_ok=True)
    out_bib_txt = '{}/{}_{}.txt'.format(out_dir_bib, uf_bibid, vid)

    ### OUTPUT THE bib's METS.XML FILE
    #log_message.append("Outputting bib's mets info to filename {}".format(out_bib_fn))
    with open(out_bib_fn, 'wb') as fwb_bib:
        # Write with bytes to encode to utf-8
        fwb_bib.write((result_mets_str.encode('utf-8')))

    #OUTPUT a .txt file of test_bytes, the FULL-TEXT to be indexed by SOLR but
    #intentionally not read-accessible via the mets file, per agreement with Elsevier
    text_bytes = b''

    for xpath in ['.//ce:title', './/prism:teaser', './/dc:description',
        './/ce:abstract', './/xocs:srctitle', './/dc:title'
        ]:
        node_text = node_root_input.find(xpath, namespaces=d_ns)
        if node_text is not None:
            text_bytes += '   ---   '.encode('UTF-8')
            text_bytes += xpath.encode('UTF-8')
            text_bytes += '   ---   '.encode('UTF-8')
            text_bytes += etree.tostring(node_text, encoding='UTF-8', method='text')

    node_text = node_root_input.find('.//xocs:rawtext', namespaces=d_ns)
    if node_text is None:
        # if no fulltext,
        xpath = ".//{*}body"
        #print("Looking for FULLTEXT AT xpath='{}'".format(xpath))
        node_text = node_root_input.find(xpath, namespaces=d_ns)
    if node_text is not None:
        text_bytes += '   ---   '.encode('UTF-8')
        text_bytes += b'BODY   ---   '
        # RVP - next was node_rawtext...
        text_bytes += etree.tostring(node_rawtext, encoding='UTF-8', method='text')

    if text_bytes != b'' :
        #output the rawtext to accompanying text file.
        #Note: If rawtext exists, the generated mets file already references it.
        #print("writing text_bytes len={} to file {}".format(len(text_bytes), out_bib_txt))
        with open(out_bib_txt, 'wb') as fwb_txt:
            fwb_txt.write(text_bytes)
    # Confirm or reserve this pii to bibvid

    d_return['log_message'] = log_messages
    return d_return

# end def article_xml_to_mets_file()

'''
Method articles_xml_to_mets() -

Transform each article file named in input_file_paths to a new SobekCM-Inbound-Folder-friendly
mets output file and write it to output_folder.

Given Arguments:
  - source: a keyword like 'tested' used to access a particular xslt template
      to help generate METS files
  - xslt_format_str: a template salted with both xsl variables and python variables,
      to be filled in via an xslt-fill-in pass and a python variable fill-in pass
  - input_file_paths: list of all xml paths of input files to try to convert to METS output
  - output_folder: filesystem string name of the output folder to use
  - pii_reservations: the PiiReservations object to maintain the pii-bibvid official realtionship in UFDC
  - skip_extant: True means to NOT even generate output METS files if the pii is already in d_pii_bibvid.
      That is to test limited new features of this program. Normally it is false, to allow/support
      updates for mets files for known PII articles.
  - skip_nonserial: True means to not generate mets files for 'nonserial' items. Experience has found
      that Elsevier xml files that show the article is 'nonserial', which we do not need in UFDC, always
      have a pii value that starts with 'B', so we use that to skip over nonserial items that the Elsevier
      API also gives to us. We could change eatxml to not produce these, but who know whether one day we
      will want them?
      We should leave this at True until such time comes when we want nonserial items too.
  - verbosity: used in development mostly to temporarily adjust outputting of misc print messages.

Return Values:
'''
def articles_xml_to_mets(source=None
    , xslt_format_str=None
    , input_file_paths=None
    , output_folder=None
    , pii_reservations=None
    , skip_extant=False
    , skip_nonserial=True
    , verbosity=0):
    me = "articles_xml_to_mets"

    for i,arg in enumerate([source, output_folder, input_file_paths
        ,skip_extant, pii_reservations, xslt_format_str], start=1):
        if arg is None:
            msg = "{}:arg number {} is None. Bad. No soup for you!".format(me,i)
            raise ValueError(msg)

    log_messages = []

    print("{}:processing {} input file paths".format(me,len(input_file_paths)))

    # Set some  sobek dictionary values.
    # For 'd_sobek_track' entries, the sha1 hexdigest value will change if any of these values change.
    d_sobek_track, d_sobek_vary = get_sobek_dicts(
         source_statement_code='Elsevier'
        ,publisher='Elsevier, B. V.')

    #msg = "{}:Got arg skip_extant='{}'".format(me, repr(skip_extant))

    # Future: may pass separate dictionaries downstream, but combine here now
    log_messages.append({'sobek-future-changes-to-track': dict(d_sobek_track)})
    log_messages.append({'sobek-future-changes-to-ignore': dict(d_sobek_vary)})

    vid_int = 1 # Now a normal Elsevier-item new vid_int is 00001, but a stored one may be different.
    max_files_processed = 0

    outputted = 0
    skip_reads = 0
    skip_mets = 0
    skip_dups = 0
    skip_nonserials = 0
    processing_messages = []
    total_mets_failures = 0
    debug_file = sys.stdout
    bibid_type=''
    bibvid=''

    for i, path in enumerate(input_file_paths):
        input_base_name = path.name
        input_file_name = "{}\{}".format(path.parents[0], path.name)

        if (max_files_processed > 0) and ( i >= max_files_processed):
            log_messages.append(
                "Max of {} files processed. Breaking.".format(i))
            break;

        x_msg = ("Processing file count={}, name='{}'.\n"
              .format(str(i),input_file_name))

        #print(x_msg, file=debug_file)

        if verbosity and (i % 10 == 0 and i > 0):
            file_sample = 1
        else:
            file_sample = 0
        if (file_sample):
            # print debug or simple progress-monitoring message to debug_file
            utc_now = datetime.datetime.utcnow()
            utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")
            msg =("{}: time {}: Processed {} input files so far.\n".format(me,utc_secs_z,i))
            print(msg, file=debug_file)

        #print ("exoldmets(): Using input filename='{}'".format(input_file_name))
        # Get pii from filename like: pii_the-pii-value.xml or entry_the-pii-value.xml
        dot_parts = input_base_name.split('.')
        bar_parts = dot_parts[0].split('_')
        pii = bar_parts[1].upper()

        if pii.startswith('B') and skip_nonserial == True:
            msg=("Skipping this file. First PII letter 'B' means nonserial. pii='{}'\n"
                 .format(pii))
            print(msg,file=debug_file)
            x_msg += msg
            skip_nonserial += 1
            log_messages.append(x_msg)
            continue

        # Determine whether UFDC already has this PII
        reservation = pii_reservations.d_pii_reservation.get(pii,None)
        stored_sha1_hexdigest = None
        bibvid = None
        if reservation:
            # pii was already found in the dictionary of production pii values
            skip_dups += 1
            if skip_extant == True:
                x_msg += ("Skip this file. It has extant pii='{}'\n".format(pii))
                log_messages.append(x_msg)
                continue
            else:
                # print("{}: Not skipping the extant pii='{}'".format(me, pii), file=debug_file)
                pass
            bibid_type = 'OLD'
            bibvid = reservation['bibvid']
            stored_sha1_hexdigest = str(reservation['stored_sha1_hexdigest']).lower()
        # end if reservation...
        else:
            # This is a new article/pii that may need to reserve a bib, if METS file creation goes OK.
            bibid_type = 'new'
            # Note: This is a new bibvid because the if-condition catches old ones
            bibvid = pii_reservations.bibvid_available_for_pii(pii)
        # end else

        msg = ("For pii='{}' considering a reservation for {} bibvid={}\n"
              .format(pii, bibid_type, bibvid))
        # print(msg, file=debug_file)
        x_msg += msg

        # Try to read the article's xml input file.
        with open (str(input_file_name), "r") as input_file:
            try:
                input_xml_str = input_file.read().replace('\n','')
                # print("### Got input_xml_str={}".format(input_xml_str))
            except Exception as e:
                msg = ("Skipping READ FAILURE='{}' for input_file_name={}\n"
                        .format(e, input_file_name))
                x_msg += msg
                log_messages.append(x_msg)
                skip_reads += 1
                continue

        # Try to create mets.xml output for the input article
        d_results = article_xml_to_mets_file(source=source
            , xslt_format_str=xslt_format_str
            , core_pii=pii #pii in filename (orig from dublin core pii xml tag)
            , input_file_name=input_file_name
            , out_dir_root=output_folder
            , d_sobek_track=d_sobek_track
            , d_sobek_vary=d_sobek_vary
            , stored_sha1_hexdigest=stored_sha1_hexdigest
            , bibvid=bibvid
            , verbosity=verbosity
            )
        article_xml_log_messages = d_results['log_messages']
        if len(article_xml_log_messages)>0:
            log_messages.append({'article-xml-to-mets':article_xml_log_messages})

        failure_message = d_results['failure_message']
        if failure_message != '':
            # This is a FAILURE to build a METS file for this PII, so we will continue
            # to the top of this loop so that we do not reserve (a bibvid for) the PII.
            # No mets file could be generated this time.
            msg = ("For this input file's PII {}, did not make METS file. "
                 "{}. Bibvid {} is still unused.\n"
                  .format(pii,failure_message,bibvid))
            x_msg += msg + failure_message
            skip_mets += 1
            log_messages.append(x_msg)
            continue

        # Here, we succeeded to output a hopefully good METS file for this pii,
        # so check or set the reservation

        msg = ("Input file={}, trying reservation for{} pii = {} for bibvid={}"
              .format(input_file_name, bibid_type,pii,bibvid))
        pii_reservations.reserve_for_pii(pii=pii)

        if verbosity > 0 and 1 == 2:
            msg = ( "Good input: file[{}]={}, pii={}, {}, bibvid={}, with hexdigest={}. \n"
                .format(i+1, input_file_name, pii
                ,bibid_type ,bibvid, sha1_hexdigest))
            # log_messages.append(msg)
            print(msg)

        msg = ("{}:SUCCEEDED to make new mets file {}...{} for pii={} with bibivid={}"
               .format(me,output_folder,outputted,pii,bibvid))
        outputted += 1
        x_msg += msg
        # Append to xml log the message(s) for processing this input file.
        log_messages.append(x_msg)
    #end for i, fname in input_file_paths

    d_statistics = {
          "input-files-count": str(i)
        , "skipped_dups": skip_dups
        , "skipped_reads" : skip_reads
        , "skipped_mets" : skip_mets
        , "output-mets-files-count": outputted
    }
    log_messages.append({"statistics": d_statistics})

    return log_messages, bibvid
# end def articles_xml_to_mets

'''
Object pii_reservation manages all pii to bibvid associations known to the SobekCM source
system during exoldmets processing.

The SobekCM source system is probably always the official UFDC SobekCM Database,
the UF production system, and confined to bibvids of Elsevier bibs (the bibroot value
in SobekCM is 'LS' - per verbal agreement with UF DPS in 2015) because now only
Elsevier loads maintain a hash hexdigest value in the SobekCM_Item.Tickler column,
which is a critical requirement to operation of this object.
'''
class PiiReservations(object):
    '''
    Method __init__(self, d_pii_reservation):

    Arguments:
    - d_pii_reservation:
      This is a dictionary with key of pii value of an Elsevier article or bib item
      id, such as 'LS00123456_0002',
      and the value is a dictionary with the following required key:values.
        -- deleted: value is 0 or 1 from the Sobek Database SobekCM_Item.deleted value
        -- bibvid: value is the current SobekCM bibid, eg ("LS005123456_00001") that is
           used for the pii value.
        --bibid: format is LS8
        -- pii: the pii value of this entry, corresponding to a unique Elsevier article.
    - data members:
      -- bibroot: set to 'LS' - may later accept argument value
    '''
    def __init__(self, d_pii_reservation, verbosity=0):
        me = "PiiReservations.__init__"

        self.d_pii_reservation = d_pii_reservation
        # maybe set bibroot by argument when support generic bibroots.
        self.bibroot='LS'
        bib_low_int_dex = len(self.bibroot)
        self.d_bib_reservation = OrderedDict()
        self.d_pii_reservation = OrderedDict()
        self.max_bibint = -1
        self.bib_dup_count = 0
        self.bib_new_count = 0

        # Create entries for inverse dictionary using bibvid as the key, value is reservation
        for pii, reservation in d_pii_reservation.items():
            deleted = reservation['deleted']
            bibvid = reservation['bibvid']

            reservation = self.add_pii_reservation(pii, reservation)
            if not reservation:
                print("{}:Could not add reservation for pii={}. It already exists. Skipping."
                     .format(me,pii))
                continue
            # -
            bibint = int(bibvid[bib_low_int_dex:bib_low_int_dex+8])
            if bibint > self.max_bibint:
                self.max_bibint = bibint
            reservation['pii'] = pii # If already present, just silently overwrite pii

            if self.d_bib_reservation.get(bibvid, None) is not None:
                # Consider to: Allow duplicate bibvids only if they are
                # marked as deleted in source system.
                # for now let them go here. Another process can detect and clean
                # them.
                if str(deleted) == '0':
                    self.bib_dup_count += 1
                    # Just print a verbose warning message here...
                    if verbosity > 0:
                        msg = (
                            "{}:Source bib '{}' is already in UFDC."
                            .format(me,bibvid))
                        print(msg)
            else:
                # Add entry to 'inverse' bibvid-keyed dictionary of pii reservations
                self.bib_new_count += 1
                self.d_bib_reservation[bibvid] = reservation

        # end: for each d_pii_reservation item

        self.d_bib_reservation = OrderedDict(sorted(self.d_bib_reservation.items()))
        # Simple algo for now: set the next candidate bibid_next
        # Can improve on this method because this way ignores gaps in lower bibids, though.
        self.bibint_next = str(self.max_bibint +1)

        self.bibvid_next = "{}{}_00001".format(self.bibroot,str(self.bibint_next).zfill(8))

        # Can add code here later, if needed to set up a list of bibvid 'gaps', of unusued
        # bibvids, or at least the first one. As new bibvids are needed, an algo can use
        # some variables to manage finding the next bibvid more efficiently, that is, to not
        # skip over lower-integer-numbered bibvids that are available to use... if any...
        # First cut - just always find the highest bibvid and keep track of the next unused
        # one in integer order.

        return
    #end def __init__

    '''
    Method def enforce_valid_bibvid(self, bibvid=None):

    Check validity of given bibvid.

    Raise fatal error on invalid bibvid.
    If it is fine, and its value exceeds self.max_bibint, update self.max_bibint
    and self.bibvid_next.
    '''
    def enforce_valid_bibvid(self, bibvid=None):
        if bibvid is None:
            raise ValueError("Bibvid is not given.")
        if not bibvid.startswith(self.bibroot):
            raise ValueError("Bad bibvid='{}' does not start with {}".format(bibvid, self.bibroot))
        #reservation['bibvid'] = bibvid
        parts = bibvid.split('_')
        bib = parts[0]
        len_p0 = len(self.bibroot) + 8
        if len(parts) == 1:
            vid = '00001'
        else:
            #assume len is > 1 and parts[1] has the vid
            vid = parts[1]

        if len(parts[0]) != len_p0 or len(vid) != 5 or int(vid) != 1:
            raise ValueError("Bibvid='{}' in invalid format.".format(bibvid))
        bibint = int(bib[len(self.bibroot):len_p0])
        if bibint > self.max_bibint:
            self.max_bibint = bibint
            self.bibvid_next = "{}{}_00001".format(self.bibroot, str(bibint +1).zfill(8))
        return bibvid
    # end enforce_valid_bibvid
    '''
    Method add_pii_reservation():

    Context/Role:
    (1) Called by __init__, which scans a given dictionary of registered
    pii-bibvid pairings.
    (2) also called by reserve_for_pii()

    Synopsis:

    Register a reservation for the given pii and reservation params.
    If the pii value is already stored, this is a fatal error.
    If the reservation bibvid key is absent or has a bad value, this is a fatal error.

    Given Arguments:

    - pii: pii string value of a pii that has no standing reservation. (It has no presence in SobekDB).
    - reservation: a dictionary with:

        KEY                   : VALUE
        bibvid (required key) : bibvid that is associated with the pii
        deleted (optional)    : defaults to '0' to mean the pii is not registered
                                as deleted from SobekCM database. Might later be used for...?

    Returns:
    - reservation: None?
    - future? the reservation that was taken for this pii


    20161020 ideas - Processing:

      If the bibint of the given
      bibvid is the biggest one so far reserved, store it as self.bibint_max, and also
      construct and set up next_bibvid value, for callers future convenience to announce a new
      available bibvid for the reservation for a new pii.

      IMPORTANT: This method should not be called until a METS file has been successfully generated,
      for this pii, in order to not skip over unused bibints in the available/unused set of
      bibints for a bibvid, using the simplistic algorithm used by __init__ that simply finds the
      highest used bibint and stores it so a caller can use that to increment it and find a 'safe'
      unusued bibint to put in the reservation['bibvid'] value.

      Arguments:
      - pii: a unique new pii for an article for which no reservation yet exists
      - reservation: a dictionary with keys:
        -- bibvid: value is formatted as LS, 8-digit bibint, _, then 5 digit zero filled vid,
           which is always 00001 for Elsevier bibvids.
           Note: if the bibvid key is missing or its value does not conform to that of a bibvid, then
           (a) this method will set key 'bibvid' value to self.next_bibvid.
           (better) this method raises an error
        Notes:
        -- any other reservation dictionary keys and their values are ignored.
        -- any key 'deleted' is overwritten and its value is set to '0'.
        -- any key 'status' is overwritten and its value is set to 'proposed'


      The caller will normally have for the key reservation['bibvid'] set its value either by:

      (1) reading the inital set of reservations from SobekCM production,
          each with pii and bib and optional key 'deleted'
          from the sobekCM production database, where reserved['status'] will be 'made', or
      (2) the caller proposing a new reservation for a pii by its surmising an available bib,
          which it might surmise from the pii_reservations.max_bibint and adding 1 (or in the future by
          calling a pii_reservations.xxx() method to propose one)
      (3) Not setting reservation['bibvid'] at all, thus defaulting to the default self.next_bibvid


      NOTES:

      ---------- revise below later --------

      Also see method cancel_bib_by_pii, which the caller can use to cancel a proposed bib reservation.
      IMPORTANT NOTE: If the METS file is rejected by the builder or not submitted,
      the mets file should probably be destroyed, or at least be set aside and made obsolete,
      because the next run of exoldmets might assign a different bibvid value for the pii.

      IN OTHER WORDS - We must do the following:
      Run exoldmets and either (1) submit its output mets files to the builder once and never again
      or (2) never submit them to the builder - just examine them perhaps for testing and then destroy
      them to prevent accidental future submission to the builder.

      So, reservations for pii-bibvid bindings are only 'taken' by the caller (exoldmets) - set forth in
      its output METS files, but the reservations are not 'made' until the Builder accepts them.
      Then the pii-bibvid association is permanently stored in the SobekCM database (the PII is part
      of the database SobekCM_Item.link value and the Bibvid is stored in SobekCM_Item and SobekCM_Item_Group).

      The pii to bibvid assocation is only ever made permanent in SobekCM when the builder accepts
      a mets file with the pii-bibvid association.

      The design decision was to avoid a lifetime of
      over-complexity and so to NOT store and maintain a
      separate pii-bibvid data relationship external to SobkeCM, letting the SobekCM target system always
      be the authoritative source of the pii-bibvid 'permanent' relationship. However, the trade-off is there
      is a risk that old outputs of exoldmets METS files laying around may contain incorrect pii-bibvid
      associations, and so should never be loaded into SobekCM.

      Once a 'builder loader manager' is incorporated at the end of an atomic ealdxml-exoldmets-eloadmanager
      chain is in place, then that will limit human error of depositing obsolete METS files into the builder.

    '''
    def add_pii_reservation(self, pii=None, reservation=None):
        me = "add_pii_reservation"
        if pii is None or reservation is None:
            raise ValueError("pii or reservation is not given.")

        reservation_used = self.d_pii_reservation.get(pii,None)
        if reservation_used and int(reservation_used['deleted']) == 0:
            # Cannot provide a new reservation for a known used pii. Fatal error.
            #print("{}:pii='{}' already has a non-deleted reservation.".format(me, pii))
            return None

        # Enforce use of a valid bibvid
        bibvid = reservation.get('bibvid', None)

        # Note: enforce_valid_bibvid() also sets self.max_bibint, bibvid next as needed
        reservation['bibvid'] = self.enforce_valid_bibvid(bibvid)

        # Default for 'deleted' is 0
        if not reservation.get('deleted', None):
            reservation['deleted'] = 0

        # As a 'service' set  or overwrite given reservation pii.
        reservation['pii'] = pii

        #print("Making reservation for pii = {}, bibvid={}".format(pii, bibvid))

        # Register new reservation in d_pii_reservation
        self.d_pii_reservation[pii] = reservation

        # Set bibvid dictionary key's value to the reservation too.
        self.d_bib_reservation[bibvid] = reservation

        return reservation
    # end def add_pii_reservation()

    '''
    Method reserve_for_pii

    Synopsis:
    For given pii,
    (1) if the pii is new, OR if it is not new, but the deleted flag is set,
        make and return a reservation using self.bibvid_next,
    (2) if the pii is not new and the deleted flag is not set, just return its current reservation

    Argument: pii

    Return: the reservation object for given pii
    '''
    def reserve_for_pii(self, pii=None):
        if not pii:
            ValueError("pii not given")

        reservation = self.d_pii_reservation.get('pii', None)
        if reservation is not None and int(reservation['deleted']) == 0:
            return reservation
        # Note - if a prior bibvid was deleted for this pii, we allow a new bibvid
        # to be assigned for it.

        reservation = {}
        reservation['bibvid'] = self.enforce_valid_bibvid(self.bibvid_next)
        reservation = self.add_pii_reservation(pii, reservation)

        return reservation

    def get_reservation_by_pii(self, pii=None):
        if pii is None:
            raise ValueError("Required argument pii was not given")
        return self.d_pii_reservation.get(pii, None)
    # end def reservation_by_pii()

    '''
    Method def bibvid_available_for_pii
    Given a pii value

    Return the assigned bibvid if the pii has a reserved bibvid, else return
    bibvid_next as an available bibvid for the caller to use to make a
    reservation for this pii.

    NOTE: if this is called twice for two different new piis, and there was NOT
    an intervening call to reserve_by_pii() for the first given pii, then the
    second call to this method for the second pii will get the same available
    bibvid value.
    In other words, the caller must reserve the available bibvid for a new pii before
    asking for another available bibvid for another pii, or the same available bibvid
    will be returned, which will probably lead to unwanted results.

    '''
    def bibvid_available_for_pii(self, pii=None):
        if pii is None:
            raise ValueError("Required argument pii was not given")
        reservation = self.d_pii_reservation.get(pii,None)
        if reservation:
            # For known pii, just return its current bibvid
            bibvid = reservation['bibvid']
        else:
            # The pii has no reservation yet, so return the next avilable bibvid.
            bibvid = self.bibvid_next
        return bibvid

    #end def bibvid_for_pii
# end class PiiReservations

'''
Method get_pii_reservations_from_marshaldb():

Also See below PREREQUISITES:

Arguments:

- engine_ufdc and table_ufdc:
  The SqlALchemy engine and table object for a table with the expected columns:
  bibvid, pii, tickler, is_deleted.

  The rows are assumed to include one for every Elsevier article item known
  in the UFDC/SobekCm database.
  The bibvid is required to be be a unique key, but PII values may be duplicated,
  though any dups with the same is_deleted value should probably be resolved, by
  removing all but the 'best' one - a task for another program.


- Processing:
  Instantiate and return a PiiReservations object given the
  UFDC information.

Returns:
- log_messages: dict with various log messages

- pii_reservations: instance of PiiReservations object with the
  pii-bibids currently in use by a SobekCM database.
  -- It will contain:
     -- a dictionary of pii to bibid aka bibvid reservations
     -- and another dict keyed by bibid aka bibvid to reservation objects
     -- a next_bibid member
     -- a last_bib_int value (integer component of the last(highest) used
        bibid aka bibvid found in UFDC)
     -- bibroot: will always be 'LS' for Elsevier

PREREQUISITES:

FIRST: run the python project sobekdb program sobek_item_to_table.py
to copy needed SobekDB item information to the marshal database table
'item_elsevier_ufdc', because that is the expected table name for ufdc
production. Use a different engine or  table name for ufdc integration or local
test environments, as produced by program sobek_item_item_to_table.py when
it is run on either the integration test or a local environment.

No new Elsevier items should be loaded to the UFDC environment after
that program is run until after this program exoldmets is run.

After exoldmets is run, the created METS files in the staging directory
may be loaded safely into the UFDC environment at issue.

For each row, store its  bibvid, pii, is_deleted and tickler values
'''

def get_pii_reservations_from_marshaldb(
    engine_ufdc=None, table_ufdc=None, verbosity=1):

    me = "get_pii_reservations_from_marshaldb"

    conn_ufdc = engine_ufdc.connect()

    rows_item_elsevier_ufdc = (conn_ufdc.execute(select([table_ufdc])
      .where( and_ (
      table_ufdc.c.ufdc_deleted == 0,
      table_ufdc.c.bibvid.like('%LS%'),
      ) ))
    .fetchall())

    od_pii_bibvid = OrderedDict()
    od_pii_reservation = OrderedDict()

    count_deleted = 0
    count_not_deleted = 0
    dup_piis = 0

    bibvid_index = 2
    pii_index = 4
    tickler_index = 5
    deleted_index = 6

    for row in rows_item_elsevier_ufdc:

        bibvid = row['bibvid'] # [:10]
        pii = row['pii'].upper()
        tickler_pack = row['tickler']
        deleted = row['ufdc_deleted']

        # Ticklers are packed into one large value with 'space-pipe-space'
        # delimiters, starting with the delimiter, so the first one is always
        # a throwaway.
        # Also the last one is always the current one to use.
        # Historical ones are traditionally kept in SobekCM
        # for some reason that may be worth reconsidering.
        ticklers = tickler_pack.split('|')
        # Parse the most recent tickler value...still must discard the space
        # characters left over from the legacy delimiter convention.
        # The last tickler is maintained as the stored_sha1_hexdigest,
        # assigned below
        tickler = ticklers[-1].replace(' ','')

        # Check validity of some column values.
        if len(bibvid) > 16:
            msg = ("Error: OOPS got string value too long for a bibvid:'{}'. "
                .format(bibvid))
            raise ValueError(msg)

        # Object reservation exists for each pii, and it has
        # three key-values for keys:
        # (1) bibvid (the bibvid reserved for the pii),
        # (2) deleted (whether UFDC sees this pii's bibvid as deleted),
        # (3) stored_sha1_hexdigest () - the bibvid's METS file's hash code
        reservation = OrderedDict()
        if bibvid in reservation.values():
            msg = ("Error: OOPS duplicate bibvid:'{}'. "
                .format(bibvid))
            raise ValueError(msg)
        reservation['bibvid'] = bibvid

        reservation['deleted'] = deleted
        reservation['stored_sha1_hexdigest'] = tickler.upper()

        # Raise warnings: If pii and deleted == 0 combo value is duplicated
        # it is an error to resolve in the production database.
        if (pii in od_pii_reservation.keys() and str(deleted) == '0'
           and od_pii_reservation[pii]['deleted'] == '0'):
            msg = ("\n***\n{}:Warning: pii={} has dup bibvids={},{}"
                " both with deleted value 0."
                # "Please update the SobekDB data to have at most one row for
                # this pii with deleted=0"
                  .format(me,pii,od_pii_reservation[pii]['bibvid'], bibvid))
            dup_piis += 1
            print(msg)

        if deleted is not None and str(deleted) == '0':
            count_not_deleted += 1
        else:
            count_deleted += 1
        od_pii_reservation[pii] = reservation
    # end for row ...

    conn_ufdc.close()

    if verbosity > (-1) :
        print(
          "{}: Found {} Elsevier bibvids that are not deleted,"
          " {} that are deleted."
          .format(me,  count_not_deleted, count_deleted))

    if dup_piis > 0:
        msg = ("{}:Fatal error. Found {} duplicate pii items (see bibvids listed"
            " above) that are not deleted"
            .format(me,dup_piis))
        print(msg)
        # raise ValueError(msg)
    # Create a PiiReservations object and return it
    # It is designed to containe for a single pii key a reservation object
    # of 3 values.
    # Consider later making the od_pii_reservation value
    # a simple 3-tuple instead  of a dictionary, but it works OK as is.
    return PiiReservations(od_pii_reservation)
#end get_pii_reservations_from_marshaldb

import shutil

# SET more RUN PARAMS AND RUN
def exoldmets_run(env='test', engine_ufdc=None,table_ufdc=None,
    data_elsevier_folder=None, input_folders=None):

    me='exoldmets_run'

    d_log = OrderedDict()
    d_params = OrderedDict()

    # Hard-codes
    xslt_sources = ['full', 'entry', 'tested']
    bibvid_prefix = 'LS'

    print("{}:Running for xml input files under {} input_folders"
      .format(me,len(input_folders)))
    sys.stdout.flush
    # skip_extant=True => don't create new METS file if PII is in ufdc.
    skip_extant = False
    # skip_nonserial=True ==>don't create new METS file if the PII
    # starts with 'B', meaning nonserial, usually a Book
    skip_nonserial = True
    # If skip_pii_new ==> we only want to create METS files for PII values
    # that are already in use by UFDC
    skip_pii_new = True

    utc_now = datetime.datetime.utcnow()

    # Make date formats with utc time aka Zulu time, hence Z suffix.
    # On 20160209, this is the second 'edtf' format on the first bullet at
    # http://www.loc.gov/standards/datetime/, on the download of the PowerPoint
    # Presentation link: http://www.loc.gov/standards/datetime/edtf.pptx
    utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")

    # secsz_start = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")
    # We also use secsz_start as part of a filename, and windows chokes on ':',
    # so use all hyphens for delimiters
    secsz_start = utc_now.strftime("%Y-%m-%dT%H-%M-%SZ")
    secsz_str = utc_now.strftime("%Y-%m-%dT%H-%M-%SZ")

    output_app_folder = '{}output_exoldmets/'.format(data_elsevier_folder)
    output_base_folder = '{}staging/'.format(output_app_folder)
    output_logs_folder = '{}logs/'.format(output_app_folder)

    # NOTE: As we do below, the staging directory and contents must be
    # completely removed to preserve the integrity of new bibvids to be
    # generated on this run.

    # Otherwise, if these files are not all removed, it is possible that
    # filenames lingering here with obsolete bibvids are later used (loaded to ufdc),
    #  If so, those wrong PII values may exist in old bibvids that have not
    # been, for any reason, successfully loaded
    # into the sobekcm databse by the SobekCM Builder.
    # Maybe we forgot to try to load them or we did but the builder was down
    # and did not create good error messages about a failure to load them,
    # Maybe they failed or we did not even try to load them.

    os.makedirs(output_base_folder, exist_ok=True)
    shutil.rmtree(output_base_folder)

    os.makedirs(output_logs_folder, exist_ok=True)

    d_xslt = get_d_xslt()

    # 'tested' is the current best xslt transform to apply.
    xslt_source_name='tested'
    xslt_format_str = d_xslt[xslt_source_name]

    if 1 == 1:
        input_files_low_index  = None
        input_files_high_index = None
        # REVIEW: make sure this db has the most recent bibids before running env of prod
        print("{}: Connecting to SQLEXPRESS database 'silodb'".format(me))
        sys.stdout.flush

        load_selection = 'all_new_or_changed'

    # Object to manage pii to bibvid reserved pairings for METS file outputs.
    # Call with arg prod conn later

    print("{}: Using env={}.".format(me,env))
    sys.stdout.flush

    print("{}: Getting pii reservations...".format(me))
    sys.stdout.flush

    pii_reservations = get_pii_reservations_from_marshaldb(
        engine_ufdc=engine_ufdc, table_ufdc=table_ufdc)

    p = pii_reservations
    print(
      "pii_reservations found {} bibs, {} new, {} in ufdc."
      .format(p.bib_dup_count+p.bib_new_count, p.bib_new_count,
       p.bib_dup_count))

    msg="Early Test exit"
    #raise ValueError(msg)
    sys.stdout.flush

    #pii_reservations = get_pii_reservations_from_silodb()

    print("{}: got the exiting UFDC pii reservations...".format(me))
    #raise Exception("Test EXIT 20161223")

    d_params.update({
         'python-sys-version': sys.version
        ,'secsz-1-start': secsz_start
        ,'output-folder': output_base_folder
        ,'input-folders': repr(input_folders)
        ,'input-xslt-source-dict-key-name': xslt_source_name
        ,'skip_extant': repr(skip_extant)
        ,'skip_nonserial': repr(skip_nonserial)
    })

    d_log['run_parameters'] = d_params

    #log_source_xml_messages = ""
    all_input_file_paths = []
    d_result_counts = {}

    # Loop through the input_folders by year:
    print("Reading pii*xml files from {} input folders"
       .format(len(input_folders)))

    for i, input_folder in enumerate(input_folders):
        # Get list of 'Elsevier FULL-API'-based input files, first few for testing,
        # from 'per-day' folders under output_ealdxml
        input_folder_path = Path(input_folder)

        # TODO: implement a 'builder-feeder' routine that spoonfeeds the mets files to the builder,
        # at a regulated pace so as to not bog down other production work by DPS, Laura Perry and crew.

        input_file_paths = list(input_folder_path.glob('**/pii_*.xml'))

        print("{}: processing {} pii*xml input files under folder {}"
              .format(me, len(input_file_paths), input_folder))
        sys.stdout.flush

        # use ealdxml's filenames
        print("Processing input_folder={} reading {} files that were output by ealdxml."
             .format(repr(input_folder),len(input_file_paths)))
        sys.stdout.flush

        print("{}:calling articles_xml_to_mets for {} files in input folder={} with skip_extant='{}'"
              .format(me, len(input_file_paths), input_folder, repr(skip_extant)))
        sys.stdout.flush

        # Process all input xml files in the input_file_paths
        log_source_xml_messages, bibvid = articles_xml_to_mets(
          source=xslt_source_name
          , xslt_format_str=xslt_format_str
          , input_file_paths=input_file_paths
          , output_folder=output_base_folder
          , pii_reservations=pii_reservations
          , skip_extant=skip_extant
          , skip_nonserial=skip_nonserial
          , verbosity=2
        )
        #log_source_xml_messages += log_source_xml_messages
        input_folder_messages_key = ('input-folder-{}'.format(input_folder)
            .replace(':', '').replace('/','-').replace('\\','-'))

        d_log[input_folder_messages_key ] = log_source_xml_messages
        # Save all input file paths to be returned to caller
        all_input_file_paths.extend(input_file_paths)
    # end loop through input folders

    secsz_finish = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
    d_log['run_parameters'].update({"secsz-2-finish": secsz_finish})

    # Put d_log info into xml tree at e_root
    e_root = etree.Element("uf-exoldmets-xml-to_mets")
    etl.add_subelements(e_root, d_log)

    # Finally, output the d_log's xml tree at e_root.
    log_filename = '{}/{}.xml'.format(output_logs_folder,secsz_str)
    print("{}: writing log_filename='{}".format(me,log_filename))
    with open(log_filename, 'wb') as outfile:
        outfile.write(etree.tostring(e_root, pretty_print=True))
    print("{}: output_folder={}. Now returning...".format(me,output_base_folder))
    return log_filename, all_input_file_paths, pii_reservations
#end def exoldmets_run()


#MAIN  PARAMETER SETTINGS AND RUN

def run():
  #RUN - Create METS files from input...
  #input_subfolders = ['2016','2015','2014','2015','2014','2013','2012']

  # By convention, output of precursor program, ealdxml.py is under the following
  # specified data_relative_folder
  data_elsevier_folder = etl.data_folder(linux='/home/robert/', windows='U:/',
        data_relative_folder='data/elsevier/')

  # Set up temporal folders to search for the ealdxml output, our input xml files, based on the
  # given cymd_start and cymd_end values

  cymd_start = '20090101'
  cymd_start = '20170820'
  cymd_end = '20170824'

  input_folders = []
  input_folder_base = '{}/output_ealdxml/'.format(data_elsevier_folder)
  days = etl.sequence_days(cymd_start, cymd_end)

  for cymd, dt_cymd in days:
    subfolder = ('{}/{}/{}/'.format(cymd[0:4],cymd[4:6],cymd[6:8]))
    print("One subfolder is = '{}'".format(subfolder))
    input_folders.append('{}{}'.format(input_folder_base,subfolder))

  print("Will process files among {} subfolders from {} to {}"
        .format(len(input_folders),cymd_start,cymd_end))
  sys.stdout.flush

    # Select a source of input xml, also a specific  xslt transform is implied
    # see def exoldmets_run and see comments on database info on bibvids.
    # Note: legal envs = ['prod','local','test']

  # Settings for UFDC elsevier item info
  engine_ufdc = get_db_engine_by_name(name='uf_local_mysql_marshal1')
  eumd = MetaData(engine_ufdc)
  table_ufdc = Table('item_elsevier_ufdc', eumd, autoload=True,
      autoload_with=engine_ufdc)

  log_filename, used_input_file_paths, pii_reservations = exoldmets_run(
          engine_ufdc=engine_ufdc,
          table_ufdc=table_ufdc,
          env='test',
          data_elsevier_folder=data_elsevier_folder,
          input_folders=input_folders
  )

  if used_input_file_paths:
      print("Done with exoldmets() using {} input files from {} to {} under{}."
        .format(len(used_input_file_paths),cymd_start,
        cymd_end,data_elsevier_folder))

  print("See logfile={}".format(log_filename))
  utc_now = datetime.datetime.utcnow()
  print ("\nDone at utc_now={}\n".format(utc_now))
  return
#end def run()

# RUN
run()
