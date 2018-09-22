'''
mets_batch_edit.py
20180827-Robert Phillips - bib_type 3 added for Melissa Jerome request
20180620-Robert Phillips

Python 3.6+ code
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
    for input_folder in input_folders:
        for input_path_glob in input_path_globs:

            paths = list(Path(input_folder).glob(input_path_glob))

            if (verbosity > 0):
                msg = ("{}: Found {} files in input_folder='{}'"
                   " that match glob ={}\n"
                  .format(me, len(paths), input_folder, input_path_glob))
                print(msg)
                print(msg,file=log_file)

            #input_path_list.extend(list(Path(input_folder).glob(input_path_glob)))
            for path in paths:
                yield path
            # end for path
        #end for input_path_glob
    # end for input folder
# end def sequence_paths

def get_root_from_file_bytes(input_file_name=None, log_file=None,
    verbosity=None):
    me = 'get_xml_file_root'

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

def get_tree_and_root_from_file(input_file_name=None, log_file=None,
    verbosity=None):
    me = 'get_root_from_parsed_file_bytes'

    parser = etree.XMLParser(remove_comments=False)

    with open(input_file_name, mode='rb') as input_bytes_file:

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


def file_add_or_replace_xml(input_file_name=None,
    parent_tag_name=None,
    child_tag_namespace=None,
    child_model_element=None,
    log_file=None,
    replace_children=False,
    input_encoding='latin-1', errors='ignore',
    verbosity=0,):

    me = 'file_add_or_replace_xml'

    utc_now = datetime.datetime.utcnow()
    utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")
    utc_yyyy_mm_dd = utc_now.strftime("%Y_%m_%d")

    parent_xpath = ".//{}".format(parent_tag_name)

    if verbosity > 0:
        msg = ('{}: using input_file={}, parent_xpath={},child_tag_namespace={}'
          .format(me, input_file_name, parent_xpath,child_tag_namespace))
        print(msg, file=log_file)
    # { see https://stackoverflow.com/questions/13590749/reading-unicode-file-data-with-bom-chars-in-python
    # Jonathan Eunice message of 20180429
    #
    doctree, node_root_input = get_tree_and_root_from_file(
        input_file_name=input_file_name,
        log_file=log_file,
        verbosity=verbosity)

    if node_root_input is None:
        return -1

    # Create d_ns - dictionary of namespace key or abbreviation name to
    # namespace 'long name' values.
    d_namespace = { key:value
      for key,value in dict(node_root_input.nsmap).items()
      if key is not None}

    if verbosity > 1:
        msg='--- {} NAMESPACE KEY VALUES ARE:'.format(me)
        print(msg, file=log_file)
        for key,value in d_namespace.items():
            msg = ("{} : {}".format(key,value))
            print(msg, file=log_file)

    # Find the parent node(s) if any
    parent_nodes = node_root_input.findall(
        parent_xpath, namespaces=d_namespace)

    if parent_nodes is None:
        if verbosity > 0:
            msg = ('{}: in {}, found NO parent node occurences. Skipping file.'
              .format(me, input_file_name))
            print(msg, file=log_file)
        return -2

    plen =len(parent_nodes)
    if verbosity > 0:
        msg = ('{}: in {}, found {} parent nodes'
          .format(me, input_file_name,plen))
        print(msg, file=log_file)

    # Check for extant child - default behavior is to NOT insert child if
    # same type of node already exists

    # if element tag name has a :, th namespace must exist in original xml
    # todo: provide parameter to specify new namespace(s) too.
    if child_tag_namespace is not None:
        # put tag name in lxml-prescribed format.
        # see: http://lxml.de/tutorial.html#namespaces
        try:
            namespace_ref = d_namespace[child_tag_namespace]
        except Exception as e:
            msg = ("Child namespace '{}' not allowed in this file. Skipping"
                .format(child_tag_namespace))
            print(msg, file=log_file)
            return -2

        cet_name = "{{{}}}{}".format(namespace_ref, child_model_element.tag)
        child_tag = '{}:{}'.format(
          child_tag_namespace, child_model_element.tag)
    else:
        cet_name = child_model_element.tag
        child_tag = cet_name

    child_check_path = './/{}'.format(child_tag)
    child_check_path = '{}'.format(child_tag)

    if verbosity > 0:
        print("Using child_check_path={}"
          .format(child_check_path),file=log_file)

    child_nodes = parent_nodes[0].findall(
        child_check_path, namespaces=d_namespace)

    if child_nodes is not None and len(child_nodes) > 0:
        have_child = True
    else:
        have_child = False

    if replace_children == False and have_child:
        # Do not replace any target child elements found.
        # Leave old children in place and skip this file
        clen = len(child_nodes)
        if verbosity > 0:
            msg = ("{}: in {}, found {} extant '{}' child node occurences. "
              "NOT adding . Skipping file."
              .format(me, input_file_name,clen,child_check_path))
            print(msg, file=log_file)
        return -2

    if replace_children == True and have_child:
        if replace_children == True:
            # Delete these obsolete child nodes
            for obsolete in child_nodes:
                parent = obsolete.getparent()
                par0 = parent_nodes[0]
                otag = obsolete.tag
                parent.remove(obsolete)
                print( f"From parent='{parent}'',removed obsolete='{otag}'"
                    ,file=log_file)
                msg = (f"From par0 '{par0}' removed otag='{otag}'")
                print(msg, file=log_file)

    # prepare to add the child element as either new or a replacement
    # It is OK to add a new child here.

    if verbosity > 1:
        msg = ('{}: in {}, found PARENT to receive a new  node'
          .format(me, input_file_name))
        print(msg, file=log_file)

    # Create child node to append for this parent
    child_element = etree.Element(cet_name)
    child_element.text = child_model_element.text

    parent_nodes[0].append(child_element)
    if verbosity > 1:
        print("Using etname='{}'".format(cet_name),file=log_file)
        msg = ("appended to parent {} the child {}"
           .format(parent_nodes[0].tag, child_element.tag))
        print(msg, file=log_file)


    # Done modifying the in-memory documet.
    # Now output it in its file.
    # TODO: CHANGE AFTER TESTING
    # output_file_name = "{}.txt".format(input_file_name)
    # Production

    # Backup original mets file to a file under sub-directory sobek_files
    #
    # First, construct the backup file name
    vid_folder, relative_mets_file_name = os.path.split(input_file_name)
    fparts = relative_mets_file_name.split('.')
    # This extracts the bib_vid part of the mets.xml file name, assumed
    # to comply with the ufdc *.mets.xml file naming convention
    bib_vid = fparts[0]
    backup_folder_name = "{}\\sobek_files\\".format(vid_folder)

    # Just in case, make sure the backup dir is made
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
    # So the span of relevance for this record goes from the file md
    # creation date to the file name's encoded date
    copy2(input_file_name, backup_file_name)

    #Now overwrite the original input file

    output_file_name = input_file_name
    with open(output_file_name, 'wb') as output_file:
        # NOTE: alt to next would be
        # output_string = etree.tostring(node_root_input,
         #   xml_declaration=True).decode('utf-8')
        #output_string = (etree.tostring(
        #    node_root_input, pretty_print=True).decode('utf-8'))

        if verbosity > 0:
            msg="Writing to output file={}".format(output_file_name)
            print(msg, file=log_file)
        #output_string = output_string.replace(xml_tag_replace_char, ':')
        #REM: opened with mode='w' to output this type, a string
        # output_file.write(output_string)
        #doctree.write(output_file, xml_declaration=True)
        #doctree.write(output_file, xml_declaration=True, encoding="utf-8")
        doctree.write(output_file, xml_declaration=True, encoding="utf-8")
    return 1
# end def file_add_or_replace_xml

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

            rv = file_add_or_replace_xml(
                log_file=log_file,
                input_file_name=input_file_name,
                parent_tag_name=parent_tag_name,
                child_tag_namespace=child_tag_namespace,
                child_model_element=child_model_element,
                replace_children=replace_children,
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
    log_file_name=None,
    parent_tag_name=None,
    child_tag_namespace=None,
    child_model_element=None,
    replace_children=False,
    strftime_format="%Y%m%dT%H%MZ",
    verbosity=1,):

    me='run'
    n_files = 0

    if log_file_name is None:
        #datetime_string = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        day_string = datetime.datetime.utcnow().strftime(strftime_format)
        log_file_name = ("{}/mets_batch_edits_{}.txt"
            .format(input_folder,day_string))
    else:
        log_file_name = ("{}/{}"
            .format(input_folder, log_file_name))

    # utf-8-sig strips BOM as we desire
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
    print("{}:Using child local tag='{}'".format(me, child_model_element.tag)
        ,file=log_file)

    input_file_folders = [input_folder]

    n_files, n_changed, n_unchanged = process_files(
      backup_folder=backup_folder,
      input_folders=input_file_folders,
      parent_tag_name=parent_tag_name,
      child_tag_namespace=child_tag_namespace,
      child_model_element=child_model_element,
      file_globs=file_globs,
      replace_children=replace_children,
      log_file=log_file, verbosity=verbosity)

    msg = ("{}: ENDING: Processed {} files, and added a child node to {}.\n"
       .format(me, n_files, n_changed))
    print(msg, file=log_file)
    print(msg)
    return

#end def run()
# end main code


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()

    #Hold of on making this a command line parameter for now.
    #It could allow for critical outages

    # Note: do default to get some settings from user
    # config file, like passwords
    # Add help to instruct about MY_SECRETS_FOLDER, etc.
    # Arguments

    '''
    parser.add_argument("-v", "--verbosity",
      type=int, default=1,
      help="output verbosity integer (0 to 2)")

    parser.add_argument("-i", "--input_folder",
      #required=True,
      # default="U:\\data\\elsevier\\output_exoldmets\\test_inbound\\",
      help='All .DAT and .MON files anywhere under this folder will be read '
          'for imports. The import program will here create the file or '
          'overwrite a previous import log file.' )

    parser.add_argument("-x", "--max_exception_logs_per_file",
      type=int, default=5,
      help='Maxiumum number of insert exceptions to report per input file.' )


    parser.add_argument("-l", "--log_file_name",
      #required=True,
      # default="U:\\data\\elsevier\\output_exoldmets\\test_inbound\\",
      help='This is the name of the output log file to be placed under your '
      'input folder. If not given, the log_file_name defaults to'
      'import_buoy_sensor_data_log.txt.'
     )

    args = parser.parse_args()
    '''
    # Settings for 20180620 la democracia bib
    # PRODUCTION -
    # backup_folder = ('C:\\rvp\\data\\backups\\mets_batch_editor')
    backup_folder = None
    replace_children = False
    #20180625b - use None as backup folder - now we assume we have sub folder
    # sobek_files per item and write backup there
    # bib_type =  1

    # bib_type = 2
    bib_type = 3

    if bib_type == 1:
        input_folder = ('F:\\ufdc\\resources\\AA'
          '\\00\\05\\28\\74\\'
          )
        replace_children = False
    # TESTING
    # input_folder = ('c:\\rvp\\tmpdir\\' )
    # input_folder = ('c:\\rvp\\data\\test_vids\\' )

    ######## Set up args for xml node replacements
    #

    # { These variables will be runtime parameters

        child_model_text = '''El periódico La Democracia, fundado y dirigido por
