# Create your views here.
from django.conf import settings
import maw_settings
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required

from .models import Bibvid, X2018Thesis, X2018Subject
from lxml import etree
########################### IMPORT
# NB; WARNING - canNOT use parens to make an import multiline in python
# yet. Must use bakslash.
from sqlalchemy_tools.core.import_selected_spreadsheet_to_table \
  import spreadsheet_to_table

#from sqlalchemy_tools.core import spreadsheet_to_table
from collections import OrderedDict
from sqlalchemy import (
  Boolean, create_engine,
  CheckConstraint, Column, Date, DateTime,Float, FLOAT, ForeignKeyConstraint,
  inspect, Integer,
  MetaData, Sequence, String, Table, Text, UniqueConstraint,
  )

'''
Method out_mets(request):

Read the contents of X2018Thesis and input the rows, each representing a uf
bibvid item, with some basic uf_bibivid info
and AI-supplied info exported from a XIS export of UF Electronic Theses and
Dissertatino (ETD) items that were
exported by Xiaoli Ma circa August 2018).

For each,
(1) retrieve and store in core the subjects data from table X2018Subject
    where 'keep' == 'y'.
(2) read the associated METS file in ufdc resources, parse with lxml and store
    the doc tree in local core.
    (a) If option reset_subjects = True, delete all current lxml nodes for subjects
    (b) insert all 'keep' subjects
(3) Generate a new output mets file for the item in an  output folder
    given by a django setting.py (which in turn is defined in the local
    maw_settings.py file on the instance of the Django MAW webserver):
'''

def mets_folder_by_bibvid(bibvid=None, verbosity= 0):
    pass
#end def

import os, sys

# def bibvid_resources_folder(bibvid=None, verbosity=0):
def mets_filename_by_bibvid(bibvid=None, verbosity=0):
    me = 'bib_resources_folder'
    bparts = bibvid.split('_')
    if len(bibvid) != 16 or len(bparts[0]) != 10 or len(bparts[1]) != 5:
        msg = f"{me}: bibvid='{bibvid}' has invalid format"
        raise ValueError(msg)

    kp_folder = maw_settings.DPS_UFDC_FOLDER + 'resources'
    for i in range(0, 9, 2):
        kp_folder += os.sep + bparts[0][i:i+2]
    kp_folder += os.sep + bparts[1]
    mets_file = kp_folder + os.sep + bibvid + '.mets.xml'
    if verbosity > 0:
        print(f"\n\n{me}:reading mets_file='{mets_file}'\n\n")
        sys.stdout.flush()

    return mets_file

'''
Method mets_root_by_bibvid(bibvid=None, verbosity=0)

For given bibvid, use DPS_UFDC_FOLDER as a base and construct the
keypair subfolder path, and read and parse the mets.xml file into
an lxml tree.

Return the root node
'''
def mets_docroot_by_bibvid(bibvid=None, verbosity=0):
    me = 'mets_root_by_bibvid'
    kp_folder = bib_resources_folder(bibvid=bibvid)
    filename = kp_folder + os.sep + 'mets.xml'
    docroot = None
    with open(filename, "r") as metsfile:
        pass
    return kp_folder
#end def
def get_tree_and_root_from_filename(filename=None, log_file=sys.stdout,
    verbosity=None):
    me = 'get_root_from_parsed_file_bytes'
    parser = etree.XMLParser(remove_comments=False)
    with open(filename, mode='rb') as input_bytes_file:
        try:
            tree = etree.parse(input_bytes_file, parser=parser)
        except Exception as e:
            log_msg = (
                "{}:Skipping exception='{}' in filename='{}'"
                .format(me, repr(e), filename))
            print(log_msg, file=log_file)
            return None, None
    # end with open
    return tree, tree.getroot()
#end def get_root_from_parsed_file
'''
Method out_mets()
'''
def out_mets(request):

    out_html = '<ol>'
    max_bibvids = 5
    od_bibvid = OrderedDict()
    # Retrieve the bibvid items from table Thesis.
    # Report and Skip any duplicate items.
    n_thesis = 0
    n_bad = 0
    for thesis in X2018Thesis.objects.all():
    #for thesis in Bibvid.objects.all():
        n_thesis += 1
        if n_thesis > max_bibvids:
            break;
        bibvid = thesis.uf_bibvid
        out_html += f"<li>{bibvid}</li><ol>"
        # Get the subjects
        n_subject = 0
        for subject in X2018Subject.objects.filter(thesis=thesis, keep='y'):
            n_subject += 1
            out_html += f"<li>{subject.term}</li>"
            pass

        mets_filename = mets_filename_by_bibvid(bibvid=bibvid, verbosity=1)
        tree, node_root = get_tree_and_root_from_filename(
            filename=mets_filename)
        if node_root is None:
            n_bad += 1
            continue
        # Create d_ns - dictionary of namespace key or abbreviation name to
        # namespace 'long name' values.
        d_namespace = { key:value
          for key,value in dict(node_root_input.nsmap).items()
          if key is not None}

        l = len(node_root)
        out_html += f"<li>Note: mets_filename={mets_filename}, len={l}</li>"
        out_html += '</ol>'


    #end for thesis or bibvid


    out_html += f"</ol><p>Found {n_thesis} bibvids, {n_bad} bad ones.</p>"
    print(out_html)
    return HttpResponse(out_html)

# end def out_mets
