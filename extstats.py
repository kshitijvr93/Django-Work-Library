# EXTSTATS
'''
Program extstats inputs article information from saved xml files from the elsevier full-text api.
Each input xml file has xml-coded information pertaining to a single
The eatxml input is from the Elsevier
Full-Text API based on Search API results for queries for UF-Authored articles.

'''

import datetime
import pytz
import os
import sys

# import http.client
#import requests
#import urllib.parse
#import json
#import pprint
from pathlib import Path
import hashlib

from lxml import etree
from pathlib import Path

# Given a pii value, seek a known bibvid for it in the d_pii_bibvid dictionary.

def get_bibvid(pii, d_pii_bibvid, verbosity=0):
        #############
        made_bibid_int = 0
        log_messages=[]

        bibvid = d_pii_bibvid.get(pii.upper(),None)
        if bibvid:
            parts = bibvid.split('_')
            bibid = parts[0]
            bibid_int = int(bibid[2:])
            vid = parts[1]
            vid_int = int(vid)
            if verbosity > 0:
                log_messages.append(
                    "Given pii={} is a key in the SobekCM dictionary of PII, and it has bibvid={}."
                    .format(pii,bibvid))
        else: # The pii value is missing from the dictionary.
            log_messages.append(
                    "Given pii={} unknown to UFDC. No bibvid."
                    .format(pii))
            bibvid = ''

        return log_messages, bibvid
#end def get_bibvid()

'''
Method xml_stats() - read each file named in input_file_list to
accrue some statistics or make a spreadsheet, etc...
'''
def tag_generic(tag):
    return (tag.lstrip('./').replace(':','_').replace('-','_')
            .replace('/','_').replace('{*}','').replace('@','')
           .replace('{','_').replace('}',''))

# Get and return the dictionary of pii values with already-assigned bibvid values
def get_odict_pii_bibvid(input_filename=None):
    #
    pii_file = open(input_filename, 'r')
    d_pii = OrderedDict()
    l_messages = []
    i = 0
    pii_index = 0
    bibvid_index = 1
    for line in pii_file:
        # line.rstrip('\n')   # does NOT work on windows, nor '\r' nor '\r\n'
        # Either of next 2 lines DO work, but use replace() because it should  also
        # work (not cause problems) on both windows and linux platforms...
        line = line.replace('\n','')
        #line = line[:-1]
        parts = line.split(',')
        if len(parts[bibvid_index]) > 16:
            l_messages.append("Error: OOPS got value too long for a bibvid:'{}'".format(parts[1]))
            v=parts[bibvid_index]
            ascii_val = int(parts[bibvid_index][16])
            l_messages.append("Error: Ascii of char at [16]={}".format(int(ascii_val)))
            return None
        d_pii[parts[pii_index]] = parts[bibvid_index]
        i += 1
    pii_file.close()

    return l_messages, d_pii
# end def get_odict_pii_bibvid()

# To an lxml tree, add subelements recursively from nested python data structures
def add_subelements(element, subelements):
    if isinstance(subelements, dict):
        d_subelements = OrderedDict(sorted(subelements.items()))
        for key, value in d_subelements.items():
            # Check for valid xml tag name:
            # http://stackoverflow.com/questions/2519845/how-to-check-if-string-is-a-valid-xml-element-name
            # poor man's check: just prefix with Z if first character is a digit..
            # the only bad type of tagname found ... so far ...
            if key[0] >= '0' and key[0] <= '9':
                key = 'Z' + key
            subelement = etree.SubElement(element, key)
            add_subelements(subelement, value)
    elif isinstance(subelements, list):
        # Make a dict indexed by item index/count for each value2 in the 'value' that is a list
        for i, value in enumerate(subelements):
            subelement = etree.SubElement(element, 'item-{}'.format(str(i+1).zfill(8)))
            add_subelements(subelement, value)
    else: # Assume it is a string-like value. Just set the element.text and do not recurse.
        element.text = str(subelements)
    return True
# end def add_subelements()

'''
Read an elsevier input xml file and output some statistics for:
  (1) a list of single-occurrence xml tag names and
  (2) a list of multi-occurrence tag names, along with a key_name ...

Return log messages and d_row dict of results, and if d_row is None, a failure occurred.
return value d_tag: The key is one of the given tag_names and the value is the tag_name's text
value in the input_file_name else it is the empty string for tags that are not found there.

Return list value l_tagvalues: l_tagvalues is a list of the values in the given input xml
file name, and the values are
ordered in the same order of the corresponding given argument tag_names.

Return value l_od_index: a list of ordered dictionaries, with an ordered correspondence to the
input argument list of multi_tag_names.

Consider that the argument has multi_tag_name[x] of 'ce:textfn',
then l_od_index[x] is a dictionary where for each item it's key is the index value of the occurrence of
name 'ce:textfn' in the input file, and its value is the value found for that occurence in the input
file (starting at index 0).

If the multi-tag did not appear in the input file, then the l_od_index[x] is None, where x corresponds to the
index of that tag name in input argument multi_tag_name.

Otherwise the od_index = l_od_index[x] dictionary exists and its items have the key
that is the string of is the occurrence number of the tag in the input file,
and the value is the text value of that tag.
'''

def elsevier_xml_file_stats(
    input_file_name=None, tag_names=None, multi_tag_names=None, verbosity=0):

    log_messages = []
    full_api_failure = 0

    if not (input_file_name):
        log_messages.append("Missing input file_name. Bad arguments.")
        return log_messages, None, None
    # msg = "Using input_file_name='{}'".format(input_file_name)
    # print('\n----------------------\n{}\n------------------------\n'.format(msg))
    # log_messages.append(msg)

    # (1) Read an elsevier input xml file to variable input_xml_str
    # correcting newlines and doubling up on curlies so format() works on them later.
    with open (str(input_file_name), "r") as input_file:
        input_xml_str = input_file.read().replace('\n','')

    # (2) and convert input_xml_str to a tree input_doc using etree.from fstring,
    if input_xml_str[0:9] == '<failure>':
        # This is a particular check for a 'bad' xml file in a particular set of xml files.
        # This skipping is not generic feature of this method.
        #print("This xml file is a <failure>. Skipping it.")
        log_messages.append("<failure> input_file {}.Skip.".format(input_file_name))
        return log_messages, None, None

    try:
        tree_input_doc = etree.parse(input_file_name)
    except Exception as e:
        msg = (
            "Skipping exception='{}' in etree.fromstring failure for input_file_name={}"
            .format(repr(e), input_file_name))
        #print(msg)
        log_messages.append(msg)

        return log_messages, None, None

    # GATHER STATISTICS FOR THIS PII/ARTICLE FROM ITS FULL-API XML TREE
    try:
        input_node_root = tree_input_doc.getroot()
    except Exception as e:
        msg = ("Exception='{}' doing getroot() on tree_input_doc={}. Return."
                .format(repr(e),repr(tree_input_doc)))
        #print(msg)
        log_messages.append(msg)

        return log_messages, None, None

    d_namespaces = {key :value for key,value in dict(input_node_root.nsmap).items() if key is not None}

    l_tag_values = []
    for tag_name in tag_names:
        text = ''
        #elt = input_node_root.find(tag_name, namespaces=d_namespaces)
        xpe = '{}/text()'.format(tag_name)
        # print("Using xpe={}".format(xpe))
        text = tree_input_doc.xpath(xpe, namespaces=d_namespaces)[0]

        if text is not None:
            # We must replace tabs here, as we use that delim in output stats file(s), headed for excel
            #text = '' if elt.text is None else elt.text.replace('\t',' ')
            #text = '' if text is None else text.replace('\t',' ')
            msg = "Parsed tag {}={}".format(tag_name,text)
            #print(msg)
            # too verbose?
            # log_messages.append(msg)
        else:
            text = ''
            pass
        l_tag_values.append(text)

    # loop to get field/column values
    #
    #print("elsevier_xml_file_stats: returning: l_tag_values='{}'".format(repr(l_tag_values)))

    # Also output a dictionary of data for each tag that can appear multiple times per column
    # tag names with multiple occurrences
    l_mtag_dicts = []
    for mtagname in multi_tag_names:
        # Create ordered dict for this multi-occurrence mtag with key of index
        # and value of that occurrence in the input
        od_mtag = OrderedDict()
        l_mtag_dicts.append(od_mtag)
        #elts = input_node_root.findall(mtagname, namespaces=d_namespaces)
        xpe = '{}'.format(mtagname)
        #print("Using mtag xpe={}".format(xpe))

        texts = tree_input_doc.xpath('{}'.format(xpe), namespaces=d_namespaces)

        #print("Printing {} occurences for multi-tagname='{}':".format(len(texts), mtagname))

        #for i,elt in enumerate(elts):
        for i, text in enumerate(texts):
            #print("multi-tagname={}, occurrence={}, text={}".format(mtagname,i,elt.text))
            #od_mtag[str(i)] = elt.text
            od_mtag[str(i)] =  text
    #print("l_mtag_dicts:\n{}\n".format(repr(l_mtag_dicts)))
    return log_messages, l_tag_values, l_mtag_dicts

