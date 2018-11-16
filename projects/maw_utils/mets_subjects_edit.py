'''
mets_subjects_edit.py
20181105-Robert Phillips -

App to optionally delete and to add subjects for bibs
given input file.

Python 3.6+ code
'''

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

def sequence_paths(log_file=None, input_folders=None, input_path_globs=None,
    verbosity=0):
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

            #input_path_list.extend(list(Path(input_folder).glob(input_path_glob)))
            #for path in paths:
            #    yield path
            # end for path
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

    return node_root_input
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

def get_sorted_subjects_by_thesauri_bib_vid(thesauri=None,
    d_namespace=None, bib=None, vid=None, verbosity=1):
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
    d_thesaurus_xtag = { 'jstor': 'TOPIC',}
    category = d_thesaurus_xtag[thesauri[0]]

    suggested_terms = [
      'matrices',
      'geometric shapes',
      'dynamic modeling',
      'degrees of freedom',
      'datasets',
      'damping',
      'butterflies',
    ]

    suggested_terms0 = ['suggested_term1','suggested_term2','suggested_term3']

    # consider:put terms in a list to remove late-comer dups
    # for now, there 'should be' no dups from AI because we are
    # querying only for a single xtag, TOPIC, but we can just
    # discover that during testing and overcome it if it is an
    # issue.
    l = len(suggested_terms)
    msg = f"Got {l} suggested terms"

    print(msg, file=sys.stdout, flush=True)
    sorted_terms = sorted(suggested_terms, key=str.lower)

    l = len(sorted_terms)
    msg = f"Got {l} sorted suggested terms"
    print(msg, file=sys.stdout, flush=True)

    sorted_subject_nodes = []
    term_count = 0
    mods_namespace = d_namespace['mods']

    subject_name = f"{{{mods_namespace}}}subject"
    subject_tag = "mods:subject"

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

def get_sorted_subject_nodes(subject_nodes=None, d_namespace=None,
    log_file=None, verbosity=0):
    '''
    Given a list of input 'subject' lxml nodes with data formatted for UF Digital
    Collections mets.xml files,

    Return a sorted list of subject xml nodes ...
    '''
    me = 'get_sorted_subject_nodes'
    xnodes = subject_nodes

    d_heading_subject = {}

    for subject_node in xnodes:
        tnodes= subject_node.findall(
            "./TOPIC", namespaces=d_namespace)
        t_count = 0
        tsep = ''
        key_heading = ''
        for tnode in tnodes:
            t_count += 1
            key_heading += tnode.text
            tsep = ' -- '

        d_heading_subject[key_heading] = subject_node
    # end for subject_node in xnodes

    # Now subject nodes are ready to be sorted by key heading into
    # returnable list of subject nodes

    sorted_xnodes = sorted(d_heading_subject.values(), key=lambda kv:kv[0])
    return sorted_xnodes
# end def get_sorted_subject_nodes(0)

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

