'''
Method test_loader()

Tests a Ufdc_loader object (also coded in this file) that is set to
load (copy) mets files from a a mounted staging directory to a
UFDC load directory.

At first, cron will call this method, and later a different
scheduling system may be used to call this.

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
    sys.path.append('{}git/citrus/modules'.format(modules_root))
    return
register_modules()
import etl
from shutil import copy
from etl import sequence_paths
from pathlib import Path

class Ufdc_loader():
    '''
    <param name='staging_folder'> The directory where to-be-loaded METS
    files are to be found,  with filenames ending .mets.xml.
    Each METS file should be named bib_vid.mets.xml and should be found in
    a subfolder named by the BIB and a subfolder named by the VID.
    All mets files and other files found in the folder of the METS file will
    be copied.

    The bib_vid prefix name of the *mets.xml file will be matched with the two
    parent folder names and a warning will issue if the bib_vid values do not
    match.
    </param>

    <param name="inbound_folder"> The directory where the METS files are to
    be copied, which should be an inbound UFDC folder where the builder is
    looking for files to load. <param>

    Note that this program is intended to be scheduled to run on a linux
    host via a cron job. Other scheduling systems may be supported later.

    '''

    def __init__(self, staging_folder=None, inbound_folder=None):
        required_args = [staging_folder, inbound_folder]
        if not all(required_args):
            msg = ("Not all required args supplied: {}".format(required_args))
            raise ValueError(msg)

        self.staging_folder = staging_folder
        self.inbound_folder = inbound_folder
        incoming_mets_dirname = (
            '/'.join(self.inbound_folder.split('/')[:-1]))
        self.failures_folder = "/{}/failures".format(incoming_mets_dirname)
        self.input_file_globs = ["**/*.mets.xml"]
        self.log_file = sys.stdout

        return

    def valid_mets_copy(self, mets_input_path=None, verbosity=1):
        '''
        We found the absolute path to a mets file to copy to the inbound folder.
        Also copy any of its sibling files in the staging area.

        '''
        me = 'valid_mets_copy'

        # todo: more coding to validate
        # todo: consider: maybe also allow any subfolder with a mets.xml file

        staging_file_name = mets_input_path.resolve()
        staging_mets_dirname = os.path.dirname(staging_file_name)
        staging_mets_basename = os.path.basename(staging_file_name)
        # construct parent folder from the bib_vid in the filename itself.
        dparts = staging_mets_basename.split('.')
        bparts = dparts[0].split('_')

        if len(bparts) != 2:
            msg = ("Input filename '{}' has illegal bib vid prefix.",
                input_file_name)
            raise ValueError(msg)

        bib = bparts[0]
        vid = bparts[1]
        inbound_mets_dirname = "{}{}{}_{}".format(self.inbound_folder,
            os.sep,bib,vid)
        os.makedirs(inbound_mets_dirname, exist_ok=True)

        # For each file in the staging_mets_folder, copy it to the
        # inbound_mets_folder

        staging_mets_folders = [staging_mets_dirname]
        # create/use the incoming failure folder as a temporary folder
        print("Copying input files from folder={}".format(staging_mets_dirname)
         , flush=True)
        fpaths = sequence_paths(input_folders=staging_mets_folders,
            input_path_globs=["*.*"])

        for fpath in fpaths:
            input_file_name = fpath.resolve()

            if verbosity > 0 or 1 == 1:
                print("{}: Copying input file '{}' to {}"
                    .format(me,input_file_name,inbound_mets_dirname)
                    ,flush=True, file=self.log_file )
            copy(input_file_name, inbound_mets_dirname)
        # end for fpath in fpaths

        return 1
    #end def valid_mets_copy

    def load(self, max_mets_files=0, verbosity=0):
        # Get list of paths of .mets.xml files under staging folder.
        #
        input_folders = [self.staging_folder]
        paths = sequence_paths(input_folders=input_folders,
            input_path_globs=self.input_file_globs)

        n_loaded = 0
        file_count = 0
        for path in paths:
            file_count += 1
            was_copied = self.valid_mets_copy(mets_input_path=path,
                verbosity=verbosity)
            n_loaded += was_copied
            if max_mets_files > 0 and n_loaded >= max_mets_files:
                #maybe add code to print to log file here...
                break
        # end for path in paths

        return n_loaded

#end class Ufdc_loader

def test_ufdc_loader(env=None):
    me = 'test_ufdc_loader'
    if env is None:
        env = 'uf_office'

    if env == 'uf_office':
        staging_folder = "U:\\data\\elsevier\\output_exoldmets\\staging\\"
        inbound_folder = "C:\\rvp\\data\\test_inbound\\"
    else:
        msg = "Unknown env='{}'".format(env)

    log_file_name = "{}/{}".format(staging_folder,"load_to_ufdc.txt")
    with open(log_file_name, mode='w', encoding='utf-8') as log_file:
        print("{}:Starting".format(me))
        ufdc_loader = Ufdc_loader(staging_folder=staging_folder,
            inbound_folder=inbound_folder)
        # Run a loading run

        n_loaded = ufdc_loader.load(max_mets_files=10)
        print("{}: loaded {} mets files".format(me, n_loaded))

    print("{}:Ending".format(me))
    #end with log_file
#end def test_ufdc_loader

test_ufdc_loader(env='uf_office')