Luis Muñoz Rivera en 1890 y publicado en principios desde Ponce, Puerto Rico.

Abogó por los principios del Partido Autonomista, de corte liberal que
buscaba mayores derechos con la Corona Española. Incluía temas políticos
como situaciones internas de delegados y protestas del pueblo, mantenía
diálogo con otros periódicos, publicaba las propuestas de los diputados a
Cortes, los tratados de España con otros países y la insurrección de Cuba.
En cuanto a lo económico, protestó la imposición de tarifas sobre azúcar y
otros productos y la prohibición del café hacia Cuba, publicó protestas de
comerciantes de San Juan y embargos de fincas. Apoyó la creación de
Asociación de Agricultores, el Banco Agrícola y la Exposición Santurce, en
busca de soluciones económicas, sin éxito.

En 1895, al declararse la guerra de Cuba, y luego de la reorganización del
Partido Autonomista, Muñoz Rivera viajó a Madrid en busca de la autonomía,
desde donde escribía regularmente en el periódico. Entre 1896-98, el periódico
concentró sus esfuerzos en el tema político hasta la elección de los
Diputados, quienes nunca se reunieron por estallar la Guerra.
'''
    elif bib_type == 2:
        input_folder = ('F:\\ufdc\\resources\\AA'
          '\\00\\03\\16\\01\\'
          )
        # TESTING
        # { These variables will be runtime parameters

        replace_children = False
        child_model_text = '''Como un eco de La Correspondencia de España, el
