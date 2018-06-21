'''
mets_batch_edit.py
20180620-Robert Phillips

Python 3.6+ code
'''

import sys, os, os.path, platform

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

#import regex
import re

def sequence_paths(log_file=None, input_folders=None, input_path_globs=None, verbosity=0):
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

from tempfile import NamedTemporaryFile, mkstemp, TemporaryFile
from shutil import move
from os import remove

def file_replace_pattern(input_file_name=None, pattern=None,
    log_file=None,
    substitution=None, verbosity=0):
    me = "file_replace_pattern"

    file_like_obj = NamedTemporaryFile(mode='w')

    temp_file = file_like_obj
    temp_file_name = file_like_obj.file.name
    if verbosity > 0:
      msg=("Got temp file name='{}'".format(temp_file_name))
      print(msg,log_file)
      log_file.flush()
    if verbosity > 0:
        msg=("{}: processing input file name '{}', pattern='{}'"
          .format(me,input_file_name,pattern))
        print(msg)
        print(msg, file=log_file)
    if 1 == 1:
        n_lines = 0
        with open(input_file_name) as input_file:
            #for n_lines, line in enumerate(input_file):
            for line in input_file:
                line = line.replace(pattern, substitution)
                temp_file.write(line)
                if verbosity > 0:
                    msg=("{}: Wrote line='{}'".format(me,line))
                    print(msg)
                    print(msg, file=log_file)
        remove(input_file_name)
        move(temp_file_name, input_file_name)
    # end with NamedTemporaryfile
    return n_lines
# end def file_edit

def process_files(input_folders=None, file_globs=None, pattern=None,
    substitution=None, verbosity=1, log_file=None):

        me = 'process_files'
        file_count = 0

        total_file_lines = 0
        log_file = log_file
        if verbosity > 0:
            msg = ("{}:processing files for input_folders={}, globs={}"
              .format(me,input_folders,file_globs))
            print(msg)
            print(msg,file=log_file)

        gpaths = sequence_paths(log_file=log_file, input_folders=input_folders,
            input_path_globs=file_globs, verbosity=verbosity)

        paths = []
        n_lines=0

        for path in gpaths:
            if verbosity > 1:
                print("{}:Got path.resolve()='{}'".format(me,path.resolve()))
            if path in paths:
                # gpaths could have duplicates when mulitple globs
                # were used to generate the gpaths, so skip dups
                # If carefully chosen to guarantee the globs have no dups,
                # one can bypass this checking
                continue
            #Store this path to reject future duplicates in the sequence
            paths.append(path)

            # Start processing a file
            file_count += 1

            input_file_name = path.resolve()
            if verbosity > 1:
                print("{}:processing file = '{}'"
                  .format(me,input_file_name),file=log_file)

            #n_rows, n_inserts, n_exceptions = self.import_file(
            n_lines = file_replace_pattern(
                log_file=log_file,
                input_file_name=input_file_name, pattern=pattern,
                substitution=substitution, verbosity=verbosity)


            total_file_lines += n_lines

            #l_rows = ['one']
            if verbosity > 0:
                print(
                   "{}: Processed file {}={} with {} physical lines."
                  .format(me, file_count, input_file_name, n_lines)
                  ,file=log_file)

        # end for path in paths

        if verbosity > 0:
            print("{}: Ending with {} files with {} lines found and processed."
                .format(me,file_count,n_lines), file=log_file)

        return file_count, n_lines
# end def process_files

import datetime
def run(input_folder=None, file_globs=None,
    log_file_name=None, pattern=None,
    substitution=None, strftime_format="%Y%m%dT%H%MZ",
    verbosity=1,):

    me='run'

    if log_file_name is None:
        #datetime_string = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        day_string = datetime.datetime.utcnow().strftime(strftime_format)
        log_file_name = ("{}/mets_batch_edits_{}.txt"
            .format(input_folder,day_string))
    else:
        log_file_name = ("{}/{}"
            .format(input_folder,log_file_name))

    log_file = open(log_file_name, mode="w", encoding='utf-8')

    if verbosity > 0:
        msg="{}: Using log_file_name='{}'".format(me,log_file_name)
        print(msg, file=log_file)

    print("{}: STARTING: Using verbosity value={}".format(me, verbosity)
        ,file=log_file)

    print("{}:Using data input_folder={}".format(me, input_folder)
        ,file=log_file)

    print("{}:Using target pattern='{}'".format(me, pattern)
        ,file=log_file)

    print("{}:Using substitution='{}'".format(me, substitution)
        ,file=log_file)

    input_file_folders = [input_folder]

#def process_files(input_folders=None, file_globs=None, pattern=None,
#    substitution=None, verbosity=1):
    n_files, n_lines = process_files(input_folders=input_file_folders,
      file_globs=file_globs,pattern=pattern, substitution=substitution,
      log_file=log_file, verbosity=verbosity)

    msg = ("{}: ENDING: Processed {} files, with {} lines.\n"
       .format(me, n_files, n_lines))
    print(msg, file=log_file)
    print(msg)
    return

#end def run()
# end main code

# Launch the run() method with parsed command line parameters

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
    # PRODUCTION
    # input_folder = ('F:\\flvc.fs.osg.ufl.edu\\ufdc\\resources\\AA'
    #  '\\00\\02'
    #  )
    # TESTING
    input_folder = ('c:\\rvp\\tmpdir\\' )
    #input_folder = ('/c/rvp/tmpdir' )

    pattern = '<mods:mods>'
    substitution = '''<mods:mods>
<abstract>
El periódico La Democracia, fundado y dirigido por Luis Muñoz Rivera en
1890 y publicado en principios desde Ponce, Puerto Rico.

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

</abstract>'''

    run(input_folder=input_folder,
        log_file_name='testlog.txt',
        file_globs = ['*.xml'],
        pattern=pattern,
        substitution=substitution,
        verbosity=1)

#end if __name__ == "__main__"

#END FILE
