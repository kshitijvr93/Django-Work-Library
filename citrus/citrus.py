'''citrus.py

<summary name='citrus.py'>Read METS files for the UFDC citrus collection and
transform to a predefined spreadsheet output format, suitable for manual edits and
submittal to the "Deeply Rooted" project.</summary>

'''

import sys, os, os.path, platform

# Note: expanduser depends on HOME and USERPROFILE vars that may get changed by
# Automatic updates, (this happened to me, causing much angst) so be explicit.
env_var = 'HOME' if platform.system().lower() == 'linux' else 'USERPROFILE'
path_user = os.environ.get(env_var)

print("Using path_user='{}'".format(path_user))
print("Note: HOME variable is '{}'".format(os.environ.get('HOME')))
# For this user, add this project's modules to sys.path
path_modules = '{}/git/citrus/modules'.format(path_user)
print("Using path_modules='{}'".format(path_modules))
sys.path.append(path_modules)

print("\n------------\n------------using sys.path='{}'\n\n".format(sys.path))
print("ABC")
print("TESTEXIT")
sys.stdout.flush()
#raise Exception(ValueError,"TEST EXIT")

import etl

import csv
from pathlib import Path
from lxml import etree
from lxml.etree import tostring
from collections import OrderedDict
import xlrd, xlwt
from xlrd import open_workbook
from etl import FilePaths