diario La Correspondencia de Puerto Rico fue fundado por Ramón B. López en
San Juan, el 18 de diciembre de 1890. Llegó a ser el periódico de mayor
circulación y exposición popular, con precio de un centavo, y una tirada de
5,000 ejemplares diarios. Por eso se le adjudicó el sobrenombre sarcástico
de “El periódico de las cocineras”. Se inició en él el formato del
periódico reporteril para llegar a las masas.
En su tesis doctoral de Historia del 2007, Análisis histórico de la noción
del “periodismo profesional” en Puerto Rico (del siglo XIX al XX),
Luis Fernando Coss destacó los elementos de modernidad que la publicación
de La Correspondencia de Puerto Rico supuso en los 1890. Una ruptura clara
con el partidismo tradicional de la prensa, un interés en abordar asuntos de
pertinencia general, más allá de los reclamos localistas de la prensa de la
Capital, Ponce y Mayagüez, y un alarde de objetividad marcaron al nuevo periódico.
La Correspondencia, en su cobertura de la discusión de los aranceles en
1895, en su sobria discusión de los monopolios y las protestas urbanas
contra ellos, y en su enfoque sobre la nueva guerra de independencia cubana
alcanzó la atención de lectores de toda la isla. Para el investigador son
importantes los textos de este periódico de los años 1897, 1898 y 1899.
La instalación del gabinete autonómico, las elecciones de marzo de 1898,
la Guerra Hispanoamericana, las dificultades del gobierno autonómico para
conseguir financiamiento de las obras públicas,  la invasión de Puerto Rico,
los primeros reportajes sobre la zona de ocupación estadounidense entre
agosto y octubre de 1898, las transiciones de poder del gabinete autonómico
al gobierno militar en 1899, así como las medidas de los gobernadores
Guy V. Henry y George Davies en el difícil año de 1899, en torno a la
jornada laboral de 8 horas, la suspensión de ejecuciones sobre hipotecas
de propietarios agrícolas  y el canje de la moneda provincial por la
norteamericana, especialmente después del huracán del día de San Ciriaco
(8 de agosto) dan múltiples matices y detalles que no se encuentran
fácilmente en otras publicaciones periódicas de la época.
En sus inicios, la gerencia del periódico quiso proscribir la literatura;
sin embargo, entrado el siglo XX y, sobre todo cuando Manuel Zeno Gandía
compra el diario el 30 de abril de 1902, el médico y literato le dio otro
giro, divulgando en sus columnas poemas de escritores valiosos y
reconocidos posteriormente. Sirvió de ese modo como vehículo para la
divulgación del modernismo literario en la isla. Durante la primera década
del siglo XX tomó un giro político afiliado al partido Unión de Puerto Rico
(1904) tras la consigna del gobierno propio o self-government y la
definición del status, fungiendo como portavoz de las preocupaciones
derivadas de la Ley Orgánica de 1900 (Ley Foraker) y la organización del
gobierno civil, atento al progreso económico e intelectual de Puerto Rico.
'''
    # end if bib_type == 2
    elif bib_type == 3:
        #Request by Melissa Jerome via email 20180813 to rvp
        input_folder = (
          'F:\\ufdc\\resources\\AA\\00\\05\\28\\74\\'
          )

        replace_children = True
        child_model_text = '''La Democracia

