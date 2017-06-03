#etl - extract transform load tools.
import datetime
import pytz
import os
import platform
import sys
import re

from pathlib import Path
import hashlib
from collections import OrderedDict
from lxml import etree
from lxml.etree import tostring
from pathlib import Path

def data_folder(linux='/tmp/data/', windows='c:/data/',
    data_relative_folder=None, exist_ok=True, verbosity=0):
    if platform.system().lower() == 'linux':
        folder = linux + data_relative_folder
    else:
        folder = windows + data_relative_folder
    os.makedirs(folder, exist_ok=exist_ok)
    return folder

def home_folder_name():
    from os.path import expanduser
    return expanduser("~")

def make_home_relative_folder(home_relative_folder='',exist_ok=True, verbosity=0):
    if home_relative_folder.startswith('/'):
        home_relative_folder.replace('/','')
    folder = home_folder_name() + "/" + home_relative_folder
    if verbosity > 0:
        print("Making folder {}".format(folder))
    os.makedirs(folder, exist_ok=exist_ok)
    return folder

''' Generic utility excape_xml_text:
Given a str, replace embedded 'special xml characters' with their xml quotable formats.
Also replace tabs with space for easier conversion of multiple fields later
to tab-separated values.
'''
def escape_xml_text(str):
    str = str.replace("<", "&lt;")
    str = str.replace(">", "&gt;")
    str = str.replace("&", "&amp;")
    str = str.replace("\"", "&quot;")
    str = str.replace("\t", " ")
    return str
'''
Method html_escape(str)

Replace text xml characters in given 'str' with their 'xml quotable' formats.
Also replace tabs with space for easier conversion of multiple fields later
to tab-separated values.

Return the altered str
'''
def html_escape(text):
    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
        "\t": " ", # extra:replace tabs to create tab-delimited outputs when needed
    }
    #text = str(text.encode('ascii', 'xmlcharrefreplace'))
    text_out = ""
    for c in text:
        text_out += str(html_escape_table.get(c,c) )
    #text_out = text_out.encode('utf-8', 'xmlcharrefreplace')
    return text_out

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
#end class FilePaths


'''Method add_subelements():
Generic logging utility helper:

Given an lxml element, add subelements recursively from nested python data structures
This may be used to generate xml log files, however, it can take up too much core if used to
report per-input-file messages, and if so, it may be
better to disable for 'big' batches of xml files to convert, or break up to create multiple log files.
'''
def add_subelements(element, subelements, item_ids=False):
    if isinstance(subelements, dict):
        d_subelements = OrderedDict(sorted(subelements.items()))
        for key, value in d_subelements.items():
            # Check for valid xml tag name:
            # http://stackoverflow.com/questions/2519845/how-to-check-if-string-is-a-valid-xml-element-name
            # poor man's check: just prefix with Z if first character is a digit..
            # the only bad type of tagname found ... so far ...
            if key[0] >= '0' and key[0] <= '9':
                key = 'Z' + key
            try:
                subelement = etree.SubElement(element, key)
            except Exception as e:
                print("Skipping etree.SubElement error='{}' for key='{}'"
                     .format(e,key))
                continue
            add_subelements(subelement, value, item_ids=item_ids)
    elif isinstance(subelements, list):
        # Make a dict indexed by item index/count for each value in the 'value' that is a list
        for i, value in enumerate(subelements):
            id_filled = str(i+1).zfill(8)
            if item_ids:
                subelement = etree.Element("item")
                subelement.attrib['id'] = id_filled
                element.append(subelement)
            else:
                #encode the ID as a suffix to to element tag name itself
                subelement = etree.SubElement(element, 'item-{}'.format(id_filled))

            add_subelements(subelement, value, item_ids=item_ids)
    else: # Assume it is a string-like value. Just set the element.text and do not recurse.
        element.text = str(subelements)
    return True
# end def add_subelements()
'''
 From given dictionary, return a list of lxml tree elements, one per dictionary item.
 Arguments are: A root lxml element, and a dictionary where each item represents a sub-element.
 Add a sub-element for each item using the item key as the sub-element name.
 If the item value is a dictionary, then do a recursive call using the new sub_element as d_root and
 the item value as the d_elts parameter.
'''
def add_subelements_from_dict(element, d_subelements):
    # Use an OrderedDct that is sorted by key for easier human-reading
    # First argument must be an lxml element
    # second argument must be a dictionary with
    #  (1) keys being legal XML tag names (not checked here),
    #  but note that they should begin with an alphabetic character, not a digit nor special character.
    # and (2) values being either
    # (a) a string or
    # (b) another dictionary of key values pairs, or
    # (c) a list of dicts with key-value pairs
    d_subelements = OrderedDict(sorted(d_subelements.items()) )
    for key, value in d_subelements.items():
        #For given element, create a new sub-element from this key
        # Check for valid xml tag name: http://stackoverflow.com/questions/2519845/how-to-check-if-string-is-a-valid-xml-element-name
        # poor man's check: just prefix with Z if first character is a digit.. the only bad type of tagname found so far...
        if key[0] >= '0' and key[0] <= '9':
            key = 'Z' + key
        subelement = etree.SubElement(element, key)

        if isinstance(value, dict):
            # Add  value-dict's subelements to this element
            add_subelements_from_dict(subelement, value)
        elif isinstance(value, list):
            #Use the key value as a parent element and the list index(plus 1) as a count attribute
            for i,value2 in enumerate(value):
                subelement2 = etree.SubElement(subelement, 'item')
                subelement2.attrib['count'] = str(i+1)
                add_subelements_from_dict(subelement2, value2)
        else:
            # Assume the value is a string for this element's text value
            subelement.text = str(value)
# end add_subelements_from_dict

def has_digit(inputString):
    return bool(re.search(r'\d', inputString))
def has_upper(inputString):
    return any(i.isupper() for i in inputString)
