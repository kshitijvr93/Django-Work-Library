'''citrus.py
'''
import csv
import etl
from pathlib import Path
from lxml import etree
from lxml.etree import tostring
# print("Hello From Atom Python!")

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

    def __init__(self, paths=None, input_folders=None, input_path_glob=None, output_deeply_rooted=None):
        self.paths = FilePaths(input_folders, input_path_glob).paths
        self.output_deeply_rooted = output_deeply_rooted
        description = ('This item has been aggregated as part of the Association of Southeastern'
              + ''' Research Libraries (ASERL)'s "Deeply Rooted: The Agricultural & Rural History of the '''
              + 'American South" project.')
        #The keys of this dictionary double as the header column names to be output to an eventual csv or excel file
        # The values's first tuple indicates constant, or xml (single element) or list (repeated elements)
        # Code cases will rely on the key name to do special processing as well.
        self.d_deeply_source = {
                'relation': ('constant', 'Deeply Rooted' ),
                'title': ('xml', './/mods:title' ),
                #special conditions for transforming subject data here require subject id and sub-elt topic
                'subjects': ('list', './/mods:subject'),
                'description': ('constant', description ),
                'source': ('xml', './/mods:recordContentSource' ),
                'publisher': ('xml', './/sobekcm:Publisher' ), #special case/code to extract from this node
                'coverage_temporal': ('xml', './/sobekcm:Temporal/sobekcm:period' ),
                'format': ('constant', 'image/jpeg, image/jp2, image/tiff, image/jpeg-thumbnails' ),
                'identifier': ('xml', './/mods:url' ),
                'rights': ('xml', './/mods:accessCondition' ),
                'creator': ('list', './/METS:agent' ), # use the  name of creator individual
                'language': ('xml', './/mods:languageTerm' ),
                'type': ('xml', './/mods:genre' ),
                'contributor': ('xml', './/mods:hierarchicalGeographic' ),
                'date': ('xml', './/mods:dateIssued' ),
        }
        #fieldnames = [ key for key in d_]
        return
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
                            print("Seeking node at xpath='{}'".format(value))
                            node = input_node_root.find(value, d_namespaces)
                            # insert here special cases for mining deeply rooted data from this particular node
                            result = node.text if node is not None else ""
                        elif value_type == 'list':
                            nodes = input_node_root.findall(value, d_namespaces)
                            sep = ''
                            for node in nodes:
                                if (key == 'creator' and node.attrib['ROLE'] == 'CREATOR'
                                   and node.attrib['TYPE'] == 'INDIVIDUAL'):
                                    # This is a node in a list of creator nodes and we only need this one.
                                    node2 = node.find('./METS:name', d_namespaces)
                                    result = '' if node2 is None else node2.text
                                    break;
                                elif (key == 'subjects'):
                                    node2 = node.find('./mods:topic', d_namespaces)
                                    result = '' if node2 is None else node2.text
                        else:
                            raise Exception("Bad value_type='{}'".format(value_type))

                        # print("Setting d_output key={}, value={}".format(key,repr(result)))
                        print("key={}, tup2={}, result='{}'".format(key,repr(tup2),result))
                        d_output[key] = result
                    # end loop to harvest single-xml-node values from the input file
                    #
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

citrus = Citrus(input_folders=input_folders, input_path_glob="AA*00_00001.mets.xml", output_deeply_rooted=output_file)

citrus.deeply_rooted()
print ("Done! See output_file={}".format(output_file))
