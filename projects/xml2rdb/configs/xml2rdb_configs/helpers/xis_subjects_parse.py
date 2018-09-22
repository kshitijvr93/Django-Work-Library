'''
xis_subjects.py

Python 3.6+ code
'''

'''
sample input file has sequence of these 'item' subject term info sections:
---
#Sample XIS-exported input file with subject keywords has sequence of items like this:
-------
<Thesis n="0000002">
<ADD><D>20170214</D>
<IN>DJV</IN>
</ADD>
<CHG><D>20180629</D>
<IN>win</IN>
</CHG>
<TOPIC>Globalization^Sovereignty^Financial markets^Financial transactions^Currency^Information technology^Financial services^International organizations^Flexible spending accounts^Conceptualization</TOPIC>
<OLDLCSH />
<OLDKW>globalization, sovereignty, uk^Political Science^Florida State University^Cocoa High School (Cocoa, Fla.)^Globalization^Sovereignty^Financial markets^Currency^Financial transactions^Financial services^Information technology^Finance^Flexible spending accounts^Conceptualization</OLDKW>
<GEO>Union County (Florida)</GEO>
<FLORIDIANS>Florida State University^Cocoa High School (Cocoa, Fla.)</FLORIDIANS>
<AU><FNAME>Jamie E</FNAME>
<LNAME>Scalera</LNAME>
</AU>
<TI>Challenging the Sovereign</TI>
<DPUB>2007</DPUB>
<ID>UFE0021053_00001</ID>
</Thesis>
-------

and a simple input pre-process program xis_xml.py will read that input file
and only convert the elements with ^-separated terms to
child <I> (item) elements, eg:

<FLORIDIANS>
  <I>Florida State University</I>
  <I>Cocoa High School (Cocoa, Fla.)</I>
</FLORIDIANS>
---
'''


import sys, os, os.path, platform
from io import StringIO, BytesIO
import codecs
from copy import deepcopy

from tempfile import NamedTemporaryFile, mkstemp, TemporaryFile
from shutil import move, copyfile, copy, copy2
from os import remove


def register_modules():
    platform_name = platform.system().lower()
    if platform_name == 'linux':
        modules_root = '/home/robert/'
        #raise ValueError("MISSING: Enter code here to define modules_root")
    else:
        # assume rvp office pc running windows
        modules_root="C:\\rvp\\"
    sys.path.append('{}'.format(modules_root))
    sys.path.append('{}git/citrus/modules'.format(modules_root))
    return platform_name

#platform_name=register_modules()

from pathlib import Path
from collections import OrderedDict
from lxml import etree

#import regular expressions
import re
import datetime

utc_now = datetime.datetime.utcnow()
utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")

'''
def generator_new_xis_items(
   input_file_name=None, item_tag=None, parse_tags=None, delim='^',
    log_file=None, verbosity=0):

DO: given an input file name, and string item_tag try to read the next input
    line set for an 'item_tag' item and:

Return null if:

(1) no line left in input file, or
(2) the next line does not begin with the <item_tag>

Buffer input lines into a string and keep reading until:
case: an end of file,
   in which case return null
case: an </item_tag> is found
   in which case
   - parse the input buffer into an lxml doc,
   - find any nodes in the item with named in given caret_tags
   - for each such caret-node, if it has text content:
      -- parse its text content into sub-values
      -- remove its text content
      -- for each subvalue_n
          -- add <I>subvalue_n</I> child in the caret_tag/node
             for every sub value
  - yield the root xml node

NOTE for Future: consider to return a tuple, where always the first value
is the prescribed item node (or None), and as a new second value, return the
lines buffer.
So, if buffer is not len 0, then maybe caller wants to do something with it.

'''
def generator_new_xis_items(
    input_file_name=None,
    item_tag=None, parse_tags=None,
    delim='^', log_file=None,
    verbosity=0):

    me = 'generator_new_xis_items'
    seq = 'sequence_new_xis_items'
    node = None
    lines = ''

    with open(input_file_name,mode="r") as input_file:
        line = input_file.readline()
        if verbosity > 0:
            print(f"{me}: Got first input line='{line}'")
        sw =f"<{item_tag}"
        if not line.startswith(sw):
            if verbosity > 0:
                print(f"{me}:Error: line  '{line}' does not startwith '{sw}'")
            return lines
        lines += line
        sw =f"</{item_tag}"
        for line in input_file:
            if verbosity > 1:
                print(f"{seq}: Got input line='{line}'")
            lines += line
            if line.startswith(sw):
                #Parse the lines buffer as xml and return the item node
                if verbosity > 1:
                    print(f"{seq}: Made all lines='{lines}'")
                node_root = etree.fromstring(str.encode(lines))

                for parse_tag in parse_tags:
                    xp = (f".//{parse_tag}")
                    nodes = node_root.findall(xp)
                    l = len(nodes)
                    for node in nodes:
                        text = '' if node.text is None else str(node.text)
                        node.text = None
                        terms = text.split(delim)
                        l = len(terms)
                        if verbosity > 1:
                            print(f"Found node of {xp} found {terms} terms.")
                        for term in terms:
                            #Create child elts 'I' for items of terms
                            child_element = etree.Element("I")
                            child_element.text = term
                            # Add the item
                            node.append(child_element)
                        # created child item for each term
                    # created required child elements for this node instance
                # created required child elements for this parse tag

                # render the updated item tree

                newlines = etree.tostring(node_root, pretty_print=True)
                lines = ''

                # Find all nodes and do special parsing and reconstruction
                # for given ones

                #Create xml tree and parse  subject nodes
                yield newlines

        #if we got here this is premature end of file
        # should never happen with automated inputs, just print it if it does
        print( f"{me}: premature end of input file {input_file}, lines={lines}")
        return lines
    # end with open
    # normal end of file
    return (None, lines)

# end def generator_new_xis_items

def run():
    ifn = r'C:\rvp\data\xis\export_subjects\input.txt'
    ofn =  r'C:\rvp\data\xis\export_subjects\xis_subjects_parsed.xml'
    lfn =  r'C:\rvp\data\xis\export_subjects\log.txt'

    n_items = 0
    max_items = 0
    lines = ''
    verbosity = 1
    create_root_tag = True

    with open(ofn, mode='wb') as out_file, \
        open(lfn, mode='w') as log_file:
        # Use wb for  out_ifle as lines is byte str
        seq_new_items = generator_new_xis_items(input_file_name=ifn,
                item_tag = 'Thesis',
                parse_tags = ['TOPIC', 'OLDLCSH', 'OLDKW', 'GEO',
                    'FLORIDIANS' ],
                log_file=log_file,
                verbosity=verbosity,
                )
            #Print node output here to file
        if create_root_tag:
            out_file.write(bytes("<ALL>\n".encode('utf-8')))
        for lines in seq_new_items:
            n_items += 1
            if verbosity > 1:
                print( f"Outputting output item number {n_items}\n",
                  file=log_file)
                print(
                  f"Got output item number {n_items},lines={lines}",
                    file=log_file)

            out_file.write(lines)
            if max_items > 0 and n_items == max_items:
                break
        # end while
        if (create_root_tag):
            out_file.write(bytes("</ALL>\n".encode('utf-8')))

    # end with context
# end def run

# MAIN program just run
run()