# end def elsevier_xml_file_stats()

def xml_tag_to_db_tag(d_url_nsa=None, tag=None, use_nsa=True):
    if not (d_url_nsa and tag):
        print("Whoa!!")
        return None

    db_tag = tag.replace('-','_') # make name compatibile with db column names
    tag_parts = db_tag.split('}')

    if len(tag_parts) > 1:
        # The xml tag has an explicit 'curly' namespace - probably always the case?
        if use_nsa == True:
            # We want to try to use a namespace abbreviation for the 'curly' namespace
            nsa = d_url_nsa.get(tag_parts[0][1:],None)
            if nsa:
                # The url was found in our url to nsa (namespace abbreviation dictionary)
                # Use the namespace abbreviation and '_' for first part of tag name
                db_tag = '{}_{}'.format(nsa,tag_parts[1])
            else:
                # If key is not in d_url_nsa, it is default namespace, so
                # just use the tag part without the curly default namespace.
                # By default by xml conventions, it has no nsa.
                db_tag = tag_parts[1]
        else:
            # We want to just drop the curly namespace and take our chances on tag name duplicates...
            # But later we can fix it and provide for synonyms in a mod to the the d_visit tree substructures
            db_tag = tag_parts[1]
    else:
        #There is no curly namespace in this tagname, so use the basic tagname
        db_tag = tag_parts[0]

    return db_tag

# end def xml_tag_to_db_tag

#Note argument d_namespaces requires a key of None for the default namespace
def dict_expand(d_input=None, d_nsmap=None, recurse=True):
    # print("dict_expand, using d_nsmap={}".format(repr(nsmap)))
    r_collect={}
    default_ns = d_nsmap.get(None, "")
    level = 0
    for key,value in d_input.items():
        # For r_collect key values, we must substitute the full http expression for namespace
        # abbreviations, to make matching faster later
        if isinstance(value, dict) and (recurse == True) :
            value = dict_expand(d_input=value, d_nsmap=d_nsmap, recurse=recurse)

        tag_parts = key.split(':')
        if len(tag_parts) > 1:
            # Construct the expanded namespace prefix in the key here
            # so node.tag values (which lxml provides with these expanded names)
            # used in method xml_node_visit(),  will match without having to convert
            # each node.tag value to a non-expanded abbreviated namespace prefix.
            full_namespace = d_nsmap[tag_parts[0]]
            sub_tag = tag_parts[1]
        else:
            if key != 'doc': #special root node name to NOT expand - elementtree prepends the {}
                # Insert default namespace to later allow for node.tag matches in xml_node_visit()
                full_namespace = default_ns
                sub_tag = key
            else:
                # 'doc' is special root node for this program, it has no namespace, but
                # node.tag provides it as "{}doc", so enter that key in the output dict here.
                r_collect['doc'] = value
                continue # Must continue here to avoid overwrite

        r_collect['{{{}}}{}'.format(full_namespace,sub_tag)] = value
    # end for ... loop over input dict items
    return r_collect
#end def dict_expand()