def mets_xml_add_or_replace_subjects(
    input_file_name=None,
    input_encoding='latin-1', errors='ignore',
    bib=None,
    vid=None,
    thesauri=None,
    log_file=None,
    # Replace_subjects: True means delete current mets subjects
    # and False means to preserve current mets subjects
    # We always add subjects for the given list of thesauri for an item.
    replace_subjects=False,
    verbosity=0,):

    '''
    Given a mets input_file_name formatted like:
      f'{bibid}_{vid}.mets.xml'

    If bib and vid are not given in named arguments, then
    from the input file name, parse the bibid and vid, and use that to
    garner the Access Innovations 'SuggestedTerms'.

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
    - If arg replace_subjects is True, go directly a few steps below to
      remove all current subject elments from the mets tree.
    - Read all the current subject elements into an ordered dictionary 'd_current_term'
      (or maybe unordered dict at this stage): using
       -- item parsing: each 'item' in a dictionary is defined by a mets xml
          SUBJECT element.
       -- key: the ordered concatentated string of all child 'topic/ text values
          of the subject, probably trimmed of leading and trailing whitespace,
          with multiple occurrences prefixed by a tab.
       -- value: an ordered dictionary of all the attributes of the parent
          subject. (eg authority:'lcsh', others).
          Note that the TOPIC values in a mets should have no attributes to
          be accepted nor preserved.
    - Sort the 'd_current' dictionary by key.

    - Remove all current subject elements from the mets tree

    - Arrange a sorted list ai_terms[] of the sorted TOPIC terms from AI.
    - For each ai_terms[] item, create and append to the mets_tree a <subject>
      element with the child element <topic> with the term name value.
      NOTE: now AI does not give a 'path' value for a term as does lcsh,
      so each AI term we receive now is always a single topic term name/string.

    - Future: add option to indicate other XTAGs than TOPIC for
      values to use as an sql filter or to set as a request parameter
      to the API
    - If arg replace_subjects is False, output the ordered list of terms
      in d_current
      -- For each d_current key/term,
         -- create a subject element with the attribute ID in the format of
            marc_12_n, and with attribute authority with value jstor
         -- from the d_current value, split via the tab character into 1 or
             more subvalues and for each (in order) append to the subject a child
             element <topic> with the splitted-out subvalue.
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
    if thesauri is None:
        # jstor is default thesaurus used by UF and access innovations (AI)
        # future: review -- is this the now-agreed-upon jstor name?
        # will synchronize thesauri names to it/those when extend this to use the
        # API GetSuggestedTerms
        thesauri = ['jstor']

    me = 'mets_xml_add_or_replace_subjects'

    utc_now = datetime.datetime.utcnow()
    utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")
    utc_yyyy_mm_dd = utc_now.strftime("%Y_%m_%d")

    parent_xpath = f".//mods:mods"

    child_tag_namespace = 'mods'
    child_tag_localname = 'subject'
    child_tag_name = f'{child_tag_namespace}:{child_tag_localname}'

    # Get bib and vid from filename
    print(f"{me}:Starting with input_file_name={input_file_name}")
    base_name =  os.path.basename(input_file_name)
    print(f"{me}:Got base_name={base_name}")
    if bib is None:
        # Get both the bib and vid from the filename, regardless of presence
        # of a vid argument value
        dot_parts = base_name.split('.')
        print(f"Got dot_parts={dot_parts}")

        # Assume the first dot_parts[0] is formatted like bib_vid
        bparts = dot_parts[0].split('_')
        print(f"Got bparts={bparts}")

        bib = bparts[0]
        vid = bparts[1]

    if verbosity > 0:
        msg = ('{}: using input_file={}, parent_xpath={},child_tag_namespace={}'
          .format(me, input_file_name, parent_xpath,child_tag_namespace))
        msg += f'\nbib={bib}, vid={vid}'
        print(msg, file=log_file)

    # { see https://stackoverflow.com/questions/13590749/reading-unicode-file-data-with-bom-chars-in-python
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

    # Create d_namespace - dictionary of namespace key or abbreviation
    # name to namespace 'long name' values.
    d_namespace = { key:value
      for key,value in dict(node_root_input.nsmap).items()
      if key is not None}

    # New function to replace get_suggested_terms_by_thesauri_bib_vid
    sorted_suggested_subject_nodes = get_sorted_subjects_by_thesauri_bib_vid(
        d_namespace=d_namespace,
        thesauri=thesauri, bib=bib, vid=vid)

    if verbosity > 1:
        msg=f'--- {me}: NAMESPACE KEY VALUES ARE:'
        print(msg, file=log_file)
        for key,value in d_namespace.items():
            msg = (f"{key} : {value}")
            print(msg, file=log_file)

    # Find the parent node(s) if any - for a mets.xml file, they are designed
    # for one parent/root node
    parent_nodes = node_root_input.findall(
        parent_xpath, namespaces=d_namespace)

    if parent_nodes is None:
        if verbosity > 0:
            msg = ('{}: in {}, found NO parent node occurences. Skipping file.'
              .format(me, input_file_name))
            print(msg, file=log_file)
        return -2

    plen = len(parent_nodes)
    if verbosity > 0:
        msg = ('{}: in {}, found {} parent nodes'
          .format(me, input_file_name, plen))
        print(msg, file=log_file)

    # Check for extant child - default behavior is to NOT insert child if
    # same type of node already exists

    mods_namespace = d_namespace['mods']

    subject_name = f"{{{mods_namespace}}}subject"
    subject_tag = "mods:subject"

    topic_name = f"{{{mods_namespace}}}topic"
    topic_tag = "mods:topic"

    # subject_xpath is the xpath to find all child nodes
    # to be edited/replaced

    subject_xpath = subject_tag

    if verbosity > 0:
        print(f"Using subject_xpath={subject_xpath}", file=log_file)

    child_nodes = parent_nodes[0].findall(
        subject_xpath, namespaces=d_namespace)

    if child_nodes is not None and len(child_nodes) > 0:
        have_child = True
    else:
        have_child = False

    if verbosity > 1:
        print(f"{me}: Current mets has/had {len(child_nodes)} subject elts")

    if replace_subjects == False:
        # Here, we want to preserve current subjects (not replace them)
        # Create a dictionary that allows for sorting by topic name
        # so we can issue them alphabetically in document tree order.
        #

        sorted_current_subject_nodes = get_sorted_subject_nodes(
            d_namespace=d_namespace,
            subject_nodes = child_nodes,
            log_file=log_file, verbosity=verbosity)


        if verbosity > 1:
            l = len(sorted_current_subject_nodes)
            print(f"{me}: Got count={l} current sorted subject elts.")

    # If needed, we got the current_subjects, so now we can remove those
    # obsolete subject element nodes.
    if replace_subjects == True:
        # Delete the current but to-be removed obsolete child nodes
        for obsolete in child_nodes:
            otag = obsolete.tag

            parent = obsolete.getparent()
            parent.remove(obsolete)

            msg= f"From parent='{parent}'',removed obsolete='{otag}'"
            print(msg, file=log_file)

    if verbosity > 1:
        msg = ('{}: in {}, found PARENT to receive a new  node'
          .format(me, input_file_name))
        print(msg, file=log_file)

    # For each found suggested term, append a new mets 'subject' child node
    # stanza

    for subject_node in sorted_current_subject_nodes:
        parent_nodes[0].append(subject_node)

    for subject_node in sorted_suggested_subject_nodes:
        parent_nodes[0].append(subject_node)

    # TEST OUTPUT
    output_file_name = r'C:\rvp\tmp.mets.xml'
    output_by_node__output_file_name(node=node_root_input,
        output_file_name=output_file_name)

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
    backup_folder_name = f"{vid_folder}\\sobek_files\\"

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
# end def mets_xml_add_or_replace_subjects

'''
mets_paths_backup_optional()

