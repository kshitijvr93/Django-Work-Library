'''citrus.py
'''
import csv
import etl
from pathlib import Path
from lxml import etree
from lxml.etree import tostring
from collections import OrderedDict
import xlrd, xlwt
from xlrd import open_workbook

class FilePaths():

    def __init__(self, input_folders=None, input_path_glob=None ):
        if (input_folders is None or input_path_glob is None):
            raise Exception(ValueError, )
        if (input_folders is not None and input_path_glob is not None):
            # compose input_path_list over multiple input_folders
            input_path_list = []
            for input_folder in input_folders:
                print("FiePaths(): Gathering files in input_folder='{}' that match {}\n"
                .format(input_folder, input_path_glob))
                input_path_list.extend(list(Path(input_folder).glob(input_path_glob)))
            self.paths = input_path_list
            print('FilePaths: found {} file paths matching {}'.format(len(self.paths), input_path_glob))
        self.file_index = 0
        return
#end class Files

class Citrus():

    def __init__(self, paths=None, edits_file=None, input_folders=None, input_path_glob=None, output_deeply_rooted=None):
        self.paths = FilePaths(input_folders, input_path_glob).paths
        self.output_deeply_rooted = output_deeply_rooted
        description = ('This item has been aggregated as part of the Association of Southeastern'
              + ''' Research Libraries (ASERL)'s "Deeply Rooted: The Agricultural & Rural History of the '''
              + 'American South" project.')
        #The keys of this dictionary double as the header column names to be output to an eventual csv or excel file
        # The values's first tuple indicates constant, or xml (single element) or list (repeated elements)
        # Code cases will rely on the key name to do special processing as well.
        self.d_deeply_source = OrderedDict([
                ('relation', ('constant', 'Deeply Rooted' )),
                ('title', ('xml', './/mods:title' )),
                #special conditions for transforming subject data here require subject id and sub-elt topic
                ('subjects', ('list', './/mods:subject')),
                ('description', ('constant', description )),
                ('source', ('xml', './/mods:recordContentSource' )),
                ('publisher', ('xml', './/sobekcm:Publisher' )), #special case/code to extract from this node
                ('coverage_temporal', ('xml', './/sobekcm:Temporal/sobekcm:period' )),
                ('format', ('constant', 'image/jpeg, image/jp2, image/tiff, image/jpeg-thumbnails' )),
                ('identifier', ('xml', './/mods:url' )),
                ('rights', ('xml', './/mods:accessCondition' )),
                ('creator', ('list', './/METS:agent' )), # use the  name of creator individual
                ('language', ('xml', './/mods:languageTerm' )),
                ('type', ('xml', './/mods:genre' )),
                ('spatial', ('xml', './/mods:hierarchicalGeographic' )),
                ('contributor', ('constant', 'University of Florida Libraries' )),
                ('date', ('xml', './/mods:dateIssued' )),
        ])
        #fieldnames = [ key for key in d_]

        # EXCEL SPREADSHEET OF EDITS
        book = open_workbook(edits_file, 'r')
        self.sheet = book.sheet_by_index(0)

        # read dict of column name:index info into key-value pairings
        self.d_colname_colidx = OrderedDict(
            {self.sheet.cell(0,col_index).value : col_index for col_index in range(self.sheet.ncols)})
        print("Got edit spreadsheet column names,indexes = {}".format(repr(self.d_colname_colidx)))
        # User OrderedDict to Maintain bib order of original input spreadsheet
        # Use bibid (in column index 1) as key because no dups are allowed
        self.d_bibid_rowidx = OrderedDict(
            {self.sheet.cell(row, 1).value.upper() : row for row in range(self.sheet.nrows)})

        print("Got {}={} citrus spreadsheet bibs".format(len(self.d_bibid_rowidx), self.sheet.nrows))

        # Pre-agreed period time-era names keyed by with start year
        self.d_year_era = OrderedDict([
            (1920, "Florida Land Boom"),
            (1929, "Great Depression"),
            (1939, "World War II"),
            (1946, "First Cold War"),
            (1954, "Civil Rights"),
            (1969, "Vietnam War"),
            (1976, "Post 1975"),
        ])

    #end def init
    '''
    Method deeply_rooted()
    from set of paths parse citrus files and for each output a tab-separated line of output column values suitable for
    excel import and transmission to the "Deeply Rooted" project at Mississippi U. circa 2017 c/o Julie Shedd
    '''
    def deeply_rooted(self):
        with open(self.output_deeply_rooted, mode="w", encoding='utf-8') as output_file:
            for path in self.paths:
                input_file_name = "{}/{}".format(path.parents[0], path.name)
                print("Processing input file={}".format(input_file_name))
                with open (str(input_file_name), "r") as input_file:
                    input_xml_str = input_file.read().replace('\n','')
                    d_output = {}
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
                        msg = ("Exception='{}' doing getroot() on tree_input_doc={}. Return."
                                .format(repr(e), repr(tree_input_doc)))
                        print(msg)
                        raise
                    # Do not put the default namespace (as it has no tag prefix) into the d_namespaces dict.
                    d_nsmap = dict(input_node_root.nsmap)
                    d_namespaces = {key:value for key,value in d_nsmap.items() if key is not None}
                    # Output some data for this citrus item
                    print("Input file={}".format(input_file_name))

                    # First produce single-valued output column values
                    for key, tup2 in self.d_deeply_source.items():
                        value_type = tup2[0]
                        value = tup2[1]
                        result = ''
                        if value_type == 'constant':
                            result = value
                        elif value_type == 'xml':
                            #print("Seeking node at xpath='{}'".format(value))
                            node = input_node_root.find(value, d_namespaces)
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
                                else:
                                    result = node.text if node is not None else ""
                            # if node is not None
                        elif value_type == 'list':
                            nodes = input_node_root.findall(value, d_namespaces)
                            sep = ''
                            for node in nodes:
                                if (key == 'creator' and node.attrib['ROLE'] == 'CREATOR'
                                   and node.attrib['TYPE'] == 'INDIVIDUAL'):
                                    # This is a node in a list of creator nodes and we only need this one.
                                    node_creator_name = node.find('./METS:name', d_namespaces)
                                    result = '' if node_creator_name is None else node_creator_name.text
                                    break
                                elif (key == 'subjects'):
                                    nodes_topic = node.findall('./mods:topic', d_namespaces)
                                    for node_topic in nodes_topic:
                                         if node_topic is not None:
                                             result += sep + node_topic.text
                                             sep = ';'
                                    # for node_topic
                        else:
                            raise Exception("Bad value_type='{}'".format(value_type))

                        # print("Setting d_output key={}, value={}".format(key,repr(result)))
                        print("key={}, result='{}', tup2={}".format(key,result,repr(tup2)))
                        d_output[key] = result
                    # end loop to harvest single-xml-node values from the input file
                    #
                    # VALIDATE/REPORT MISSING INVALID DATA FROM THIS INPUT FILE

                    identifier = d_output.get('identifier', '')
                    if identifier == '':
                        print("Input file {}. Has no identifier. Skipping it.".format(input_file))
                        continue
                    id_parts = identifier.split('/')
                    xml_bib = '_'.join(id_parts[-2:])
                    # xml_bib is in format bib_vid. Skip it if not in the spreadsheet.
                    ss_row = self.d_bibid_rowidx.get(xml_bib.upper(), None)
                    if ss_row is None:
                        print("ERROR: Input file {}, bib {}, is not in edits spreadsheet. Skipping it."
                            .format(input_file, xml_bib))
                        continue
                    # Set ss row value to -1 to show it was visited
                    self.d_bibid_rowidx[xml_bib.upper()] = -1

                    # We can follow custom spreadsheet processing rules (uf lib basecamp3 Deeply Rooted group circa 2017)
                    # Required spreadsheet column names have been agreed upon previously.
                    # RULE 1 For UFDC UPDATES
                    #  If spreadshseet column original_date_issued is not null, use it rather than date_issued column
                    # But for deeply rooted output, take the date_issued value that Angie has inputted in edtf format
                    ss = self.sheet
                    dc = self.d_colname_colidx
                    colidx = dc['date_issued']
                    print("Using row index '{}', col index '{}'".format(repr(ss.row), repr(colidx)))
                    edtf_date = ss.cell(ss_row, dc['date_issued']).value
                    # Supersede the original mets input_file's date_issued for Deeply Rooted
                    d_output['date'] = edtf_date

                    print("\noutput line={}".format(repr(d_output)))

                # end with open input file
            # end with open output file
        return
    # end def run()

# SET UP FOR RUN to generate deeply_rooted data
linux='/home/robert/'
windows='U:/'
input_folder = etl.data_folder(linux=linux, windows=windows, data_relative_folder='data/citrus_mets_base')

input_folders = [input_folder]
output_folder = etl.data_folder(linux=linux, windows=windows, data_relative_folder='data/outputs/deeply_rooted')
output_file = output_folder + '/' + 'deeply_rooted.txt'

edits_file = input_folder + '/citrus_20170519a.xlsx' # Angie's edited spreadsheet of citrus data
citrus = Citrus(edits_file=edits_file,input_folders=input_folders, input_path_glob="AA*00_00001.mets.xml",
    output_deeply_rooted=output_file)

citrus.deeply_rooted()
print ("Done! See output_file={}".format(output_file))