El periódico La Democracia, fundado y dirigido por Luis Muñoz Rivera en 1890 y publicado en principios desde Ponce, Puerto Rico.

Abogó por los principios del Partido Autonomista, de corte liberal que buscaba mayores derechos con la Corona Española. Incluía temas políticos como situaciones internas de delegados y protestas del pueblo, mantenía diálogo con otros periódicos, publicaba las propuestas de los diputados a Cortes, los tratados de España con otros países y la insurrección de Cuba. En cuanto a lo económico, protestó la imposición de tarifas sobre azúcar y otros productos y la prohibición del café hacia Cuba, publicó protestas de comerciantes de San Juan y embargos de fincas. Apoyó la creación de Asociación de Agricultores, el Banco Agrícola y la Exposición Santurce, en busca de soluciones económicas, sin éxito.

En 1895, al declararse la guerra de Cuba, y luego de la reorganización del Partido Autonomista, Muñoz Rivera viajó a Madrid en busca de la autonomía, desde donde escribía regularmente en el periódico. Entre 1896-98, el periódico concentró sus esfuerzos en el tema político hasta la elección de los Diputados, quienes nunca se reunieron por estallar la Guerra Hispanoamericana. A principios de 1899, Muñoz Rivera viajó a Washington para exigir gobierno civil y fue respaldado por listas de liberales de todos los pueblos, publicadas en el periódico.

