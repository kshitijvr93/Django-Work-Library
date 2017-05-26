#TODO - allow undefined namespaces
from lxml import etree
import os

def xml_pretty_str_by_filename(xml_fname):
    input_xml_str=""
    with open (xml_fname, "r") as input_file:
        input_xml_str = input_file.read().replace('\n','').replace('{', '{{{{').replace('}', '}}}}')
    tree_input_doc = etree.fromstring(input_xml_str)
    str_pretty = etree.tostring(tree_input_doc, pretty_print=True, xml_declaration=True)
    return(str_pretty)

filename="C:/rvp/tmpdir/tmpfile.xml"
pretty = xml_pretty_str_by_filename(filename)

print(pretty)
