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

from lxml import etree
'''
Method uf_affiliation_value()

Given an Elsevier-asserted author affiliation text value, this method:
returns 1 - if the text value identifies the university of florida
returns 0 - otherwise
NB: Elsevier is very good about using one of the substrings sought,
however it will be most often be embedded in other text, hence the
need for this simple method.
'''
def uf_affiliation_value(name,verbosity=0):
    me = 'uf_affiliation_value'
    text_lower = name.lower() if name is not None else ''
    if verbosity > 0:
        print("{}:Using affil argument name={}".format(me,repr(name)))
    for match in ['university of florida','univ.fl','univ. fl'
        ,'univ fl' ,'univ of florida'
        ,'u. of florida','u of florida']:
        if text_lower.find(match) != -1:
            if verbosity > 0:
                stars = '***************************'
                print("\n{}\nMatch='{}'\n{}"
                  .format(stars, text_lower,stars))
            return 1
    if verbosity > 0:
        print("NO Match")
    return 0

'''
def uf_elsevier_item_authors()

<summary>
This method is a sequence/generator that is initialized
with a full-text article root xml lxml node.
</summary>

<return> The generator is returned, and over success calls it returns:

A sequence, where each squence member/iteration is a tuple:
0 = True or False - whether this author for this main item/article is a UF author
1 = node_author - the xml node for this author within the full-text xml
    document result for this item/article from Elsevier.
</return>
'''

def uf_elsevier_item_authors(node_root_input=None, namespaces=None,
    verbosity=0):

    me = 'uf_elsevier_item_authors()'
    d_ns = namespaces

    node_serial_item = node_root_input.find(
        './/xocs:serial-item', namespaces=d_ns)
    if verbosity > 0:
        print("{}: Got node_serial_item='{}'"
              .format(me,repr(node_serial_item)))

        # For each author_group of this doc serial item, assign any UF Authors.
        # We'll build up a chunk of target XML into a variable to xml-authors
        # to stuff into the output string as format() arguments later.
        nodes_ag = node_serial_item.findall(
          './/ce:author-group', namespaces=d_ns)
        if (verbosity > 0):
            print("{}: scanning {} author-group nodes"
              .format(me,len(nodes_ag)))
        for node_ag in nodes_ag:
            # d_id_aff: key is string for attribute id for an affiliation,
            # value is its lxml node
            d_id_aff = {}
            #print('Got an author group, getting affiliations')

            # Save all child affiliation nodes keyed by their id
            nodes_aff = node_ag.findall(
              './ce:affiliation', namespaces=d_ns)
            if verbosity > 0:
                print("{}: Author group has {} affiliation nodes"
                  .format(me,len(nodes_aff)))

            for node_aff in nodes_aff:
                #print('Got affiliation ')
                if 'id' in node_aff.attrib:
                    #print("Got affiliation with id={}".format(id))
                    d_id_aff[node_aff.attrib['id']] = node_aff
                else:
                    #Uuse empty string as ID - support author-groups all with
                    # single affiliation, where neither author refid nor
                    # affiliation id attributes are needed or used.
                    d_id_aff[''] = node_aff

            # Generate xml with a list of the authors, also indicating whether
            # each is a UF author.
            #print("Getting authors")
            nodes_author = node_ag.findall(
                './ce:author', namespaces=d_ns)
            for node_author in nodes_author:
                #print("got an author")
                is_uf_author = 0
                author_has_ref_aff = None
                node_refs = node_author.findall(
                  './ce:cross-ref', namespaces=d_ns)
                for node_ref in node_refs:
                    #print("got a cross-ref")
                    if 'refid' in node_ref.attrib:
                        refid = node_ref.attrib['refid']
                        #print("got a refid={}".format(refid))
                        if refid.startswith('af') and refid in d_id_aff:
                            author_has_ref_aff = 1
                            if refid not in d_id_aff:
                                print("WARN: Author has refid={}, but no"
                                     " affiliation has that id"
                                     .format(refid))
                            node_aff = d_id_aff[refid]
                            node_text = etree.tostring(
                              node_aff, encoding='unicode', method='text')
                            # Must replace text tabs with spaces, used as bulk
                            # load delimiter, else bulk insert msgs appear 4832
                            # and 7399 and inserts fail.
                            node_text = node_text.replace(
                              '\t',' ').replace('\n',' ').strip()
                            #print("Found affiliation={}".format(node_text))
                            # set to 1 if this is a UF affiliation, else 0.
                            is_uf_author = uf_affiliation_value(node_text,verbosity=verbosity)
                            if (verbosity > 0):
                                msg = ("For {}, is_uf_author={}"
                                  .format(repr(node_text),is_uf_author))
                                msg = msg.encode('ascii',errors='replace')
                                print(msg)
                            if is_uf_author:
                                break
                        #end if refid.startswith('af')
                    #end if 'refid' in node_ref.attrib
                # end node_refs (cross-refs) for this author
                if not author_has_ref_aff:
                    # Still found no affiliation for this author, so use empty
                    # string for refid
                    node_aff = d_id_aff.get('',None)
                    if node_aff is not None:
                        node_text = etree.tostring(
                          node_aff, encoding='unicode', method='text')
                        node_text = node_text.replace('\t',' ').replace(
                          '\n',' ').strip()
                        is_uf_author = uf_affiliation_value(node_tex,verbosity=verbosityt)
                        #print("For this affiliation, is_uf_author={}"
                        # .format(is_uf_author))
                #end if not author_has_ref_aff
                yield is_uf_author, node_author
            #for node_author in findall()
        #end author group
    return
#end uf_elsevier_item_authors(node_root_input=None)

def test_run():
    pass

# RUN TEST Program
env = 'windows'
if env == 'windows':
    root_folder = ""
else:
    raise ValueError("Env={} is not implemented.".format(env))

test_run()
print("Done!")

'''
<summary>
def articles_with_uf_authors():

This is a generator method that is given a root folder path and a glob pattern.

It returns a sequence of tuples, each tuple representing an xml file
under the folder.

</summary>
<return> The return value is a sequence, where
each member of the sequence is a tuple of
0 - the xml root node to an elsevier item of an indicated file.
1 - the path of a file name
</return>


<param name='items_with_uf_author'

It is given a root directory and a glob pattern,
and it recursively visit all directories for that pattern (must end with .xml)
and expect to find xml full-text article
file.

For each file, parse its xml and assess whether it has a UF author.

Yield here a tuple:
0 = True or False whether the article has one or more UF authors
1 = The lxml root node for the item.
For example, a caller may generate these yielded tuples and do something like:
for each tuple that shows a True UF Author, use the node to output the fulltextxml
to an output file in a folder where only UF Authored articles will be stored.

absolute path or the Path object (maybe make an option) to that file.

This method can be used to copy or just visit true UF-authored articles in a
folder structure where xml files also for non-uf articles have been deposited,
as done by the ealdxml.py program, at least to date, 201780108.

This functionality was baked into exoldmets, and some new-in-2018 use cases for
marshaling applications have arisen, so splitting this out from exoldmets.py.
<summary>
'''