# Return dict d_visit that identifies specific paths in the input xml files that include nodes
# with information of interest to visit to seek nodes with values to save to relational db files.
# Returns also d_tag_output - a dictionary that indicates for node tags among those
# for in the d_visit dictionary, those whose data must be outputted, and an indication of whether the
# node is single-occurrence or multiple-occurence, which dictates how its data should be output.
def get_d_visit(d_nsmap):
    if d_nsmap is None:
        return None
    # d_abbr_collect is a dictionary of tag names (with abbreviations for namespaces)
    # following the root tag name that leads down to nodes whose
    # data is to be collected into db tables.
    # It may be better named d_node_visit if refactored.
    d_abbr_visit0 = {
         "coredata" : {
            "pii": None
            ,"openaccess": None
            }
        ,"originalText" : {
            "xocs:doc": {
                 "xocs:serial-item" : {
                       "ja:simple-article" : {
                             "ja:simple-head"    : {
                                   "ce:author-group"  : {
                                          "ce:affiliation" : {
                                            "ce:textfn" : None
                                          }
                                         ,"ce:author" : {
                                                "ce:given-name" : None
                                               ,"ce:surname" : None
                                               ,"ce:cross-ref" : None
                                          }
                                    }
                              }
                       }
                 }
            }
        }
    }

    # d_abbr_visit is used to select nodes to visit, while
    # d_abbr_tag_output tells how to treat/create output file(s) for various tags
    # of interest encountered during the visits
    d_abbr_visit = {
        'full-text-retrieval-response' : {
             "coredata" : {
                "pii": None
                ,"openaccess": None
                ,"prism:publicationName":None
                ,"prism:coverDate":None
                ,"dc:title":None
                }
            ,"originalText" : {
                "xocs:doc": {
                     "xocs:serial-item" : {
                           "ja:simple-article" : {
                                 "ja:simple-head"    : {
                                       "ce:author-group"  : {
                                          "ce:affiliation" : None
                                         ,"ce:author" : None
                                       }
                                  }
                           }
                     }
                }
            }
        }
    }

    # d_analysis and d_author_group are Not implemented..
    # as d_xpath_analysis with xpath expresions instead of node names is
    # more promising to do next to replace the functionality of the pair of datastructures
    # named d_abbr_visit and d_abbr_tag_output...

    d_author_group = {'multiple':1, 'attrs':'id',
        'nodes': {
            'ce:affiliation':{'multiple':1, 'attrs':'id',
                'nodes':{
                    'ce:textfn':{'multiple':0, 'name':'affil_name', 'text':True
                        ,'derivations' : {'uf':uf_affiliation_value}
                    }
                }
            }
            ,'ce:author':{'multiple':1, 'attrs':'id',
                'nodes':{
                    'given-name':{'multiple':0, 'text':True }
                    ,'surname':{'multiple':0, 'text':True}
                }
            }
        }
    }
    d_analysis = {
        'full-text-retrieval-response' : {
            'nodes' : {
                "coredata" : {
                    'nodes': {
                        "pii": { 'multiple':0, 'text': True  }
                        ,"openaccess": {'multiple':0 }
                        ,"prism:publicationName":{'multiple':0, 'text': True}
                        ,"prism:coverDate":{'multiple':0, 'text': True}
                        ,"dc:title":{'multiple':0, 'text': True}
                    }
                }
                ,"originalText":{
                    'nodes': {
                        "xocs:doc":{
                            'nodes': {
                                 "xocs:serial-item":{
                                    'nodes': {
                                        "ja:simple-article":{
                                            'nodes':{
                                                "ja:simple-head" :{
                                                    'nodes':{
                                                       "ce:author-group":d_author_group
                                                    }
                                                }
                                            }
                                        }
                                    }
                                 }
                                 , "xocs:nonserial-item": { #some PII values starting with B have this
                                     'nodes':{
                                        "fb-non-chapter": {
                                            'nodes':{
                                                'ce_author-group':d_author_group
                                            }
                                        }
                                     }
                                 }
                            }
                        }
                    }
                }
            }
        }
    }

    d_xpath_xanalysis = {
         'full-text-retrieval-response' : {
            'xpaths' : {
                       ".//pii": { 'multiple':0, 'text': True  }
                        ,".//openaccess": {'multiple':0 }
                        ,".//prism:publicationName":{'multiple':0, 'text': True}
                        ,".//prism:coverDate":{'multiple':0, 'text': True}
                        ,".//dc:title":{'multiple':0, 'text': True}
                }
                ,"originalText":{
                    'nodes': {
                        "xocs:doc":{
                            'nodes': {
                                 "xocs:serial-item":{
                                    'nodes': {
                                        "ja:simple-article":{
                                            'nodes':{
                                                "ja:simple-head" :{
                                                    'nodes':{
                                                       "ce:author-group":d_author_group
                                                    }
                                                }
                                            }
                                        }
                                    }
                                 }
                                 , "xocs:nonserial-item": { #some PII values starting with B have this
                                     'nodes':{
                                        "fb-non-chapter": {
                                            'nodes':{
                                                'ce_author-group':d_author_group
                                            }
                                        }
                                     }
                                 }
                            }
                        }
                    }
                }
            }
        }


    # Dict d_abbr_tag_output has key tagnames with namespace abbreviation (nsa) format, where value
    # is 1 if the tag can be multiple occurrence, 0 if single occurence.
    # NOTE: xml_node_visit issues a fatal exception if a single-occurrence tag is found with an index of 2.
    # NOTE: because a convention is used in d_visit such that if a node value is None, then ALL descendent nodes
    # are also to be collected, the tag_names in d_tag_output can include node names of some of those descendents,
    # and hence such names will not also appear in d_visit.
    # 20160808t1441 - add 'attrs', a list of mandatory/allowable attribute names per tag,
    # because some are optional to appear across files in a sample batch, and we must keep column name set
    # consistent for each row of output.
    # Compare 'attrs' list with below 'text' boolean whether to provide a text value per relation row (regardless of whether it
    # is found to be non-null for a tag)
    d_abbr_tag_output = {
          "doc" : { 'multiple':1 }
        # retiring this as an output because now meta node is supported of 'doc'
        # , "full-text-retrieval-response" : { 'multiple':0, 'name':'article', 'text':False }
        , "pii" : { 'multiple':0, 'text': True  }
        , "openaccess" : {'multiple':0 }
        , "ce:author-group": {'multiple':1, 'attrs': 'id' }
        , "ce:affiliation": {'multiple':1, 'attrs': 'id' }
        , "ce:author" : {'multiple':1, 'attrs': 'id'}
        , "ce:given-name": {'multiple':0, 'text': True }
        , "ce:surname": {'multiple':0, 'text': True  }
        , "ce:cross-ref": {'multiple':1, 'text': True ,'attrs':'refid'}
        , "ce:textfn": {'multiple':0, 'name': 'affiliation-name', 'text': True
                       ,'derivations':{'uf':uf_affiliation_value} }
        #, "scopus-eid": {'multiple':0, 'text': True}
        , "prism:publicationName": {'multiple':0, 'text': True}
        , "prism:coverDate": {'multiple':0, 'text': True
                             ,'derivations':{'coverYear':cover_year}}
        , "dc:title": {'multiple':0, 'text': True}
    }
    #

    return (
        dict_expand(d_input=d_abbr_visit, d_nsmap=d_nsmap, recurse=True)
        , d_abbr_tag_output
        , dict_expand(d_input=d_abbr_tag_output, d_nsmap=d_nsmap, recurse=False)
        )

#end def get_d_visit()

