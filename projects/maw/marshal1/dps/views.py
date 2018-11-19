# Create your views here.
from django.conf import settings
import maw_settings
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required

from .models import Bibvid, X2018Thesis, X2018Subject
from lxml import etree
import etl
from mets_subjects_editor import MetsSubjectsEditor
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

(1) Read the contents of X2018Thesis and input the rows,
(2) each representing a uf bibvid item, with some basic uf_bibivid info
and AI-supplied info exported from a XIS export of UF Electronic Theses and
Dissertation (ETD) items that were exported by Xiaoli Ma circa August 2018).

For each row, which represents and item (a UF bibvid identifies each item),

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
    '''
    Initial version creatd in year 2018.

    Given a bibvid (bib_vid) that identifies a UFDC item,
    Derive the *.mets.xml production filename under the UFDC 'resources'
    directory for the UFDC item.
    '''

    me = 'mets_filename_by_bibvid'
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
#end def mets_filename_by_bibvid

'''
Method mets_root_by_bibvid(bibvid=None, verbosity=0)

For given bibvid, use DPS_UFDC_FOLDER as a base and construct the
keypair subfolder path for a bibvid, and read and parse the mets.xml file into
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

def remove_subject_nodes_by_node_root(node_root=None):
    pass

def new_node_by_subject(subject=None):
    # Create child node to append for this parent
    node_subject = etree.Element('subject')
    # Source authority for this row's term
    source = subject.source
    if len(source) > 0:
        node_subject.attrib['authority'] = source
    node_topic = etree.Element('topic')
    node_topic.text = subject.term
    node_subject.append(node_topic)
    return node_subject

def topic_terms(request):
    '''
    This is initially designed to be triggered by visitation to a particular url.

    This code selects all the X2018_Thesis items.
    For each item, it
    (1) parses the uf bib and vid.
    (2) Then it creates a MetsSubjectEditor for the bibvid.
    (3) Then it selects all the X2018_Subject rows for this bib and vid where XTAG
        is 'TOPIC'. For each topic it:
        (a) appends the string name to a list, topic_terms,  of topic terms
    (4) It calls the MetsSubjectEditor(retain_subjects=True,
        topic_terms=topic_terms), where

        This causes the mets.xml file for the bib vid to be edited by
        (a) copying its current subject xml nodes to a list sorted by
            topic/heading name
        (b) added a subject-topic node stanza for each topic term
    '''
    me = 'topic_terms'

    #uf_bibvid='AA00012984_00001'
    #uf_bibvid='AA00020479_00001'

    out_html = '<html><body><ol>'
    verbosity = 0

    nl = '\n' #work around f expresion constraint
    #theses = X2018Thesis.objects.all()[0:5]
    #theses = X2018Thesis.objects.all()[5:6]
    #theses = X2018Thesis.objects.all()[10:12]
    #theses = X2018Thesis.objects.all()[12:100]
    #theses = X2018Thesis.objects.all()[100:110]
    #theses = X2018Thesis.objects.all()[110:200]
    #theses = X2018Thesis.objects.all()[200:1000]
    # theses = X2018Thesis.objects.all()[1000:11520]
    #theses = X2018Thesis.objects.all()[11520:11530]
    #theses = X2018Thesis.objects.all()[11530:]
    #theses = X2018Thesis.objects.all()[20008:]
    theses = X2018Thesis.objects.all()[20070:]

    #testing
    #theses = X2018Thesis.objects.filter(uf_bibvid=uf_bibvid)

    if verbosity >= 0:
       msg = f"{nl}{me}: found {len(theses)} thesis objects.{nl}"
       print(msg, file=sys.stdout,flush=True)
       out_html += f'<li>{msg}</li>'

    for thesis in theses:
        #Parse the uf bib and vid
        uf_bibvid=thesis.uf_bibvid

        bparts = uf_bibvid.split('_')

        bib = bparts[0].upper()
        vid = bparts[1]
        mets_subjects_editor = MetsSubjectsEditor(bib=bib, vid=vid,
            verbosity=verbosity)

        # now find the topic terms to add
        subjects = (X2018Subject.objects.filter(thesis=thesis)
            .filter(xtag='TOPIC'))
        if verbosity >= 0:
          msg = f'\n{me}: thesis={uf_bibvid} has {len(subjects)} subjects'
          print(msg, file=sys.stdout,flush=True)
          out_html += f'<li>{msg}</li>'
        topic_terms = []
        for subject in subjects:
            topic_terms.append(subject.term)

        # We do not keep older mets subject nodes with jstor authority,
        # but we retain other older subject nodes
        mets_subjects_editor.add_topic_terms(discount_authority='jstor',
            retain_subjects=True,
            topic_terms=topic_terms, verbosity=verbosity)

        if verbosity > 0:
          msg = f'{me}: {uf_bibvid} has suggested topic_terms={topic_terms}'
          out_html += f'<li>{msg}</li><ol>'
          for term in topic_terms:
              out_html += f'<li>{term}</li>'
          out_html += f'</ol>'

    out_html += '</ol></html></body>'
    return HttpResponse(out_html)

def out_mets(request):
    '''
    This is designed initially to be called by a user browsing to a
    certain url see urls.py.

    Given a django request object this method does:
    (1) Loop through each row in model X2018_Thesis, and for each row:
    (2) retrieve the uf_bibvid
    '''

    out_html = '<ol>'
    out_file = 'c:\\rvp\\outmets.xml'
    out_xml = ''
    max_bibvids = 5
    od_bibvid = OrderedDict()
    # Retrieve the bibvid items from table Thesis.
    # Report and Skip any duplicate items.
    n_thesis = 0
    n_bad = 0

    with open(out_file,'w') as ofile:
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
              for key,value in dict(node_root.nsmap).items()
              if key is not None}

            # From core doctree, remove all subject nodes
            find_xpath = './/{*}subject'
            found_nodes = node_root.findall(find_xpath, namespaces=d_namespace)
            par=None
            for node in found_nodes:
               par = node.getparent()
               par.remove(node)
                # could add check here for same parent, but sample data looks good
                #
            # Removed subject nodes

            ptag = 'None' if par is None else par.tag
            l = len(found_nodes)
            out_html += (
              f"<li>Note: mets_filename={mets_filename}, partag={par.tag} "
              f"subjects count={l}</li>")
            out_html += '</ol>'

            # Find and insert new subject nodes X2018_Subject
            n_subject = 0
            subjects = ''
            for subject in X2018Subject.objects.filter(thesis=thesis, keep='y'):
                # create a new lxml sub-tree for this subject
                subject_node = new_node_by_subject(subject=subject)

                subject_str = etree.tostring(subject_node,encoding='unicode')
                #subjects += '\n' + etl.escape_xml_text(subject_str)
                subjects += '\n' + subject_str
                par.append(subject_node)
                #
            out_html += f"<pre><code>{subjects}</code></pre>"
        #end for thesis or bibvid
        out_html += f"</ol><p>Found {n_thesis} bibvids, {n_bad} bad ones.</p>"
        out_xml = etree.tostring(par, encoding='unicode');
        print(out_xml,file=ofile)
    # with open ... ofile
    return HttpResponse(out_html)
# end def out_mets
