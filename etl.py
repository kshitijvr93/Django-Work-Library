#etl - extract transform load tools.
import datetime
import pytz
import os
import sys

from pathlib import Path
import hashlib
from collections import OrderedDict
from lxml import etree
from lxml.etree import tostring
from pathlib import Path

'''Method get_output_folder_name()
'''
def home_folder_name():
    from os.path import expanduser
    return expanduser("~")

def get_output_folder_name(home_relative_folder=''):
    import platform
    p_system = platform.system()
    folder = home + "/" + home_relative_folder
    print("Making folder {}".format(folder))
    os.makedirs(folder, exist_ok=True)
    #may add code here to create the directory if not extant
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