visit a sequence of files, save only unique paths in paths[] and return it.
Optionally, if backup_folder is not None,

Back up each mets file in the backup folder too
ASSUMPTION - these are mets files couched in UFDC resources key-pair
directory hierarchy, and each mets.xml file is supposed to be unique.
So destinations filenames are copied directly into one flat backup folder.

Consider to an option later to 'flatten' the parent directory name into a
backup folder subdirectory, eg "AA12345678_12345", to ensure that no
duplicate mets file names will be 'lost' due to overwriting in this routine.
'''

def mets_paths_backup_optional(backup_folder=None, input_folders=None,
    file_globs=None, log_file=None, verbosity=None):

    me = 'mets_paths_backup_optional'

    if verbosity > 0:
        utc_now = datetime.datetime.utcnow()
        utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")
        msg = ("{}:for input_folders={},\n"
          " globs={},\nlog='{}', getting sequence paths at {}..."
          .format(me,input_folders,file_globs,log_file.name, utc_secs_z))
        print(msg)
        print(msg,file=log_file)
        sys.stdout.flush()
        log_file.flush()

    gpaths = sequence_paths(log_file=log_file, input_folders=input_folders,
            input_path_globs=file_globs, verbosity=verbosity)

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

def process_files(
    backup_folder=None,
    input_folders=None, file_globs=None,
    log_file=None,
    parent_tag_name=None,
    # child_tag_namespace allows for use of file-extant namespace prefixes
    child_tag_namespace=None,
    child_model_element=None,
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
            input_folders=input_folders, file_globs=file_globs,
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
def run(backup_folder=None,
    input_folder=None, file_globs=None,
    output_folder = None,
    log_file_name=None,
    parent_tag_name=None,
    child_tag_namespace=None,
    child_model_element=None,
    replace_children=False,
    strftime_format="%Y%m%dT%H%MZ",
    verbosity=1,):

    '''
    '''
    me='run'
    n_files = 0

    if output_folder is None:
        output_folder = input_folder

    if log_file_name is None:
        #datetime_string = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        day_string = datetime.datetime.utcnow().strftime(strftime_format)
        log_file_name = (
          f"{output_folder}/mets_subject_edits_{day_string}.txt")
    else:
        log_file_name = ( f"{output_folder}/{log_file_name}")

    # encoding utf-8-sig strips BOM as we desire
    log_file = open(log_file_name, mode="w", encoding='utf-8-sig')
    utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")

    if verbosity > 0:
        msg = ("{}: Start at {}, backup_folder={}, log_file_name='{}',\n\t"
            "parent_tag_name={}"
            .format(me,utc_secs_z,backup_folder,log_file_name,parent_tag_name))
        print(msg, file=log_file)
        print(msg)
        sys.stdout.flush()

    print("{}: STARTING: Using verbosity value={}".format(me, verbosity)
        ,file=log_file)

    print("{}:Using data input_folder={}".format(me, input_folder)
        ,file=log_file)

    print("{}:Using parent tag ='{}'".format(me, parent_tag_name)
        ,file=log_file)

    print("{}:Using child namespace='{}'".format(me, child_tag_namespace)
        ,file=log_file)

    input_file_folders = [input_folder]

    input_file_name = (
      'F:\\ufdc\\resources\\LS\\00\\00\\00\\01\\test\\'
      'LS00000001_test.mets.xml'
      )
    msg = f'{me}: using {input_file_name}'
    print(msg)
    print(msg, file=log_file)

    rv = mets_xml_add_or_replace_subjects(
                log_file=log_file,
                input_file_name=input_file_name,
                replace_subjects=replace_children,
                verbosity=verbosity)

    n_changed = 1
    n_files = 1

    msg = ("{}: ENDING: Processed {} files, and added a child node to {}.\n"
       .format(me, n_files, n_changed))
    print(msg, file=log_file)
    print(msg)
    return
#end def run()

# end main code

if __name__ == "__main__":

    backup_folder = None
    input_folder = (
      'F:\\ufdc\\resources\\LS\\00\\00\\00\\01\\test\\'
      )


    run(backup_folder=backup_folder,
        input_folder=input_folder,
        log_file_name='mets_subject_edit_log.txt',
        file_globs = ['**/*.mets.xml'],
        parent_tag_name=None,
        child_tag_namespace=None,
        child_model_element=None,
        replace_children=False,
        verbosity=2)

#end if __name__ == "__main__"
#END FILE
