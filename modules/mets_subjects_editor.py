'''
mets_subjects_edit.py
20181105-Robert Phillips -

App to and to add subjects for bibs to their mets.xml file and
possibly sort and retain current subjects of each mets file.

Python 3.6+ code
'''

#import from
import sys, os, os.path, platform
from io import StringIO, BytesIO
import codecs
from copy import deepcopy

from tempfile import NamedTemporaryFile, mkstemp, TemporaryFile
from shutil import move, copy, copy2
from os import remove
import operator

def register_modules():
    platform_name = platform.system().lower()
    if platform_name == 'linux':
        modules_root = '/home/robert/'
        #raise ValueError("MISSING: Enter code here to define modules_root")
    else:
        # assume rvp office pc running windows
        modules_root="C:\\rvp\\"
    sys.path.append('{}'.format(modules_root))
    sys.path.append('{}git/marshal/modules'.format(modules_root))
    return platform_name

platform_name=register_modules()

import etl
from ufdc_item import UFDCItem

from pathlib import Path
from collections import OrderedDict
from lxml import etree

#import regular expressions
import re
import datetime

utc_now = datetime.datetime.utcnow()
utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")

def sequence_paths(log_file=None, input_folders=None, input_path_globs=None,
    verbosity=0):
    '''
    Given input folders and globs, return a sequence of selected filenames
    '''
    # NOTE: I changed arg input_path_glob to input_path_globs
    # apologies to callers that need to adapt
    me = 'sequence_paths'
    if (input_folders is None or input_path_globs is None):
        msg = "Missing param input_folders or input_path_glob"
        raise ValueError(msg)
    if verbosity  > 0:
        msg = ("{}: Using input_folders={}, input_path_globs={}"
          .format(me,input_folders, input_path_globs))
        print(msg, file=log_file)

    # compose input_path_list over multiple input_folders
    n_files = 0
    for input_folder in input_folders:
        for input_path_glob in input_path_globs:

            #paths = list(Path(input_folder).glob(input_path_glob))
            # Use generator rather than create initial list
            for path in Path(input_folder).glob(input_path_glob):
                n_files += 1
                yield path
        #end for input_path_glob
    # end for input folder
    if (verbosity > 0):
        msg = ("{}: Found {} and yielded files in input_folder='{}'"
           " that match glob ={}\n"
          .format(me, len(paths), input_folder, input_path_glob))
        print(msg)
        print(msg,file=log_file)
# end def sequence_paths

def get_root_from_file_bytes(input_file_name=None, log_file=None,
    verbosity=None):
    '''
    todo: move this function move new file for class UtilLxml() maw_utils/lxml.py

    Read the given xml file from the input_file_name, parse it into an
    lxml tree and return the root node.
    '''

    me = 'get_root_from_file_bytes'

    # get_root_element
    with open(input_file_name, mode='rb') as f:
        #input_string = StringIO(bytes.decode('utf-8-sig'))
        input_string = f.read().decode(
           encoding='utf-8-sig', errors='replace')

        if verbosity > 1:
            msg = ("{}: Got input_string='{}'"
              .format(me, input_string))
            print(msg, file=log_file)
            log_file.flush()
    try:
        # { next ignores comments - but I want to keep them
         node_root_input = etree.fromstring(str.encode(input_string))
        # }
        #parser = etree.XMLParser(remove_comments=False)
        #tree = etree.parse

    except Exception as e:
        log_msg = (
            "{}:Skipping exception='{}' input_string='{}'"
            .format(me, repr(e), input_string))
        print(log_msg, file=log_file)
        return None
#end def get_root_from_file_bytes()

def get_tree_and_root_by_file_name(input_file_name=None, log_file=None,
    verbosity=None):
    me = 'get_tree_and_root_by_file_name'
    '''
    Parse given input file as an xml document
    For any exception, write it to give logfile and return None, None

    Parse the document and return tuple of doctree and doctree.get_root()
    '''

    #parser = etree.XMLParser(remove_comments=False, remove_blank_text=True)
    parser = etree.XMLParser(encoding='utf-8',remove_blank_text=True,
      remove_comments=False)
    etree.set_default_parser(parser)

    with open(input_file_name, mode='r', encoding='utf-8-sig') \
        as input_bytes_file:

        try:
            tree = etree.parse(input_bytes_file, parser=parser)
        except Exception as e:

            log_msg = (
                "{}:Skipping exception='{}' in input_file_name='{}'"
                .format(me, repr(e), input_file_name))
            print(log_msg, file=log_file)
            return None, None
    # end with open

    return tree, tree.getroot()