'''
xml_node_visit: visit a node of an xml tree

Argument d_visit, if the value not None, is given to filter the child tag names under this node
to visit. However if d_vist is None, then visit all nodes under
this node in the hierarchy.

Argument d_url_nsa is used to encode 'curly namespaces urls' to namespace
abbreviations to make the 'column names' of the xml data shorter and amenable
to column naming rules of many database systems.

Note: argument od_parent_index has values() do NOT include the index for this child itself,
but it is given in another argument, node_index.
Also consider argument od_parent_index, with method keys() that lists the db_tag (cleaned
tag name) value only for the parents of this node.
Code herein derives the db_tag 'cleaned' value for this node.tag value.

'''
def xml_node_visit(od_relation=None, output_folder=None
    ,d_visit=None, od_parent_index=None, node_index=None
    , node=None, d_url_nsa=None
    , d_tag_output=None, d_abbr_tag_output=None, output_file=None):

    me='xml_node_visit()'
    log_messages=[]

    if (node is None or node_index is None or d_url_nsa is None
        or od_parent_index is None or d_tag_output is None
        or output_file is None or od_relation is None
        or output_folder is None):
        msg = (
          "BAD:od_parent_index={},node={},d_url_nsa='{}',d_tag_output={},output_file={},od_relation={}"
          .format(repr(od_parent_index),repr(node),repr(d_url_nsa)
                ,repr(d_tag_output),repr(output_file),repr(od_relation)))
        raise RuntimeError(msg)
        return None

    verbose = 1

    msg = ("{}:STARTING: at node.tag={}".format(me, node.tag))
    if verbose and 1 == 2:
        print(msg)
        log_messages.append("{}:Arg d_visit={}".format(me,repr(d_visit)))

    node_db_tag = xml_tag_to_db_tag(d_url_nsa=d_url_nsa, tag=node.tag, use_nsa=False)

    if verbose and 1 == 2:
        print("using node_db_tag={}".format(node_db_tag))

    d_output_values = d_tag_output.get(node.tag, None)

    if verbose and 1 == 2:
        print("{}: Node.tag={} got d_output_values={}".format(me,node.tag,repr(d_output_values)))

    if d_output_values is None:
        # print("Node db tag={} has no output values".format(node_db_tag))
        multiple = None
        output_tag = None
        d_derivations = None
    else:
        multiple = d_output_values['multiple']
        #print("{}: Using node_db_tag={} with multiple={}".format(me,node_db_tag,repr(multiple)))
        output_tag = d_output_values.get('name', None)
        d_derivations = d_output_values.get('derivations', None)

    node_output_tag = output_tag if output_tag is not None else node_db_tag

    if verbose and 1 == 2:
        print('node_output_tag={}, multiple={},derivations={}'
              .format(repr(node_output_tag),repr(multiple),repr(derivations)))
    if multiple == 0 and node_index > 1:
        raise RuntimeError(
            "Node output tag='{}' is of multiple = 0, yet index is > 1. Error."
            .format(node.tag))

    # Only if this node has a multiple, we want some output from it, so we include it as a parent.
    if multiple is not None:
        od_child_parent_index = OrderedDict(od_parent_index)
        od_child_parent_index[node_output_tag] = node_index
    else:
        # do not append this node's index to the parent node stack
        od_child_parent_index = od_parent_index

    od_row = OrderedDict()
    if multiple is not None:
        # This node has a 'multiple' setting so we will write (from here or from a parent) this
        # node's data to the output_file.
        # If it is  multiple == 1, (it may have multiple occurences within the parent node)
        # we output the node value(s) here with the given occurrence index,
        # But if it is multiple == 0, a single value, we populate od_row of key-value pairs here
        # to be returned to the parent for future file writing.
        #

        # log_messages.append("{}:using db_tag={}".format(me,repr(db_tag)))
        if multiple == 0:
            # For multiple 0, we'll simply store any specified node values in od_row to return to parent
            if d_output_values.get('text', True) == True:
                # Only output the node's text value if 'text' is True.
                node_text = "" if node.text is None else node.text.strip()
                od_row["{}_text".format(node_output_tag)] = node_text
        else:
            # multiple must be 1, so we will output a file output line in this method
            output_line = ''
            output_line = node_output_tag

        # Add check later for dup names of attribs and or may later here convert to db_tag
        # Add attributes columns.
        for attr_name, attr_value in node.attrib.items():
            # Prepend the attribute name with node name to aid in distinghuishability
            od_row['{}_{}'.format(node_output_tag, attr_name)] = attr_value.strip()

        # Allow multiple attr_names later, but for now we only need one, so not supporting list of multiple
        # comma-separated names yet. But this would be where to do it.
        attr_name = d_output_values.get('attrs', None)
        if attr_name is not None:
            colname = '{}_{}'.format(node_output_tag, attr_name.strip())
            # Make sure this row includes mandatory attribute with empty value if one is
            # not already present.
            od_row[colname] = od_row.get(colname, "")

        # Also add any derived column names and values
        d_derivations = d_output_values.get('derivations', None)
        if d_derivations is not None:
            for colname, function in d_derivations.items():
                od_row[colname] = str(function(node_text)).strip()

    # Visit child nodes for any specified file output and/or returned od_row values
    # Keep track of child_tag index/counts as we go through this loop of child nodes.
    # We will have to give the child its own index as an argument to xml_node_visit().
    # d_child_tag_index{} keeps track of multiple child tag occurrences values
    d_child_tag_index = {}
    od_child_row = None
    #print("{}: {} has {} child nodes to try.".format(me,node_db_tag,len(node)))
    for child in node:
        #print("{}: child.tag to try is {}".format(me,child.tag))
        # Only bother to visit nodes specified in d_visit dictionary
        if d_visit is not None:
            # This is a child node to be visited, so we need to track its index
            #print("{}: testing child tag against tags in d_visit={}".format(me,repr(d_visit)))
            try:
                d_child = d_visit[child.tag]
            except KeyError:
                # This tag is not to be visited, so just skip it
                #print("child.Tag {} is not to be visited".format(child.tag))
                continue
        else:
            # d_visit is None, and None value for d_child is a sentinel that all xml tags
            # below this one are to be visited. So also set d_child to None.
            d_child = None
        #print("{}: child.tag = {} will be visited".format(me,child.tag))

        #Set this child's child_node_index within this loop
        child_node_index = d_child_tag_index.get(child.tag, 0)
        child_node_index += 1
        d_child_tag_index[child.tag] = child_node_index

        # log_messages.append("Using child.tag={}, d_child={}".format(child.tag,d_child))
        #print("indexes={},i={}".format(repr(child_indexes), i))
        sub_messages, od_child_row = xml_node_visit(od_relation=od_relation
            , output_folder=output_folder
            , d_visit=d_child, od_parent_index=od_child_parent_index
            , node_index=child_node_index
            , node=child, d_url_nsa=d_url_nsa
            , d_tag_output=d_tag_output, d_abbr_tag_output=d_abbr_tag_output
            , output_file=output_file)

        # Append any returned child column-values into od_child_row
        if od_child_row is not None and len(od_child_row) > 0:
            od_row.update(od_child_row)

        log_messages.append({"xml_node_visit_2":sub_messages})
    # end loop through child nodes

    if multiple is not None:
        # This node has a 'multiple' setting so we will write this node's data to the output_file.
        # If it is  multiple == 1, (it may have multiple occurences within the parent node)
        # we output it here with its given occurrence index, but if it is multiple == 0, a single value,
        # we populate a dictionary of key-value pairs to be output for the parent node caller
        #
        # For multiple == 0 we output the d_row from the child results here (because what is in d_row for a child
        # will only be single-occurence nodes that we can translate into column values here at the parent output

        if multiple  == 1:
            # We will output a file row from this method
            # Start off the output line with the database relation name of the output row.
            # Just use the node_db_tag name as the relation(table) name.
            output_line = node_output_tag

            # Output the group of column names for this relation's row.
            # Start with the parent relation names. This is a hierarcy of tags per the xml structure
            # but using only the tags(columns) of interest that we want to output.
            # Append each name with an 'i' for index. Using 'i' instead of 'id', a common attribute name
            # in xml files, might avoids some confusion among the column names.
            # print("db_tag={}".format(db_tag))

            for column_name in od_parent_index.keys():
                # Do not alter the column name here to keep compatible with sql server colum names
                output_line += ("\t{}".format(column_name))

            # Here, also output this tag's db-destined name
            output_line += "\t{}".format(node_output_tag)

            for key in od_row.keys():
                # d_row keys are from node.tags, which include the long curly-http namespace names,
                # so we 'clean' them first before outputting as a db column name
                clean_key = xml_tag_to_db_tag(d_url_nsa=d_url_nsa, tag=key, use_nsa=False)
                output_line += "\t{}".format(clean_key)

            # If this rel name (node_db_tag) is not yet in od_relation, store schema info for it.
            od_rel_info = od_relation.get(node_db_tag,None)
            if od_rel_info is None:
                od_rel_info = OrderedDict()
                od_relation[node_db_tag] = od_rel_info
                # Writable output file for this relationmode='w', encoding='utf-8'
                # SQL server 2008 bulk insert chokes on utf-8, so write this to ascii
                od_rel_info['db_file'] = open('{}/{}.txt'.format(output_folder,node_db_tag)
                                              , mode='w', encoding='utf-8')
                # Column names of data we will output for this relation
                od_column = OrderedDict()
                od_rel_info['columns'] = od_column

                # Use this to store field to index - consider future
                # Ex., might index each parent index, or each successive composite set of columns
                # od_index = OrderedDict()

                #od_rel_info['indexes'] = od_index
                # Use this for foreign keys - consider future
                #od_fkey = OrderdDict()
                #od_rel_info['fkeys'] = od_fkey

                #Primary key value will be simple string of concatted column names
                od_pkey = OrderedDict()
                od_rel_info['pkey'] = ""

                pkey_columns = ""
                sep = ''
                for column_name in od_parent_index.keys():
                    od_column[column_name] = 'integer'
                    pkey_columns += "{}{}".format(sep,column_name)
                    sep = ','

                pkey_columns +="{}{}".format(sep,node_output_tag)

                od_rel_info['pkey'] = pkey_columns

                #Column for this node index
                od_column[node_output_tag] = 'integer'

                # Make column names for this node's attributes
                # FIX: include attrib names from specified attrs
                # Singleton child attribute column names
                for column_name in od_row.keys():
                    clean_column = xml_tag_to_db_tag(d_url_nsa=d_url_nsa, tag=column_name, use_nsa=False)
                    od_column[clean_column] = 'nvarchar(2550)'

            # end of attribute/column names portion of the output line.
            # Write tab-separated db_line for dbfile


            dbfile = od_rel_info['db_file']


            # FINAL SECTION OF OUTPUT LINE - output the values matching the columns
            sep = ''
            db_line = ''
            for parent_index in od_parent_index.values():
                db_line += ("{}{}".format(sep,parent_index))
                sep = '\t'

            # Now, output the index value for this node.
            # It identifies a row for this node.tag in this relation among all rows outputted.
            # It is assigned by the caller via an argument, as the caller
            # tracks this node's count/index value as it scans the input xml document.
            db_line +=  ("{}{}".format(sep,node_index))
            #print("DEBUG:{}:db linenode_output_tag={}, node_index={}".format(me,node_output_tag,node_index))

            for value in od_row.values():
                db_line += ("\t{}".format(str(value).replace('\t',' ')))

            #Output a row in the db file
            print('{}'.format(db_line), file=od_rel_info['db_file'])

            # Output a database relation line in main outfile efor this node's text and attribute values
            output_line = output_line + '\t' + db_line
            # Retire/replace this one-file-output approach with individual relation output files.
            # print("{}".format(output_line), file=output_file)
            # set d_row to None to prevent parent from also outputting it
            od_row = None
        # end if multiple == 1 # we will output a file line with data for this node
        # else: we just return d_row
    # end optional output depending on 'multiple' value

    return log_messages, od_row