class Citrus():

    def __init__(self, paths=None, edits_file=None, input_folders=None, input_path_glob=None
        ,deeply_rooted_output_file_name=None):

        self.input_file_paths = FilePaths(input_folders, input_path_glob).paths
        self.deeply_rooted_output_file_name =  deeply_rooted_output_file_name
        self.description = ('This item has been aggregated as part of the Association of Southeastern'
              + ''' Research Libraries (ASERL)'s "Deeply Rooted: The Agricultural & Rural History of the '''
              + 'American South" project.')
        #The keys of this dictionary double as the header column names to be output
        # to an eventual csv or excel file
        # The values's first tuple indicates constant, or xml (single element) or
        # list (repeated elements)
        # Code cases will rely on the key name to do special processing as well.
        self.d_deeply_source = OrderedDict([
                ('relation', ('list', './/mods:relatedItem' )),
                ('title', ('xml', './/mods:title' )),
                #special conditions for transforming subject data here require subject id and sub-elt topic
                ('subject', ('list', './/mods:subject')),
                ('description', ('xml','.//mods:abstract')),
                ('source', ('xml', './/mods:recordContentSource' )),
                ('publisher', ('xml', './/sobekcm:Publisher' )), #special case/code to extract from this node
                ('coverage_temporal', ('xml', './/sobekcm:Temporal/sobekcm:period' )),
                ('format', ('constant', 'image/jpeg, image/jp2, image/tiff, image/jpeg-thumbnails' )),
                ('identifier', ('xml', './/mods:url' )),
                ('rights', ('xml', './/mods:accessCondition' )),
                ('creator', ('list', './/mods:name' )), # use the  name of creator individual
                ('language', ('xml', './/mods:languageTerm' )),
                ('type', ('xml', './/mods:genre' )),
                ('coverage_spatial', ('xml', './/mods:hierarchicalGeographic' )),
                ('contributor', ('constant', 'University of Florida. Libraries' )),
                ('date', ('xml', './/mods:dateIssued' )),
        ])
        # Ordered Column names for deeply rooted output
        self.l_deeply_output_columns = [
            'relation', 'title', 'subject', 'description', 'source', 'publisher', 'coverage_temporal'
            , 'format', 'identifier', 'rights', 'creator', 'language', 'type', 'coverage_spatial'
            , 'contributor', 'date' ]
        self.d_deeply_output = {} #will be overwritten/reused for each input bib

        # EXCEL WORKBOOK with SPREADSHEET OF EDITS
        book_edits = open_workbook(edits_file, 'r')
        self.book_edits = book_edits
        self.sheet_edits = book_edits.sheet_by_index(0)

        # read dict of column name:index info into key-value pairings
        self.d_colname_colidx = OrderedDict(
            {self.sheet_edits.cell(0,col_index).value :
               col_index for col_index in range(self.sheet_edits.ncols)})
        print("Got edit spreadsheet column names,indexes = {}".format(repr(self.d_colname_colidx)))

        # User OrderedDict to Maintain bib order of original edits spreadsheet
        # Use bibid (in column index 1) as key because no dups are allowed
        self.d_bibid_rowidx = OrderedDict(
            { self.sheet_edits.cell(row, 1).value.upper() : row for row in range(self.sheet_edits.nrows)})

        print("Got {}={} citrus spreadsheet bibs".format(len(self.d_bibid_rowidx), self.sheet_edits.nrows))

        # Pre-agreed period time-era names keyed by with start year
        self.d_year_period = OrderedDict([
            (1920, "Florida Land Boom"),
            (1929, "Great Depression"),
            (1939, "World War II"),
            (1946, "First Cold War"),
            (1954, "Civil Rights"),
            (1969, "Vietnam War"),
            (1976, "Post 1975"),
        ])
        self.outbook_init()
    #end def init

    def period_by_year(self, year=None):
        year = int(year)
        period = "Prehistoric"
        for band_year, band_period in self.d_year_period.items():
            if int(band_year) > year:
                break
            period = band_period
        return period

    def outbook_init(self):
        self.deeply_book = xlwt.Workbook()
        self.deeply_sheet = self.deeply_book.add_sheet("deeply_rooted")
        # Header row
        for col_index,col_name in enumerate(self.l_deeply_output_columns):
            self.deeply_sheet.write(0, col_index, col_name)
        self.outbook_row_index = 1

    def outbook_writerow(self, d_output=None, d_column_style=None):
        column_values = [ d_output[column] for column in self.l_deeply_output_columns]
        for column_index, (column_key, column_value) in enumerate(d_output.items()):
            style = None if d_column_style is None else d_column_style.get(column_key, None)
            if style is None:
                self.deeply_sheet.write(self.outbook_row_index, column_index, column_value.strip())
            else:
                print("Writing a style for column '{}'".format(column_key))
                self.deeply_sheet.write(self.outbook_row_index, column_index, column_value.strip(), style)
        self.outbook_row_index += 1

    '''
    Method deeply_rooted()
    Input a batch-edited spreadsheet and  a set of paths to citrus mets.xml files.
    For each bibid in both sources, output an excel row for that bibid with the required-specified
    data accepted by the "Deeply Rooted" project at Mississippi U. circa 2017 c/o Julie Shedd
    '''
    def deeply_rooted(self,max_input_files=None):
        #with open(self.output_deeply_rooted, mode="w", encoding='utf-8') as output_file:
        if (1 == 1):
            #See output specs at http://lib.msstate.edu/deeplyrooted#specs
            #Some are ambiguous and Angie and Julie may decide to alter them a bit going forward
            print("Reading {} Input Bibs from the edited spreadsheet".format(len(self.input_file_paths)))
            no_mods_url = 0 #counter for an observed error/warning condition
            for input_file_index,input_file_path in enumerate(self.input_file_paths):
                input_file_name = "{}/{}".format(input_file_path.parents[0], input_file_path.name)
                if max_input_files is not None and input_file_index >= max_input_files:
                    break
                d_column_style = {}
                #print("Processing input file={}".format(input_file_name))
                with open (str(input_file_name), "r") as input_file:
                    if  input_file_index % 250 == 0:
                        print("Processing input file index {}".format(input_file_index))
                    input_xml_str = input_file.read().replace('\n','')
                    # Initialize ordered output dictionary
                    d_output = OrderedDict([(column,'') for column in self.l_deeply_output_columns])
                    try:
                        tree_input_doc = etree.parse(input_file_name)
                    except Exception as e:
                        msg = (
                            "Skipping exception='{}' in etree.fromstring failure for input_file_name={}"
                            .format(repr(e), input_file_name))
                        print(msg)
                        raise
                    # GET xml ROOT for this file
                    try:
                        input_node_root = tree_input_doc.getroot()
                    except Exception as e:
                        msg = ("Exception='{}' doing getroot() on tree_input_doc={}, input_file={}. Return."
                                .format(repr(e), repr(tree_input_doc),input_file_name))
                        print(msg)
                        raise
                    # Do not put the default namespace (as it has no tag prefix) into the d_namespaces dict.
                    d_nsmap = dict(input_node_root.nsmap)
                    d_namespaces = {key:value for key,value in d_nsmap.items() if key is not None}
                    # Output some data for this citrus item
                    #print("Input file={}".format(input_file_name))

                    # First produce single-valued output column values
                    for key, tup2 in self.d_deeply_source.items():
                        value_type = tup2[0]
                        value = tup2[1]
                        xpath = value
                        constant = value

                        if key == 'relation':
                            #Special deeply rooted requirement, always output this as first relation,
                            #but append it with those found in input with type 'original' (see below).
                            result = "Deeply Rooted"
                        elif key == 'description':
                            #Special deeply rooted requirement. Always include following as a component
                            # in description.
                            result = self.description
                        else:
                            result = ''

                        if value_type == 'constant':
                            result = constant
                        elif value_type == 'xml':
                            # Note: may refactor later and add this section to 'list' clause, and just
                            # always use findall() to handle a list of nodes in case a list exists.
                            # Then can use only 2 value types constant and xml.
                            #print("Seeking node at xpath='{}'".format(value))
                            node = input_node_root.find(xpath, d_namespaces)
                            if node is not None:
                                if key == 'publisher':
                                    node_name = node.find('sobekcm:Name',d_namespaces)
                                    if node_name is None:
                                        result = ''
                                    else:
                                        text_name = '' if node_name is None else node_name.text
                                        node_place = node.find('sobekcm:PlaceTerm', d_namespaces)
                                        text_place = '' if node_place is None else node_place.text
                                        result = '{}, {}'.format(text_name, text_place)
                                elif key == 'description':
                                    text = '' if node.text is None else node.text
                                    # use ; sep because description always start with constant
                                    result += ';' + text
                                else:
                                    result = node.text if node is not None else ""
                            # if node is not None
                        elif value_type == 'list':
                            nodes = input_node_root.findall(xpath, d_namespaces)
                            sep = ''
                            for node in nodes:

                                # Nodes with potential Deeply-Rooted defined "Creator" values
                                if (key == 'creator'):
                                    node_role_name_part = node.findall('./mods:namePart', d_namespaces)[0]
                                    potential_creator_name = (
                                        '' if node_role_name_part is None else node_role_name_part.text )
                                    is_donor = False
                                    nodes_role_term = node.findall('.//mods:roleTerm', d_namespaces)
                                    for node_role_term in nodes_role_term:
                                        if (node_role_term.attrib.get('type','') == 'text'
                                            and node_role_term.text == 'donor'):
                                            is_donor = True
                                            break
                                    # node_role_term in nodes_role_term
                                    if is_donor == False and potential_creator_name != '':
                                        result += sep + potential_creator_name
                                        sep = ';'

                                elif (key == 'subject'):
                                    #
                                    nodes_topic = node.findall('./mods:topic', d_namespaces)
                                    result = ('Citrus fruit industry'
                                             + ';Citrus crate labels;Citrus fruits in art')
                                    continue
                                    #Note - 20170602 exam of all citrus mets.xml input files shows 'fast' is
                                    # already assigned to 5 mets
                                    #records, and they exactly match the prior subjects, and to output for deeply
                                    #rooted, we do not show authority nor does input have any other fast subjects
                                    #to add. Separately, when outputting to ufdc mets.xml files, we
                                    #will do different subject handling.
                                    # So put in a continue in prior line, but keep
                                    #unreachable code sitting below it that might be useful later

                                    authority = node.attrib.get('authority', None)
                                    if authority is None or (authority != 'fast') :
                                        # Per specs, only accept 'fast' subjects for deeply rooted
                                        continue
                                    sep = ';'
                                    for node_topic in nodes_topic:
                                         if node_topic is not None:
                                             result += sep + node_topic.text
                                    # for node_topic

                                elif (key == 'relation'):
                                    attr_type = node.attrib.get('type', None)
                                    if attr_type is None or attr_type != 'original':
                                        continue
                                    # Note: if this value is not stripped (sometimes it has trailing
                                    # return character)
                                    # excel silently/puzzlingly rejects the entire value for a
                                    # spreadsheet cell
                                    sep = ';' # Deeply rooted prefix is set above, so first sep is ';'
                                    result += sep + etree.tostring(node,encoding='unicode',method='text').strip()
                            #end node in nodes
                        else:
                            raise Exception("Bad value_type='{}'".format(value_type))

                        # print("Setting d_output key={}, value={}".format(key,repr(result)))
                        #print("key={}, result='{}', tup2={}".format(key,result,repr(tup2)))
                        d_output[key] = result
                    # end for deeply rooted key column names, extracted some data from METS input file

                    # NOW DERIVE/OVERRIDE SOME DATA FOR DEEPLY ROOTED FROM OTHER SOURCES, CUSTOM INSTRUCTIONS
                    result = 'Ephemera;Crate labels'
                    d_output['type'] = result
                    #print("Setting type='{}'".format(result))

                    #Also add mods:note text as components to the Description value:
                    xpath = './/mods:note'
                    description = d_output['description']
                    for node in input_node_root.findall(xpath, d_namespaces):
                        description += ';' + node.text
                    d_output['description'] = description

                    creator = d_output['creator']
                    if (len(creator) > 55):
                        print("******* WARNING ******  file={},index={}: Got long creator={}"
                              .format(input_file_name,input_file_index,creator))

                    #If no data given for relation, just set "Deeply Rooted"'
                    relation = d_output.get('relation','')
                    if relation  == '':
                        print("For input index {}, setting relation to Deeply Rooted"
                              .format(input_file_index))
                        d_output['relation'] = "Deeply Rooted"
                    else:
                        #print("Relation check ok at '{}'".format(relation))
                        pass

                    # VALIDATE/REPORT MISSING INVALID DATA FROM THIS INPUT FILE
                    identifier = d_output.get('identifier', '')
                    if identifier == '':
                        print("Input file {} has no mods:url identifier. trying mods:recordIdentifier it."
                              .format(input_file_name))
                        # Make this cell pink
                        easyxf_style = ('pattern: pattern solid, fore_colour light_blue;'
                              'font: colour white, bold True;')
                        d_column_style['identifier'] = xlwt.Style.easyxf(strg_to_parse=easyxf_style)
                        no_mods_url += 1
                        # Workaround for now... but may want to update METS.XML later to set mods:url to this.
                        node_identifier = input_node_root.findall('.//mods:recordIdentifier',d_namespaces)[0]
                        record_identifier = (
                            '' if node_identifier is None else node_identifier.text.replace('_','/'))
                        if record_identifier == '':
                            print("Input file {} has no identifier. Skipping it.".format(input_file_name))
                            continue
                        identifier = 'http://ufdc.ufl.edu/{}'.format(record_identifier)
                        print("Using makeshift identifier = {}".format(identifier))
                        d_output['identifier'] = identifier

                    # parse the identifier
                    id_parts = identifier.split('/')
                    xml_bib = '_'.join(id_parts[-2:])
                    # xml_bib is in format bib_vid. Skip it if not in the edits spreadsheet.
                    ess_row = self.d_bibid_rowidx.get(xml_bib.upper(), None)
                    if ess_row is None:
                        print("ERROR: Input file {}, bib {}, is not in edits spreadsheet. Skipping it."
                            .format(input_file, xml_bib))
                        continue
                    # Could add check here that the identifier within the mets file matches
                    # the bibid inferred# by the filename,but such anomalies have not been
                    # seen in our data...

                    # Set ss row value to -1 to show it was visited
                    self.d_bibid_rowidx[xml_bib.upper()] = -1
                    # We can follow custom spreadsheet processing rules (uf lib basecamp3 Deeply Rooted
                    # group circa 2017)
                    # Required spreadsheet column names have been agreed upon previously.
                    # RULE 1 For UFDC UPDATES
                    #  If spreadshseet column original_date_issued is not null, use it rather than
                    # date_issued column. But for deeply rooted output, take the date_issued value
                    # that Angie has inputted in edtf format
                    ess = self.sheet_edits
                    dci = self.d_colname_colidx
                    # minority of cells have integers
                    edtf_date = str(ess.cell(ess_row, dci['date_issued']).value)
                    index_dot = edtf_date.find('.')

                    # Remove .0 artifact in the string representation of excel float input values for years
                    if index_dot >= 0:
                        edtf_date = edtf_date[:index_dot]

                    # TEMPORAL COLUMNS
                    # Rule: Prefer the spreadsheet's date over the original mets input_file's date_issued
                    # for Deeply Rooted
                    # Rule: Dates ending u: change u to 0 for date issued, use it also for start_date, and add
                    # 10 years and use that for end date:
                    #print("Got edtf_date='{}'".format(edtf_date))
                    if edtf_date[3] == 'u':
                        str_date = edtf_date[0:3] + '0'
                    else:
                        str_date = edtf_date[0:4]

                    start_year = 0 if str_date == 'NULL' else int(str_date)
                    end_year = 0 if str_date == 'NULL' else int(str_date) + 10
                    period = self.period_by_year(start_year)
                    # for deeply rooted, put the period for coverage temporal, or could put 10-year range
                    coverage_temporal = '{}-{}'.format(start_year,end_year) #per Angie 20170522 log - for deeply
                    # coverage_temporal = period
                    d_output['coverage_temporal'] = coverage_temporal
                    #print("str_date='{}', start={}, end={}, period={}".format(str_date,start_year,end_year,period))
                    d_output['date'] = edtf_date

                    #SPATIAL COLUMNS (country,state,county,city) # see
                    country_idx = dci['country']
                    coverage_spatial = ''
                    sep = ''
                    for cidx in range(country_idx, country_idx+4):
                        value = str(ess.cell(ess_row, cidx).value)
                        if value is None or value == '' or value == 'NULL':
                            continue
                        coverage_spatial  += sep +  value
                        sep = ','
                        d_output['coverage_spatial'] = coverage_spatial
                    #print("Got coverage_spatial='{}'".format(coverage_spatial))

                    if (1==2): # early draft debug output
                        print("\nOUTPUT LINE DICT:" )
                        for key,value in d_output.items():
                            print("key='{}', value='{}'".format(repr(key),repr(value)))

                    #Write excel output row for this input file
                    self.outbook_writerow(d_output = d_output, d_column_style=d_column_style)

                # end with open input file
            # end input_file_path in paths
            #
            print("WARNING: Among {} input *.mets.xml input files, {} lacked a mods:url tag"
                .format(len(self.input_file_paths),no_mods_url))
            # Report on bibids in the spreadsheet that were not found among the in put mets files
            print ("WARNING: The following bibids in the edits spreadsheet were not found among the"
                   "inputted mets.xml files:")
            for bibid, rowidx in self.d_bibid_rowidx.items():
                if 1==1 and rowidx != -1: #disable unless we read all input files
                    print('No mets.xml input file found for bibid:',  bibid)
            # Write the excel output book file
            self.deeply_book.save(self.deeply_rooted_output_file_name)
        # end with open output file
        return
    # end deeply_rooted()

# SET UP FOR RUN to generate deeply_rooted data
linux='/home/robert/'
windows='U:/'
input_folder = etl.data_folder(linux=linux, windows=windows,
    data_relative_folder='data/citrus_mets_base')

input_folders = [input_folder]
output_folder = etl.data_folder(linux=linux, windows=windows,
    data_relative_folder='data/outputs/deeply_rooted')
output_file_name = output_folder + '/' + 'deeply_rooted.xls'

edits_file = input_folder + '/citrus_20170519a.xlsx' # Angie's edited spreadsheet of citrus data

citrus = Citrus(edits_file=edits_file,input_folders=input_folders, input_path_glob="AA*_00001.mets.xml",
    deeply_rooted_output_file_name=output_file_name)

citrus.deeply_rooted(max_input_files=None)
print ("Done! See output_file={}".format(output_file_name))