#end def get_root_from_parsed_file_bytes()


#def ai_sorted_subject_nodes_bythesauri_bib_vid(thesauri=None,
def ai_sorted_subject_nodes_by_thesauri_bib_vid(thesauri=None,
    d_namespace=None, item_text=None, bib=None, vid=None, verbosity=1):
    '''
    Given:
      (1) a UF-AI list of agreed theaurus names and
      (2) either
        (A) bib and vid or
        (B) item_text bytes
      for a UFDC item, and
      (3) a d_namespace with key 'mets' that provides the namespace
          value to be expanded

    Return:
      A list of sorted subject nodes, meant to be inserted into the main
      document node of a mets.xml tree representing the item.

      consider: to separate AI object from METS object, do not return subject nodes,
      but rather an AI object that reflects their single terms and thesauri
      or maintain a seprate 'liason or translator' object to convert AI subjec/term
      data to mets?  (but since METS is a standard, ... can keep subject_nodes
      as output here maybe?)

    Details:
      The returned list of sorted subject_nodes is created per requirements:
      - each ai term is a single string representing a topic term to
        be represented as a child xml <mets:topic> node of the subject node
      - the supported parameter list of thesauri names is no
        restricted to hold the single string 'jstor' representing the
        only supported thesaurus name.
        When/if multiple thesauri are required, this code might be revised.
      - each returned subject node will have the attributes:
        <subject authority='jstor' ID='650_#0_N'
        where N is the sequence number within the set of returned nodes
      - the returned nodes will be sorted in order of the lexicographic term
        value
      - The terms are retrieved from database model X2018_Subject

    Notes:
      no checks for (nor omission) of duplicate term strings is done.

    '''
    # Todo - add db query code
    # or api code here
    # Return test results now...
    # later add return list of tuples including thes name, term name, match
    # count
    #
    # return_list = []
    # terms for aa00012984_00001

    #Prepare to process multiple thesauri or categories(xtags) later.
    #
    me = 'ai_sorted_subject_nodes_by_thesauri_bib_vid'


    ''' promote rest of logic up the caller tree
    if ( d_namespace is None or thesauri is None or d_namespace is None):
        msg = f'{me}: Missing argument(s).'
        raise ValueError(msg)

    if item_text is None:
        if bib is None and vid is None:
            msg = f'{me}: Missing item_text or bib and vid.'
            raise ValueError(msg)
    else:
        # item_text only is provided. To be implemented.
        msg = f'{me}: Handling of item_text not yet implemented.'
        raise ValueError(msg)
    '''

    d_thesaurus_xtag = {
      'jstor': 'TOPIC', # might add more one day per new UF-AI mou?
    }
    categories = [ v for v in d_thesaurus_xtag.values()]

    suggested_terms = [
      'matrices',
      'geometric shapes',
      'dynamic modeling',
      'degrees of freedom',
      'datasets',
      'damping',
      'butterflies',
    ]

    # Get all suggested subject terms from the local database.
    # https://stackoverflow.com/questions/26411411
    # /django-orm-values-list-with-in-filter-performance

    #suggested_terms = ( Subject.objects.values_list('term', flat=True).
    #    filter(bibid=bib, vid=vid, xtag__in=categories) )

    # consider:put terms in a list to remove late-comer dups
    # for now, there 'should be' no dups from AI because we are
    # querying only for a single xtag, TOPIC, but we can just
    # discover that during testing and overcome it if it is an
    # issue.
    l = len(suggested_terms)
    msg = f"ORM Got {l} suggested terms"

    print(msg, file=sys.stdout, flush=True)
    sorted_terms = sorted(suggested_terms, key=str.lower)

    l = len(sorted_terms)
    msg = f"Got {l} sorted suggested terms"
    print(msg, file=sys.stdout, flush=True)

    sorted_subject_nodes = []
    term_count = 0
    mods_namespace = d_namespace['mods']

    subject_name = f"{{{mods_namespace}}}subject"
    # subject_tag = "mods:subject"

    topic_name = f"{{{mods_namespace}}}topic"
    topic_tag = "mods:topic"

    # We build 'sorted_subject_terms' by sequencing thru a
    # sorted list of terms
    for term_count, term in enumerate(sorted_terms, start=1):
        # Create a new child node to append for this parent in the METS tree
        # Review of LOC mets mods documentation about subject and topic
        # elements indicates that # one topic per subject is the usual case.
        # However, if one has separate values for a geographic country,
        # region, city, it is normal to put
        # all 3 geographic terms wihtin one subject element.
        # CREATE a ELEMENT NODE LXML NODE with Element() call
        subject = etree.Element(subject_name)
        sa = subject.attrib
        sa['authority'] = 'jstor'
        # To follow a year 12018 perceived SobekCM convention used in mets
        # files, now use marc field followed by subject term count as the ID.
        # Later, might want to include sub-fields for indicators, or for
        # other bits of info we want to pack into the subject attribute
        # ID value.
        sa['ID'] = f'650_#0_{term_count}'

        sorted_subject_nodes.append(subject)

        topic = etree.Element(topic_name)
        topic.text = term
        subject.append(topic)

        if verbosity > 1:
            print(f"Using subject_name='{subject_name}'",file=log_file)
            msg = ("appended to parent {} the child {}"
               .format(parent_nodes[0].tag, subject.tag))

    return sorted_subject_nodes