# end def xml_node_visit():

'''
Method elsevier_xml_tsv: from given xml file(eg, an elsevier full text retrieval apifile),
create some indexed relational data and output some tab separated value files.
'''
def elsevier_xml_tsv(od_relation=None, output_folder=None
    ,input_file_name=None, file_count=None
        ,doc_root=None # doc element is meta element to use as root xml node per article/doc
        ,output_file=None, verbosity=0):
    me = 'elsevier_xml_tsv()'
    #print("{}: Starting with input_file_name={},file_count={},doc_root={},output_file={}"
    #      .format(me,input_file_name,repr(file_count),repr(doc_root),output_file))
    log_messages = []
    full_api_failure = 0


    if (input_file_name is None or output_file is None or output_folder is None
        or file_count is None or doc_root is None or od_relation is None):
        msg = ("Missing input file_name, output_file,file_count or doc_root. Bad arguments.")
        log_messages.append(msg)
        print(msg)
        raise Exception("{}:bad arguments. {}".format(me,msg))
        return log_messages, None, None
    msg = "{}:Using input_file_name='{}'".format(me, input_file_name)
    log_messages.append(msg)
    # print(msg)

    # (1) Read an elsevier input xml file to variable input_xml_str
    # correcting newlines and doubling up on curlies so format() works on them later.
    with open (str(input_file_name), "r") as input_file:
        input_xml_str = input_file.read().replace('\n','')

    # (2) and convert input_xml_str to a tree input_doc using etree.fromstring,
    if input_xml_str[0:9] == '<failure>':
        # This is a custom check for a 'bad' xml file common to a particular set of xml files.
        # This skipping is not generic feature of this method.
        # print("This xml file is a <failure>. Skipping it.")
        log_messages.append("<failure> input_file {}.Skip.".format(input_file_name))
        return log_messages, None, None

    try:
        tree_input_doc = etree.parse(input_file_name)
    except Exception as e:
        msg = (
            "Skipping exception='{}' in etree.fromstring failure for input_file_name={}"
            .format(repr(e), input_file_name))
        #print(msg)
        log_messages.append(msg)
        return log_messages, None, None

    # GATHER STATISTICS FOR THIS PII/ARTICLE FROM ITS FULL-API XML TREE
    try:
        input_node_root = tree_input_doc.getroot()
    except Exception as e:
        msg = ("Exception='{}' doing getroot() on tree_input_doc={}. Return."
                .format(repr(e),repr(tree_input_doc)))
        #print(msg)
        log_messages.append(msg)
        return log_messages, None, None

    doc_root.append(input_node_root)
    # do not put the default namespace (as it has no tag prefix) into the d_namespaces dict.
    d_nsmap = dict(input_node_root.nsmap)
    d_namespaces = {key:value for key,value in d_nsmap.items() if key is not None}

    d_url_nsa = {value:key for key,value in d_namespaces.items()}

    #print("{}:Using d_url_nsa='{}' node.tag={}".format(me,repr(d_url_nsa),input_node_root.tag))
    # Now using 'doc' special metaroot, so can set db_tag explicitly
    # db_tag = xml_tag_to_db_tag(d_url_nsa=d_url_nsa, tag=input_node_root.tag)
    db_tag = doc_root.tag

    # parents.append(xml_tag_to_db_tag(d_url_nsa=d_url_nsa, tag=input_node_root.tag))
    # Using arg d_nsmap so that it has key of None with default namespace, needed by get_visit

    # Get some dictionaries to help xml_node_visit decode and output tag names
    d_visit, d_abbr_tag_output, d_tag_output = get_d_visit(d_nsmap=d_nsmap)

    msg = ("{}: Got d_visit='{}', d_tag_output= len={}"
          .format(me, repr(d_visit), repr(d_tag_output)))
    #print(msg)
    #log_messages.append(msg)

    # OrderedDict with key of parent tag name and value is parent's index among its siblings.

    od_parent_index = OrderedDict()
    #od_parent_index['doc'] = file_count
    node_index = file_count

    # In this scheme, the root node always has multiple = 1 - that is, it may have multiple
    # occurences, for example, over a set of files.
    # Also, this program requires that it be included in the relational output files.
    multiple = 1
    # Visit the xml tree nodes to produce database table output
    #
    sub_messages, d_row = xml_node_visit(od_relation=od_relation
        , output_folder=output_folder
        , d_visit=d_visit, od_parent_index=od_parent_index
        , node_index = node_index
        , node=doc_root
        , d_url_nsa=d_url_nsa
        , d_tag_output=d_tag_output, d_abbr_tag_output=d_abbr_tag_output
        , output_file=output_file)

    log_messages.append({"xml_node_visit_1" : sub_messages})
    #

    return log_messages
# end def elsevier_xml_tsv():

'''get_uf_affil_patterns
'''
import re
def get_uf_affil_patterns(l_regex=None):
    if l_regex is None:
        return None
    patterns=[]
    for regex in l_regex:
        patterns.append(re.compile(regex, re.IGNORECASE))
    return patterns

def uf_affiliation(text=None, patterns=None):
    if not (text and patterns):
        return None
    for p in patterns:
        if p.search(str(text)) is not None:
            return(True)
    return False

def uf_affiliation_value(text):
    text_lower = text.lower()
    #print("Using affil argument text={}".format(repr(text)))
    for match in ['university of florida','univ.fl','univ. fl'
        ,'univ fl' ,'univ of florida'
        ,'u. of florida','u of florida']:
        if text_lower.find(match) != -1:
            #print("Match")
            return 1
    #print("NO Match")
    return 0
def cover_year(text):
    return(text[0:4])