Con la Ley Foraker, o el gobierno civil, continuaron las protestas en el periódico por quiebras, emigraciones a Cuba, mala calidad harinas importadas, Tarifa Dingley a importaciones, Bill Hollander, horrores de emigración a Hawaii, manifestaciones socialistas, exigencia a los maestros de pasar examen de inglés, celebración de días patrios de Estados Unidos, castigos corporales a los niños en las escuelas y la intromisión de los carpetbaggers. En 1904, Muñoz Rivera fundó un nuevo partido llamado Unión, para unir a federales y republicanos contra los atropellos de las leyes impuestas, e imposibilidad de acción de la Cámara de Delegados que el periódico llamó cámara de esclavos.

El aspecto social y cultural de Puerto Rico a través de los anuncios y editoriales, es tema importante del periódico.  Antes del ’98, anuncios de compañías extranjeras como vapores de correos franceses, seguros contra incendios de Hamsburgo, compañía italiana de teatro, reseñas sobre vida en Haití y el circo americano, demuestran aperturas del mercado puertorriqueño.  Internamente, anuncios de actividades del Ateneo, certámenes literarios, de música y pintura, actividades del Círculo Sangermeño, de Escuela Laica Espiritista, problemas de la Iglesia Católica, Celebraciones del Cuarto Centenario, son huellas de vida cotidiana. Luego del ’99, se anuncia la New York Porto Rico Steamship Co. y la Colonial Leaf Tobacco Co., se diseña un nuevo escudo para Porto Rico, se legisla el Código Civil que permitía el divorcio, se comienza a discutir el feminismo, y se distribuyen pasaportes puertorriqueños.

Para 1905, el periódico se anuncia como el de más circulación de Puerto Rico y con su sede en San Juan.  Para esa época, es uno comercial y más interesado en la noticia que se crea desde la esferas gubernamentales.

        '''
    else:
        raise ValueError("Unknown bib_type={}}.format(bit_type)")

    # These element names will be runtime params
    parent_tag_name="mods:mods"
    child_tag_name = 'mods:abstract'
    # }

    eparts = child_tag_name.split(':')
    if len(eparts) == 2:
        child_tag_namespace = eparts[0]
        child_tag_localname = eparts[1]
    else:
        child_tag_namespace = ''
        child_tag_localname = child_tag_name

    # child_model_element is the node to insert under parent if it lacks a
    # child node like child_model_element
    # or there is no child check path defined
    child_model_element = etree.Element(child_tag_localname)
    child_model_element.text = child_model_text
    sys.stdout.flush()

    run(backup_folder=backup_folder, input_folder=input_folder,
        log_file_name='batchlog.txt',
        file_globs = ['**/*.mets.xml'],
        parent_tag_name=parent_tag_name,
        child_tag_namespace=child_tag_namespace,
        child_model_element=child_model_element,
        replace_children=replace_children,
        verbosity=2)

#end if __name__ == "__main__"
#END FILE