# end def get_suggested_nodes_by_thesauri_bib_vid


def output_by_node__output_file_name(
    node=None,
    output_file_name=None,
    ):

    with open(output_file_name, mode='wb') as output_file:
        # NOTE: Experiments show that method tostring also
        # honors param 'encoding'. But cannot find ref doc yet.
        output = etree.tostring(node,
            pretty_print=True, xml_declaration=True,
            # XML declaration, not python, so utf-8-sig does not work)
            # is not needed.
            encoding="UTF-8",
            # remove_comments=False, # unexpected
            )
        output_file.write(output)

def delete_nodes(nodes=None, log_file=None, verbosity=1):
    me = 'delete_nodes'
    for obsolete in nodes:
        otag = obsolete.tag
        parent = obsolete.getparent()
        if verbosity > 0:
            msg = f"{me}:From parent='{parent.tag}', removed obsolete='{otag}'"
            print(msg, file=log_file)
        # remove obsolete node from its own parent
        parent.remove(obsolete)
    return
# def delete_nodes()

class MetsSubjectsEditor():
    '''
    '''

    def __init__(self,
        backup_subfolder_name='sobek_files',
        bib=None,
        file_globs=['**/*.mets.xml'],
        input_folder=None,
        item_text=None,
        terms=None,
        log_file_name='mets_subject_edit_log.txt',
        log_file=None,
        output_folder=None,
        verbosity=1,
        vid='00001',

        replace_children=False,
        strftime_format="%Y%m%dT%H%MZ",
        thesauri=None,
        d_namespace=None,
        ):

        '''
        This object is initialized with a bib_vid combination that
        identifies a UFDC item that has exacly one METS file under the
        UFDC resources folder, and the file is METS-standard format.

        The METS xml tree representation of the file has a
        <mods:subject> list of elemens under the parent <mods:mods> node.
        That list is edited by some methods of this object.
        '''

        me='MetsSubjectEditor:__init__()'

        if bib is None or vid is None:
            raise ValueError(f'{me}:Missing bib or vid')
        self.bib = bib
        self.vid = vid

        # Get UFDCItem
        self.item = UFDCItem(bib=bib, vid=vid, log_file_name=log_file_name,)
        item = self.item

        output_folder = item.mets_folder
        self.mets_folder = item.mets_folder
        self.output_folder = self.mets_folder
        self.backup_subfolder_name = backup_subfolder_name

        backup_folder_name = ( f"{item.mets_folder}\\"
          f"{self.backup_subfolder_name}\\")

        if log_file_name is None:
            #datetime_string = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            day_string = datetime.datetime.utcnow().strftime(strftime_format)
            log_file_name = (
              f"{output_folder}/mets_subject_edits_{day_string}.txt")
        else:
            log_file_name = ( f"{output_folder}/{log_file_name}")

        self.log_file_name = log_file_name

        msg = f'{me}: log_file_name={log_file_name}'
        print(msg, sys.stdout, flush=True)

        if verbosity > 0:
            print(msg, flush=True)

        if log_file is None:
            log_file = open(log_file_name, mode="w", encoding='utf-8-sig')
        self.log_file = log_file

        #Todo - work this out, but get the mets tree for the item
        self.mets_tree, self.d_mets_namespace = self.item.get_mets_tree()

        # The
        # self.file_globs=file_globs
        self.mets_glob='**/*.mets.xml'

        # This is always read from an extant METS file to be edited
        self.d_mets_namespace=None,

        # Member item_text has an optional value.
        # It may be used to send to an Access
        # Innovations API  to retrieve subject terms for it.
        self.item_text = item_text

        #some constants
        qtag = 'mods:mods'
        self.parent_qualified_tag = qtag
        self.parent_xpath = f'.//{qtag}'

        qtag = 'mods:subject'
        self.subject_qualified_tag = qtag
        self.subject_xpath = f'.//{qtag}'

        qtag = 'mods:topic'
        self.topic_qualified_tag = qtag
        self.topic_xpath = f'.//{qtag}'

        self.backup_subfolder_name = backup_subfolder_name
        self.strftime_forma = strftime_format

        #Todo - implement function to populate this from the METS file
        # in method mets_tree()
        self.d_mets_namepace = None
        self.thesauri = thesauri

        if item_text is None:
            if bib is None and vid is None:
                msg = f'{me}: Missing item_text or bib and vid.'
                raise ValueError(msg)
        else:
            # item_text only is provided. To be implemented.
            msg = f'{me}: Handling of item_text not yet implemented.'
            raise ValueError(msg)

        # encoding utf-8-sig strips BOM as we desire
        log_file = open(log_file_name, mode="w", encoding='utf-8-sig')
        utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")

        if verbosity > 0:
            ptag = self.parent_qualified_tag
            bsfn = self.backup_subfolder_name
            msg = (
              f"{me}: Start at {utc_secs_z}, backup_folder={bsfn}, "
              f"log_file_name='{log_file_name}',\n\tparent_qualified_tag={ptag}"
            )
            print(msg, file=log_file)
            print(msg)
            sys.stdout.flush()

        print(f"{me}: STARTING: Using verbosity value={verbosity}",
            file=log_file)

        print(f"{me}:Using data input_folder={input_folder}",
            file=log_file)

        input_file_folders = [input_folder]

        n_files = 0

        if verbosity > 0:
            msg = f'{me}: callimg edit()'
        print(msg)
        print(msg, file=log_file)

        #RVP20181117 - change this method to accept a sequence of objects/rows of:
        # bib, vid, eg the 29K bibvids  for the UFDC ETD 2016 items

        #rv = mets_xml_add_or_replace_subjects(
        '''
            log_file=log_file,
            bib=bib, vid=vid, item_text=item_text,
            input_file_name=input_file_name,
        '''
        rv = self.edit(
            replace_subjects=replace_children,
            verbosity=verbosity)

        n_changed = 1
        n_files = 1

        msg = ("{}: ENDING: Processed {} files, and added a child node to {}.\n"
           .format(me, n_files, n_changed))
        print(msg, file=log_file)
        print(msg)
        return

    #end def __init__()

    def sorted_subject_nodes(self, subject_nodes=None, d_namespace=None,
        log_file=None, verbosity=0):
        '''
        Given a list of input 'subject' lxml nodes with data formatted
        for UF Digital Collections mets.xml files,

        Return a sorted list of subject xml nodes ...
        '''
        me = 'sorted_subject_nodes'
        xnodes = subject_nodes
        if verbosity > 0:
            msg = f'{me}: Starting with {len(subject_nodes)} subject nodes'
            print(msg, file=log_file)

        d_heading_subject = {}

        topic_tag = self.topic_qualified_tag
        for node_count, subject_node in enumerate(xnodes, start=1):
            tnodes = subject_node.findall(
                self.topic_xpath, namespaces=self.d_mets_namespace)
            #RESUME todo: find topic_tag that yields the topics
            t_count = 0
            tsep = ''
            key_heading = ''
            for tnode in tnodes:
                t_count += 1
                key_heading += (tsep + tnode.text)
                tsep = ' -- '

            d_heading_subject[key_heading] = subject_node
            if verbosity > 0:
                msg = f'{me}: subject_node {node_count} has key {key_heading}'
                print(msg, file=log_file)
        # end for subject_node in xnodes

        # Now subject nodes are ready to be sorted by key heading into
        # returnable list of subject nodes

        sorted_xnodes = sorted(d_heading_subject.values(), key=lambda kv:kv[0].text)
        return sorted_xnodes
    # end def sorted_subject_nodes(0)
    #def mets_xml_add_or_replace_subjects(self,
    '''
        input_file_name=None,
        bib=None, vid=None, item_text=None,
        log_file=None,
    '''
    def edit(self,
        thesauri=None,
        replace_subjects=False,
        retain_subjects=True,
        verbosity=0,):

        '''
        Given a mets input_file_name formatted like:
          f'{bibid}_{vid}.mets.xml'

        If bib and vid are not given in named arguments, then
        from the input file name, parse the bibid and vid, and use that to
        garner the Access Innovations 'SuggestedTerms'.

        Note: Parameter replace_subjects: True means delete current mets subjects
         and False means to preserve current mets subjects
         We always add subjects for the given list of thesauri for an item.

        For phase 1 - just select the
        'TOPIC' terms for that bibvid from the MAW django model
        named hathitrust_X2018Subject.

        Future: accept an option to indicate to use the
        GetSuggestedTerms API instead of the queries to garner the suggester new
        subject terms for each bib_vid item.
        Then we can also use a new value from a thesauri parameter, which
        holds thesauri names of interest (a simple list
        of strings) Each thesaurus name is a known string shared between UF and AI
        to identify a thesaurus that AI will use to generate suggested terms)
        This parameter is used to formulate requests on the API for suggested
        terms.

        - Find the UFDC resources mets.xml file for the bib_vid and
        - Use lxml to parse/represent the METS file into a local core mets tree,
        - If retain_subjects == True: Put all the current subject elements/nodes
          in a subject_nodes list.
           -- item parsing: each 'item' in a dictionary is defined by a mets xml
              SUBJECT element.
           -- key: the ordered concatentated string of all child 'topic/ text values
              of the subject, probably trimmed of leading and trailing whitespace,
              with multiple occurrences prefixed by a tab.
           -- value: an ordered dictionary of all the attributes of the parent
              subject. (eg authority:'lcsh', others).
              Note that the TOPIC values in a mets should have no attributes to
              be accepted nor preserved.
           -- Sort the 'subject_nodes' list.

        - Remove all current subject elements from the mets tree

        - Arrange a sorted list ai_terms[] of the sorted TOPIC terms from AI.
        - For each SuggestedTerm in ai_terms[], create and append to the mets_tree
          a <subject> element with the child element <topic> with the term name
          value, in lexicographic order of sorted topic/term name.

          NOTE: now AI does provide any multi-part  'path' value for a term as
          does lcsh for some subjects.
          So each AI suggested subject term we receive now is always a single
          topic value.

        - Future: add option to indicate other XTAGs than TOPIC for
          values to use as an sql filter or to set as a request parameter
          to the API
        - If arg retain_subjects is True, append the ordered list
          subject_nodes into the mets tree
          ---- xxx
          -- For each extant subject term,
             -- create a subject element with the attribute ID in the format of
                marc_12_n, and with attribute authority with value jstor
             -- from the term value, split via the tab character into 1 or
                 more subvalues and for each (in order) append to the subject a
                 child element <topic> with the splitted-out subvalue.
          Note: maybe have a method to do this or a stub that later will
          consult a reference resource or parameter to issue values
          for the ID that comply with set MARC number and indicator values for the
          given authority value of the term.
        - Make a backup of the current production METS file under its
          sobek_files directory.
        - Overwrite the production METS file name with the info in
          the mets tree.
        -

        This is heavily based on method file_add_or_replace_xml() of
        mets_batch_edit.py in this github project.

        '''
        me = 'edit'
        log_file = self.log_file

        if thesauri is None:
            # jstor is default thesaurus used by UF and access innovations (AI)
            # future: review -- is this the now-agreed-upon jstor name?
            # will synchronize thesauri names to it/those when extend this
            # to use the API GetSuggestedTerms
            thesauri = ['jstor']

        utc_now = datetime.datetime.utcnow()
        utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")
        utc_yyyy_mm_dd = utc_now.strftime("%Y_%m_%d")

        ptag = self.parent_qualified_tag
        parent_xpath = f".//{ptag}"

        # Get bib and vid from filename
        input_file_name = self.item.mets_file_name
        base_name =  os.path.basename(input_file_name)
        if verbosity > 0:
            msg = (
              f"{me}: input_file_name={input_file_name}, base_name={base_name}"
              )
            print(msg, file=log_file, flush=True)
            print(msg, flush=True)

        log_file= self.log_file

        if verbosity > 0:
            msg = (
              '{}: using input_file={}, parent_xpath={}'
              .format(me, input_file_name, parent_xpath,))
            msg += f'\nbib={self.item.bib}, vid={self.item.vid}'
            print(msg, file=log_file,flush=True)
            print(msg, flush=True)

        # { see https://stackoverflow.com/questions
        # /13590749/reading-unicode-file-data-with-bom-chars-in-python
        # Jonathan Eunice message of 20180429
        # Get list of tuples of suggested terms: (term name, )
        # consider - construct subject nodes

        doctree, node_root_input = get_tree_and_root_by_file_name(
            input_file_name=input_file_name,
            log_file=log_file,
            verbosity=verbosity)

        if node_root_input is None:
            print(f"Got -1 for node_root_input??")
            return -1

        if verbosity > 0:
            msg = f'{me}: mets root node is {node_root_input.tag}'
            print(msg, file=log_file,flush=True)


        # Retrieve the input file's  METS d_namespace
        # dictionary of namespace key or abbreviation
        # name to namespace 'long name' values.

        d_namespace = { key:value
          for key,value in dict(node_root_input.nsmap).items()
          if key is not None}

        self.d_mets_namespace = d_namespace

        # Get list of subject_nodes from the AccessInnovations
        # provided 'suggested terms' for the given bib, vid and thesauri.

        sorted_suggested_subject_nodes = (
          ai_sorted_subject_nodes_by_thesauri_bib_vid(
            d_namespace=d_namespace, thesauri=self.thesauri,
            bib=self.bib, vid=self.vid))

        if verbosity > 0:
            msg=f'--- {me}: NAMESPACE KEY VALUES ARE:'
            print(msg, file=log_file)
            print(msg, flush=True)
            for key,value in d_namespace.items():
                msg = (f"{key} : {value}")
                print(msg, file=log_file)
                print(msg, flush=True)

        # Find the parent node(s) for a mets.xml file, the files are designed
        # for one such parent/root node per input file, so we assume that.
        pxp = self.parent_xpath
        if verbosity > 0:
            msg = (
              f"{me}: finding parent nodes for xpath '{pxp}'")
            print(msg, file=log_file, flush=True)
            print(msg, flush=True)

        parent_nodes = node_root_input.findall(
            pxp, namespaces=self.d_mets_namespace)
        plen = len(parent_nodes)

        if verbosity > 0:
            msg = (
              f'{me}: in {input_file_name}, found {plen} parent nodes')
            print(msg, file=log_file, flush=True)

        if parent_nodes is None or plen != 1:
            # But not a fatal exception if not exactly 1, so catching that
            if verbosity > 0:
                msg = (
                  f'{me}: in {input_file_name}, did not find exactly 1 parent_node'
                  f' occurence. Skipping processing the file.')
                print(msg, file=log_file)
            return -2

        parent_node = parent_nodes[0]

        # Check for extant child - default behavior is to NOT insert child if
        # same type of node already exists
        mods_namespace = d_namespace['mods']

        if verbosity > 0:
            print(f"Using subject_xpath={self.subject_xpath}", file=log_file)

        topic_name = f"{{{mods_namespace}}}topic"
        topic_tag = self.topic_qualified_tag

        # subject_xpath is the xpath to identify and find all child nodes
        # for this bib_vid ufdc item to be edited/replaced

        subject_nodes = parent_node.findall(
            self.subject_xpath, namespaces=d_namespace)

        if subject_nodes is not None and len(subject_nodes) > 0:
            have_child = True
        else:
            have_child = False

        if verbosity > 1:
            msg = (f"{me}: METs has {len(subject_nodes)} current subject nodes")
            print(msg, file=log_file)

        if retain_subjects == True:
            # Here, we want to preserve current subjects (not replace them)
            # Create a sorted list of the subject nodes which
            # we will append alphabetically into the mets document tree.

            # Sort the current nodes to retain a sorted order
            sorted_current_subject_nodes = self.sorted_subject_nodes(
                d_namespace=d_namespace, subject_nodes=subject_nodes,
                log_file=log_file, verbosity=verbosity)

            if verbosity > 1:
                l = len(sorted_current_subject_nodes)
                msg = (f"{me}: Got count={l} current sorted subject nodes.")
                print(msg, file=log_file)
            # If needed, we got the current_subject_nodes to sort and retain

        # Delete the current subject nodes.
        delete_nodes(nodes=subject_nodes, log_file=log_file, verbosity=verbosity)

        # For each found suggested term, UFDC standard citation display UI
        # requirements are implemented by first appending to thd mets.xml file the
        # the suggested subject nodes, and later we will append any retained
        # subjet nods.

        for subject_node in sorted_suggested_subject_nodes:
            if verbosity > 1:
                msg = (f'{me}:Add suggested node {subject_node.tag}')
                print(msg, file=log_file, flush=True)
            parent_nodes[0].append(subject_node)

        if retain_subjects == True:
            # Per UFDC requirments, now restore the sorted current nodes
            for subject_node in sorted_current_subject_nodes:
                if verbosity > 1:
                    msg = (
                      f'{me}:Add retained node {subject_node.tag}')
                    print(msg, file=log_file, flush=True)
                parent_nodes[0].append(subject_node)

        # TEST OUTPUT
        output_file_name = r'C:\rvp\tmp.mets.xml'
        output_by_node__output_file_name(node=node_root_input,
            output_file_name=output_file_name)
        msg = (f'{me}: outputting new mets file to {output_file_name}\n'
            f'Done!')
        print(msg, file=log_file)
        print(msg)

        return 1

        # Done modifying the in-memory document tree
        # Now output it in its file.
        # TODO: CHANGE AFTER TESTING
        # output_file_name = "{}.txt".format(input_file_name)
        # Production

        # Backup original mets file to a backup file under subfolder sobek_files
        #
        # First, construct the backup file name
        vid_folder, relative_mets_file_name = os.path.split(input_file_name)
        fparts = relative_mets_file_name.split('.')
        # This extracts the bib_vid part of the mets.xml file name, assumed
        # to comply with the ufdc *.mets.xml file naming convention
        bib_vid = fparts[0]
        backup_folder_name = f"{vid_folder}\\{self.backup_subfolder_name}\\"

        # Just in case absent, make sure the backup dir is made
        os.makedirs(backup_folder_name, exist_ok=True)

        # Save the input file per UFDC conventions, in subfolder sobek_files
        backup_file_basename = "{}_{}.mets.bak".format(bib_vid,utc_yyyy_mm_dd)
        backup_file_name = ("{}{}"
          .format(backup_folder_name, backup_file_basename))

        # Make the file backup copy
        if verbosity > 0:
            msg="{} creating backup copy file='{}'".format(me,backup_file_name)
            print(msg)
            print(msg, file=log_file)
            sys.stdout.flush()

        # Use copy2 to preserve original creation date
        # So the historical span of relevance for this record goes from
        # the file metadata creation date to the file name's encoded
        # archiving date
        copy2(input_file_name, backup_file_name)

        #Now overwrite the original input file

        output_file_name = input_file_name

        if verbosity > 0:
            msg="Writing to output file={}".format(output_file_name)
            print(msg, file=log_file)

        # Note: must open with mode='wb' to use doctree.write(...), eg:
        # with open(output_file_name, 'wb') as output_file:

        with open(output_file_name, mode='wb') as output_file:
            # NOTE: Experiments show that method tostring also
            # honors param 'encoding'. But cannot find ref doc yet.
            output = etree.tostring(node_root_input,
                pretty_print=True, xml_declaration=True,
                # XML declaration, not python, so utf-8-sig does not work)
                # is not needed.
                encoding="UTF-8",
                # remove_comments=False, # unexpected
                )
            output_file.write(output)

        msg = f"{me}: pretty={pretty},binary={binary},output_file={output_file}"

        if verbosity > 0:
            print(msg,file=log_file)
            print(msg)

        return 1
    # end def edit()

    def mets_paths_backup_optional(backup_folder=None, input_folders=None,
        file_globs=None, log_file=None, verbosity=None):

        '''
        mets_paths_backup_optional()

        Given input_folders and file_globs:

        (1) visit a sequence of contained files,
        (2) save only unique paths in paths[]
        (3) and return the paths[] of the selected files.

        Optionally, if backup_folder is not None,
        back up each mets file in the backup folder too

        ASSUMPTION - these are mets files couched in UFDC resources key-pair
        directory hierarchy, and each mets.xml file is supposed to be unique.
        So, destinations filenames are copied directly into one flat backup folder.

        Consider an option later to 'flatten' the parent directory name into a
        backup folder subdirectory, eg "AA12345678_12345", to ensure that no
        duplicate mets file names will be 'lost' due to overwriting in this routine.
        '''

        me = 'mets_paths_backup_optional'

        if verbosity > 0:
            utc_now = datetime.datetime.utcnow()
            utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")
            msg = ("{}:for input_folders={},\n"
              " globs={},\nlog='{}', getting sequence paths at {}..."
              .format(me,input_folders,self.mets_glob,log_file.name, utc_secs_z))
            print(msg)
            print(msg,file=log_file)
            sys.stdout.flush()
            log_file.flush()

        gpaths = sequence_paths(log_file=log_file, input_folders=input_folders,
                input_path_globs=[self.mets_glob], verbosity=verbosity)

        if verbosity > 0:
            utc_now = datetime.datetime.utcnow()
            utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")
            msg = ("{}:Checking the input paths sequence for dups at utc time = {}"
              .format(me, utc_secs_z))
            print(msg)
            print(msg,file=log_file)
            sys.stdout.flush()
            log_file.flush()

        paths = []
        n_path = 0

        for path in gpaths:
            if path in paths:
                # gpaths could have duplicates when mulitple globs
                # were used to generate the gpaths, so skip dups
                # If carefully chosen to guarantee the globs have no dups,
                # one can bypass this checking
                continue
            # Store this path to return and will also use it to check for future
            # duplicates in the sequence
            n_path += 1
            paths.append(path)

            #Copy the file to backup location
            if backup_folder is not None:
                copy(path.resolve(), backup_folder)

        if verbosity > 0:
            utc_now = datetime.datetime.utcnow()
            utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")
            msg = ("{}: Found paths for {} mets files at utc time = {}"
              .format(me, n_path, utc_secs_z))
            if backup_folder is not None:
                msg += ', and backed them up under {}'.format(backup_folder)
            print(msg)
            print(msg,file=log_file)
            sys.stdout.flush()
            log_file.flush()

        return paths

    #end def mets_paths_backup_optional

    def xxprocess_files(
        backup_folder=None,
        input_folders=None,
        file_globs=None,
        log_file=None,
        parent_tag_name=None,
        replace_children=False,
        progress_count=100,
        verbosity=1,
        ):

        me = 'process_files'
        n_files = 0
        test_one = 0

        total_file_lines = 0
        log_file = log_file

        # First call mets_paths_backup_optional() to
        # collect the mets file paths and copy the mets files to backup
        # location.

        paths =  mets_paths_backup_optional(backup_folder=backup_folder,
            input_folders=input_folders, file_globs=[self.mets_glob],
            log_file=log_file, verbosity=verbosity
            )

        # We now loop through the paths[] and apply the edits.
        n_files = 0
        n_unchanged = 0
        n_changed = 0

        for path in paths:
            input_file_name = path.resolve()
            if verbosity > 0:
                msg=("{}:Got path.resolve()='{}'".format(me, input_file_name))
                print(msg, file=log_file)
            n_files += 1

            #Test limits
            min_file_index = 0
            # NOTE: set max_file_index 0 to mean unlimited
            max_file_index = 0
            if n_files < min_file_index:
                continue
            if max_file_index > 0 and n_files > max_file_index:
                return n_files, n_changed, n_unchanged

            # Start processing a file
            if verbosity > 0:
                msg=("{}:Processing input_file_name='{}'"
                  .format(me, input_file_name))
                print(msg, file=log_file)
                print(msg)
                log_file.flush()
                sys.stdout.flush()

            rv = mets_xml_add_or_replace_subjects(
                log_file=log_file,
                bib=bib, vid=vid, item_text=item_text,
                input_file_name=input_file_name,
                replace_subjects=replace_children,
                verbosity=verbosity)

            period = progress_count
            if n_files % period == 0:
                utc_now = datetime.datetime.utcnow()
                utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")
                msg = ("{}: Processed thru file index {}, name {} as of {}"
                    .format(me, n_files, input_file_name, utc_secs_z))
                print(msg)
                print(msg, file=log_file)
                sys.stdout.flush()
                log_file.flush()

            if rv is None or rv <= 0:
                n_unchanged += 1
            else:
                n_changed +=1

            if verbosity > 0:
                print(
                   "{}: Processed file {}={} with rv={}."
                  .format(me, n_files, input_file_name, rv)
                  ,file=log_file)
            if test_one == 1:
                print("Test_one - test break")
                break

        # end for path in paths

        if verbosity > 0:
            utc_now = datetime.datetime.utcnow()
            utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")
            msg = ("{}: Processed thru file index {}, name {} as of {}"
                .format(me, n_files, input_file_name, utc_secs_z))
            print(msg)
            print(msg, file=log_file)
            sys.stdout.flush()
            log_file.flush()
            print("{}: Ending with {} files processed."
                .format(me,n_files,), file=log_file)

        return n_files, n_changed, n_unchanged
    # end def process_files

import datetime

# end class UFDCMetsEditor

if __name__ == "__main__":


    item = bib='aa00012984'
    #item = UFDCItem(bib=bib, log_file_name='log_mets_subject_edit.txt', )
    subject_editor = MetsSubjectsEditor(bib=bib)

    '''
    run(backup_folder=backup_folder,
        input_folder=input_folder,
        log_file_name='mets_subject_edit_log.txt',
        file_globs = ['**/*.mets.xml'],
        parent_qualified_tag=None,
        replace_children=False,
        verbosity=2)
    '''

#end if __name__ == "__main__"
#END FILE