# Method to manage output folders and params to invoke statistics collection at the article/file level,
# accrue the statistics, and do a special case analysis of ce_text_fn to evaluate whether an article
# is affiliated  with UF.
def elsevier_xml_path_list_stats(
      d_pii_bibvid=None
    , input_path_list=None
    , output_folder=None
    , use_db=None
    , file_count_first = 0
    , file_count_span = 1
    , only_ufdc_articles=True
    , output_name_suffix=''
    , verbosity=1
    ):
    me = "elsevier_xml_path_list_stats"
    if not (input_path_list and output_folder and d_pii_bibvid):
        raise Exception("Bad juju!")
        return None

    log_messages = []
    msg="{}:START with file_count_first={}".format(me, file_count_first)
    vid_int = 1 # Now a normal new vid_int is 00001, but a stored one may be different.
    max_files_processed = 0

    outputted = 0
    total_api_failures = 0

    count_piis_ufdc_pending = 0
    count_piis_elsevier_sent_uf = 0
    count_piis_in_ufdc = 0
    count_piis_elsevier_uf_search_results=0
    count_piis_tried_read = 0
    count_piis_tried_stats = 0
    count_piis_sampled_articles = 0
    count_piis_full_api_failures = 0
    count_affiliations_uf = 0
    count_affiliations_not_uf = 0

    # count of piis for which the analysis examines the Results of the Elsevier 'full text' API
    count_piis_examined_full = 0
    max_input_files = 0

    # Dictionary with output relation name key and value is dict with row keys, values maybe types later
    od_relation = OrderedDict()

    # NOTE: the tag_names and multi_tag_names might better be managed as arguments to this method
    # rather than set here directly.
    # TODO: consider to add supporting code and data for entry_tag_names ("entry": for the
    # "Elsevier Search API" results) and entry_multi_tag_names
    # to look in the 'search entry' api results if the full results are <failure> results....
    # This is the case for many UFDC bibvids, that were admitted to ufdc based on the entry xml before we started
    # using the full xml, which is more restricted, I think in Julu 2016 when Elsevier realized their entry-search API
    # gave us non-UF article info by mistake, but not before we put many of those articles into UFDC.

    tag_names = ['.//xocs:pii-unformatted'
        ,'.//ce:textfn']
    '''
        , './/xocs:cover-date-year', './/{*}openaccess', './/dc:title', './/ce:title', './/dc:identifier'
        , './/prism:doi' ,'.//prism:publicationName','.//prism:url', './/prism:coverDate'
        , './/openaccess','.//{*}eid'
        ,'.//xocs:cover-date-start','.//xocs:cover-date-end', './/xocs:copyright-line'
        ]'''

    multi_tag_names = ['.//ce:author-group//ce:textfn/text()'
        ,'.//sa:organization/text()'
        ,'.//ce:author-group//ce:surname/text()'
        ,'.//ce:author-group//ce:given-name/text()'
        ,'.//ce:author-group//ce:author/@id'
        ,'.//ce:surname' ]

    re_patterns = get_uf_affil_patterns([
         '.*university of florida.*'
        ,'.*univ[.]fl.*'
        ,'.*univ fl.*'
        ,'.*univ of florida.*'
        ,'.*u. of florida.*'
        ,'.*u of florida.*'
        ])
    msg = ('{}:got re_patterns={}'.format(me,repr(re_patterns)))
    #print(msg)
    d_msg =  {'uf_affiliation_regular_expressions' : repr(re_patterns)}
    log_messages.append(d_msg)

    # Create collection mtag dicts to accrue multi-tag occurrence info from individual files.
    l_collect_multi_dicts = []
    for i in enumerate(multi_tag_names):
        l_collect_multi_dicts.append(OrderedDict())

    # Make 'generic' simpler versions of tag names limited to a smaller, more standard, set of symbols
    # that a spreadsheet or other popular programs or databases may accept as db column or field names.

    tag_names_generic = [tag_generic(x) for x in tag_names]

    #Append more 'metadata' for this article.
    tag_names_generic.append('pii')
    tag_names_generic.append('bibvid')
    tag_names_generic.append('uf-affilation')
    log_messages.append({'article-single-occurrence-tags' : repr(tag_names_generic)})

    # print("Seeking ordered single-occurrence xml 'full api' tag names: {}".format(tag_names))

    multi_tag_names_generic = [tag_generic(x) for x in multi_tag_names]
    #print ("Seeking ordered multiple-occurrence xml 'full api' tag names:{}".format(multi_tag_names))
    log_messages.append({'article-multiple-occurrence-tags':repr(multi_tag_names_generic)})

    row_index = 0

    # Output dictionary d_index_tag_values will hold in the first item, a key of row index 0,
    # the names of the tags in order given in tag_names list.
    # Subsequent rows will hold the values for the tags, in order.
    # For example row['1'] will hold the ordered values for the tag names found in the first acceptable
    # file found in the following loop.
    od_index_tag_values = OrderedDict()
    od_index_tag_values[str(row_index)] = tag_names_generic

    # Define output dictionary d_mtag_dicts - is keyed by a multi_tag_name, and the value is a dictionary,
    # where that dictionary has key of index (occurence count) of that multi tag name in the
    # input file and the value is the value for that occurrence count.
    d_index_mtag_dicts = {}
    d_pii_uf={}
    output_filename = "{}/db_xml.tsv".format(output_folder)
    msg = ("Database output file name: {}".format(output_filename))
    log_messages.append(msg)
    print(msg)
    ##########################################################################################
    with open(output_filename, mode='w', encoding='utf-8') as output_file:
        # Caller has already slided input_path_list with first 'real file count'
        # value being file_count_first. So in the for loop, add i to file_count_first to
        # get the file_count amont a master list of paths.
        for i, path in enumerate(input_path_list):
            if (max_input_files > 0) and ( i >= max_input_files):
                log_messages.append(
                    "Max number of {} files processed. Breaking.".format(i))
                break;

            file_count = file_count_first + i

            # Full aboslute path of input file name is as follows:
            input_file_name = "{}/{}".format(path.parents[0], path.name)
            batch_size = 100
            if batch_size > 0  and (i % batch_size == 0):
                file_sample = 1
            else:
                file_sample = 0
            if (file_sample):
                utc_now = datetime.datetime.utcnow()
                utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")
                msg = ("{}: Processed through input file count = {} so far."
                       .format(utc_secs_z, file_count))
                print(msg)
                #log_messages.append(msg)

            # get pii from filename in folder full: pii_the-pii-value.xml
            # or in folder entry: entry_the-pii-value.xml
            dot_parts = path.name.split('.')
            bar_parts = dot_parts[0].split('_')
            pii = bar_parts[1]

            sub_messages, bibvid = get_bibvid(
                pii.upper(), d_pii_bibvid, verbosity=0)

            if len(sub_messages) > 0 and False:
                if len(sub_messages) > 1:
                    log_messages.append({'get-bibvid-messages':sub_messages})
                else:
                    log_messages.append({'get-bibvid-message':sub_messages[0]})
            # new_bibid_int += made_bibid_int

            # Increment the count of piis that elsevier has ever sent uf for uf authors...
            count_piis_elsevier_uf_search_results += 1

            if not bibvid or bibvid == '' :
                count_piis_ufdc_pending +=1
                if only_ufdc_articles:
                    # skip this pii if bibvid not in dict, and so we assume it is not in ufdc
                    log_messages.append("PII={} not in UFDC with a bibvid. Skipping.".format(pii))
                    continue

            if verbosity > 2:
                log_messages.append("For input file {} = {} for pii='{}', using bibvid={}"
                  .format(i, path.name, pii, bibvid))

            # Try to read the article's input full-text xml file and accrue its statistics
            count_piis_tried_read += 1
            with open(str(input_file_name), "r") as input_file:
                try:
                    input_xml_str = input_file.read().replace('\n','')
                    # print("### Got input_xml_str={}".format(input_xml_str))
                except Exception as e:
                    if 1 == 1:
                        log_messages.append(
                            "\tSkipping read failure {} for input_file_name={}"
                            .format(e,input_file_name))
                    count_piis_full_api_failures += 1
                    continue

            #print("\n\nINDEX: For input file index={}, name={}".format(i,input_file_name))
            if verbosity > 1:
                #log_messages.append("Calling elsevier_xml_file_stats to process input file[{}], name={} "
                # .format(str(i+1),input_file_name))
                pass

            ################# CALL ELSEVIER_XML_FILE_STATS #####################################

            count_piis_tried_stats += 1

            sub_messages, l_tag_values, l_mtag_dicts = elsevier_xml_file_stats(
                input_file_name=input_file_name
                , tag_names=tag_names, multi_tag_names=multi_tag_names
                , verbosity=verbosity)

            ######################################################################################

            if len(sub_messages) > 0 and False:
                log_messages.append({'elsevier-xml-file-stats':sub_messages})

            if l_tag_values is None:
                # The full api file for this PII could not be processed, so count the failure and skip it.
                count_piis_full_api_failures += 1
                # msg was already lodged for failure: log_messages.append("No stats in {}. Skip.".format(path.name))
                continue


            # Here, we have succeeded to sample the metadata of the input xml file for this pii
            count_piis_sampled_articles += 1
            row_index += 1

            # First append special stat values for the article that we insert here,
            # and we inserted on tag_names_generic
            l_tag_values.append(pii)
            l_tag_values.append(bibvid)
            # print("\n\nFor file index={}, got l_tag_values={}".format(i,repr(l_tag_values)))

            # Accrue the l_tag_values output into a collecing dictionary keyed by the row/count
            # within sampled input files
            od_index_tag_values[str(row_index)] = l_tag_values
            #print("elsevier_path_list_stats: saved l_tag_values='{}' in dict key index={}".format(repr(l_tag_values),row_index))

            # Accrue each of the l_mtag_dicts, of od_index dictionaries into the collecting dictionary for this mtag:
            for i2, mtag in enumerate(multi_tag_names_generic):
                # For the pii of this article, and multi-tag, save its dict with key occurrence number,
                # and value of the tag.
                od_collect = l_collect_multi_dicts[i2]
                # For this pii key, store value of a dict whose key is index/occurrence of this
                # multi_tag_name and whose value is that occurrence's value.
                od_collect[pii] = l_mtag_dicts[i2]
                # print("pii={}, for multi-tag={},storing l_mtag_dict={}".format(pii,mtag,repr(l_mtag_dicts[i])))

            # Here, we have succeeded to sample the metadata of  the input xml file for this pii
            count_piis_examined_full += 1

            try:
                name = 'ce_author_group__ce_surname_text()'
                tag_idx = multi_tag_names_generic.index(name)
            except Exception as e:
                print("multitag name={} is not in '{}'".format(name,multi_tag_names_generic))

            # Special case: do special analysis for ce_text_fn - to determine whether the subject
            # article has a "UF-Affiliation".
            tag_idx = multi_tag_names_generic.index("ce_author_group__ce_textfn_text()")
            # ? d_pii_d_idx_textfn = l_collect_multi_dicts[tag_idx]

            d_idx_textfn = l_mtag_dicts[tag_idx]

            l_uf_indexes = []

            for idx, textfn in d_idx_textfn.items():
                if uf_affiliation(text=textfn, patterns=re_patterns) == True:
                    #print("{}: file_count={}, pii={},idx={} of {}, Affil textfn='{}' match is True"
                    #      .format(me, file_count,pii,idx,len(d_idx_textfn),textfn))
                    l_uf_indexes.append(idx)
                else:
                    #print("{}: file_count={}, pii={},idx={} of {}, Affil textfn='{}' match is False"
                    #      .format(me, file_count,pii,idx,len(d_idx_textfn),textfn))
                    pass

            # Append the uf-affiliation ordered value
            if len(l_uf_indexes) == 0:
                # print("{}:pii={} has no UF affiliation among {}!".format(me,pii,int(idx)+1))
                l_tag_values.append("No")
                count_affiliations_not_uf += 1
            else:
                l_tag_values.append("UF")
                count_affiliations_uf +=1

            ##################################################
            # Setup and call to xml_to_tsv....
            # ############ Produce output file for relational database data
            # First, use 'doc' as main ID (it could be from a file and API, maybe other source,
            # so call the main countable object a 'doc')
            # parents.append('doc')
            file_count = i + file_count_first
            doc_root = etree.Element("doc")
            doc_root.attrib['bibvid'] = str(bibvid)

            doc_root.attrib['filename'] = input_file_name #useful for diagnostics
            doc_root.attrib['uf_affil_count'] = str(len(l_uf_indexes))
            #NOTE: TODO: when implement d_analysis dict tree, set 'nodes' of doc_root to it..
            msg = ("{}:calling elsevier_xml_tsv with doc_root.tag={}, file_count={}"
              .format(me,doc_root.tag, file_count))
            #print(msg)
            sub_messages = elsevier_xml_tsv(od_relation=od_relation
                , output_folder=output_folder
                , input_file_name=input_file_name
                , file_count=file_count
                , doc_root=doc_root
                , output_file=output_file
                , verbosity=verbosity)

            if len(sub_messages) > 0 and False:
                log_messages.append({'elsevier-xml-tsv':sub_messages})
            ##################################################
            # May want populated dict someday? not now 2160725:
            # d_pii_uf[pii] = l_uf_indexes

            if verbosity > 2:
                log_messages.append( "Got stats for input file[{}], name = {}. \n"
                    .format(i+1, input_file_name)
                     )
            outputted += 1

        # end for i, fname in input_file_list
    # end with open() as output_file

    #############################################################################
    print('{}: Got od_relation={}'.format(me,repr(od_relation)))

    output_filename = "{}/sql_server_creates.sql".format(output_folder)
    bulk_filename = "{}/bulk_inserts.sql".format(output_folder)
    use_setting = 'use [{}];\n'.format(use_db)
    msg = ("Database output file name: {}".format(output_filename))
    log_messages.append(msg)
    print(msg)
    ##########################################################################################
    with open(output_filename, mode='w', encoding='utf-8') as output_file:
        print(use_setting,file=output_file)
        with open(bulk_filename, mode='w', encoding='utf-8') as bulk_file:
            print(use_setting,file=bulk_file)
            #TEST OUTPUT create table statements for sql server...
            for relation, info in od_relation.items():
                print('\ndrop table {};'.format(relation)
                     ,file=output_file)

                print('create table {}('.format(relation)
                     ,file=output_file)

                # SQL CREATE SYNTAX FOR COLUMNS
                sep = ''
                for column,ctype in info['columns'].items():
                    print('{}{} {}'.format(sep,column.replace('-','_'),ctype)
                        ,file=output_file)
                    sep = ','

                #PRIMARY KEY eg: CONSTRAINT pk_PersonID PRIMARY KEY (P_Id,LastName)
                print('CONSTRAINT pk_{} PRIMARY KEY({})'.format(relation, info['pkey'])
                     , file=output_file)

                #End table schema definition
                print(');\n', file=output_file)

                #bulk insert statement
                print("BULK INSERT {}".format(relation), file=bulk_file)
                print("FROM '{}/{}.txt'".format(output_folder,relation), file=bulk_file)
                print("WITH (FIELDTERMINATOR ='\\t', ROWTERMINATOR = '\\n');\n", file=bulk_file)

            # loop over relations
        #with bulk filename
    #with output filename...

    # Write stats for single occurrence tags
    stats_filename = '{}/stats_extstats{}.txt'.format(output_folder,output_name_suffix)
    with open(stats_filename, mode='w', encoding='utf-8') as outfile:
        delim ='\t'
        for i,(key,values) in enumerate(od_index_tag_values.items()):
            # We can ignore the key. It was just set to the row index value.
            # Output a new row of column/field/tag data for one of the articles
            line=''
            #print("od_index_tag_values, item={}. key='{}', value='{}'".format(i,key,values))
            for i,value in enumerate(values):
                line += delim if i else ''

                #print("i={}, value={}".format(i, repr(value)))
                line += '' if value is None else value
            # Line has concatenation of all tag values, now cap it with a newline for output.
            line += '\n'
            # Write as the binary utf-8 encoding
            outfile.write(line)
    count_input_files = i + 1

    # Write stats for collected multi-tag dictionary files
    for i, od_collect in enumerate(l_collect_multi_dicts):
        # write an output file for stats for this multi-tag
        multi_tag_name = multi_tag_names_generic[i]
        stats_filename = '{}/{}{}.txt'.format(output_folder, multi_tag_name,output_name_suffix)
        with open(stats_filename, mode='w', encoding='utf-8') as outfile:
            # column header line
            outfile.write('pii\tindex\t{}\n'.format(multi_tag_name))
            # for each entry, write the count-index, key_name key value (eg pii value), and the multi-tag value
            for pii, d_count_value in od_collect.items():
                line = ''
                for index,value in d_count_value.items():
                    line = "{}\t{}\t{}\n".format(pii, index, str(value))
                    # Write as the binary utf-8 encoding
                    outfile.write(line)
            # end for od.collect.items()
        # end with open...
    # end for l_multi_tag_dicts

    log_messages.append({"d_pii_uf":d_pii_uf})

    #print("Got d_index_tag_values='{}'".format(d_index_tag_values))
    d_statistics = {
          "count-input-files": count_input_files
        , "count-piis-ufdc-pending" : count_piis_ufdc_pending
        , "count-piis-examined-full": count_piis_examined_full
        , "count-piis-elsevier-uf-search-results" : count_piis_elsevier_uf_search_results
        , "count-piis-full-api-failures" : count_piis_full_api_failures
        , "count-piis-tried-read" : count_piis_tried_read
        , "count-piis-tried-stats" : count_piis_tried_stats
        , "count-piis-sampled-articles" : count_piis_sampled_articles
        , "count-affilitions-uf" : count_affiliations_uf
        , "count-affilitions-not-uf" : count_affiliations_not_uf
    }
    log_messages.append({"statistics": d_statistics})
    return log_messages, d_statistics, d_pii_uf, od_relation

# end def elsevier_xml_path_list_stats

# RUN PARAMS AND RUN
import datetime
import pytz
import os
from collections import OrderedDict

def extstats_run(elsevier_base=None, use_db='rvp_test', file_count_first=0, file_count_span=1):
    me = "extstats_run"
    print("extstats_run: STARTING")
    if not elsevier_base:
        return None

    # past ones 20160701 or so - until swap of machine, OU: 'c:/users/lib-adm-podengo/downloads/elsevier'

    d_log = OrderedDict()
    d_params = OrderedDict()
    d_params['folder-elsevier-base'] = elsevier_base

    # legacy value:
    # xslt_sources = ['full', 'entry', 'tested']
    # Select a source of input xml, also a specific  xslt transform is implied
    xslt_source_name='tested'

    # Reuse the 'source' name to also label output directory for results
    folder_output_base = '{}/output_extstats/{}'.format(elsevier_base, xslt_source_name)
    d_params['folder-output-base'] = folder_output_base

    only_ufdc_articles = False
    utc_now = datetime.datetime.utcnow()

    # Make date formats with utc time aka Zulu time, hence Z suffix.
    # On 20160209, this is the second 'edtf' format on the first bullet at
    # http://www.loc.gov/standards/datetime/, on the download of the PowerPoint
    # Presentation link: http://www.loc.gov/standards/datetime/edtf.pptx

    utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")
    # secsz_start = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")
    # We also use secsz_start as part of a filename, and windows chokes on ':', so use
    # all hyphens for delimiters
    secsz_start = utc_now.strftime("%Y-%m-%dT%H-%M-%SZ")
    secsz_dir = utc_now.strftime("%Y-%m-%dT%H-%M-%SZ")

    # Reuse the 'source' name to also label output directory for results
    folder_output_base = '{}/output_extstats/{}'.format(elsevier_base, xslt_source_name)

    os.makedirs(folder_output_base, exist_ok=True)

    #ORIG output_folder
    output_folder_secsz = '{}/{}'.format(folder_output_base, secsz_dir)
    os.makedirs(output_folder_secsz, exist_ok=True)

    # d_xslt = get_d_xslt()
    # xslt_format_str = d_xslt[xslt_source_name]
    # TODO: Get xslt_format_str in prettprint format and put to d_log

    # print ("Using xslt document='{}'".format(xslt_format_str))

    # Initialize input PII-BIBVID dictionaries/table of piis with bibvids already assigned in the SobekCM database.
    input_dict_folder = '{}/output_ebibvid'.format(elsevier_base)
    input_dict_pii_fn = "{}/dictionary_pii_bibvid.txt".format(input_dict_folder)
    d_params['file_input_dict_pii'] = input_dict_pii_fn

    print("{}:calling get_odict_pii_bibvid".format(me))
    od_pii_bibvid_messages, od_pii_bibvid = get_odict_pii_bibvid(input_dict_pii_fn)
    if len(od_pii_bibvid_messages) > 0:
        d_log["od-pii-bibvid-messages"] = od_pii_bibvid_messages
    if not od_pii_bibvid:
        d_log["od_pii_bibvid_error"] = "*** Bad dict in filename={}".format(input_dict_pii_fn)
        return None
    print("Using output folder={}".format(output_folder_secsz))

    # Set the first bibid_int that is available to assign for a new pii value.
    first_bibid_int = 9999999

    if 1 == 1 :
        # Get list of 'FULL-API' input files, or just first few for testing, from output_eatxml/full
        input_folder = '{}/output_eatxml/full/'.format(elsevier_base)
        print("For input folder={}, getting paths...".format(input_folder))
        input_head_path = Path(input_folder)

        # CHANGE NEXT ASSIGNMENT TO INPUT_FILE_LIST FOR PERIODIC API HARVESTER...
        # TO GET FROM GIT REPO THE LIST OF FILES CHANGED IN THE MOST RECENT COMMIT
        # REVIVE NEXT LINE AFTER TESTING...
        input_path_list =  list(input_head_path.glob('**/pii_*.xml'))
        print("Got {} files in the path".format(len(input_path_list)))

        input_low_index = file_count_first
        input_high_index = file_count_first + file_count_span

        # Use only a portion of the total input file list...
        lif = len(input_path_list)
        index_max = lif if input_high_index > lif else input_high_index

        #SLICE the input_path_list for analysis
        sliced_input_path_list = input_path_list[input_low_index:index_max]
        output_name_suffix="_{}_{}".format(input_low_index,index_max)

    os.makedirs(output_folder_secsz, exist_ok=True)
    skip_extant = False
    d_params.update({
         'python-sys-version': sys.version
        ,'secsz-1-start': secsz_start
        ,'output-folder': output_folder_secsz
        ,'input-dict-pii-filename': input_dict_pii_fn
        ,'input-dict-pii-len': str(len(od_pii_bibvid))
        ,'input-files-xml-folder' : input_folder
        ,'input-files-count': str(len(input_path_list))
        ,'bibid-first-new-int': str(first_bibid_int)
        ,'input-files-index-limit-1-low': repr(input_low_index)
        ,'input-files-index-limit-2-high': repr(input_high_index)
        ,'file-count-first': file_count_first
        ,'file-count-span': file_count_span
        ,'only-ufdc-articles' : repr(only_ufdc_articles)
    })

    d_log['run_parameters'] = d_params

    ################# READ THE INPUT, AND COLLECT AND OUPUT STATS ################
    print("{}:Calling elsevier_xml_path_list_stats".format(me))
    log_messages, d_stats, d_pii_uf, od_relation = (elsevier_xml_path_list_stats(
        d_pii_bibvid=od_pii_bibvid
      , input_path_list=sliced_input_path_list
      , only_ufdc_articles=only_ufdc_articles
      , output_folder=output_folder_secsz
      , use_db = use_db
      , file_count_first = file_count_first
      , file_count_span = file_count_span
      , output_name_suffix=output_name_suffix
      , verbosity = 0
    ))

    #Close all the output files in od_relation
    for relation, d_info in od_relation.items():
        file = d_info.get('db_file', None)
        if file is not None:
            file.flush()
            file.close()
    # too much memory consumed, so do not log this way... stream the logs like relational data rather
    # than create an in-memory dictionary...
    # d_log['path-list-stats'] = log_messages

    ######################################################################
    # Put d_log, logfile dict info, into xml tree,  and then OUTPUT logfile info
    # as an xml tree.

    secsz_finish = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
    d_log['run_parameters'].update({"secsz-2-finish": secsz_finish})

    e_root = etree.Element("uf-extstats")
    # add_subelements_from_dict(e_root, d_log)
    add_subelements(e_root, d_log)

    # log file output
    log_filename = '{}/log_extstats.xml'.format(output_folder_secsz)
    with open(log_filename, mode='w', encoding='utf-8') as outfile:
        pretty_log = etree.tostring(e_root, pretty_print=True)
        outfile.write(pretty_log.decode('utf-8'))
    return log_filename, input_path_list, pretty_log, d_pii_uf, od_relation
# end def extstats_run

# RUN the analysis and collect stats
log_filename, input_path_list, pretty_log, d_pii_uf, od_relation = extstats_run(
    elsevier_base='c:/rvp/elsevier'
    ,use_db='rvp_test'
    ,file_count_first=21000, file_count_span=3000)

print("Done.")
