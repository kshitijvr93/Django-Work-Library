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

    def __init__(self, staging_folder=None, inbound_folder=None,verbosity=0
        ,log_file=None):
        required_args = [staging_folder, inbound_folder]
        if not all(required_args):
            msg = ("Not all required args supplied: {}".format(required_args))
            raise ValueError(msg)
        # Note: not using param verbosity yet, but keep for future.

        self.staging_folder = staging_folder
        self.inbound_folder = inbound_folder
        incoming_mets_dirname = (
            '/'.join(self.inbound_folder.split('/')[:-1]))
        # Might use failures_folder later for a temporary staging area
        # to copy files under one folder there for one vid,
        # then when done, rename the temp folder to one
        # under folder inbound, if copy atomicity becomes an issue.
        self.failures_folder = "/{}/failures".format(incoming_mets_dirname)
        self.input_file_globs = ["**/*.mets.xml"]
        self.log_file = log_file
        # Note: do not set a self.verbosity, but do support separate verbosity
        # args in  constructor and methods.

        return

    def valid_mets_copy(self, mets_input_path=None,verbosity=0):
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
        if verbosity > 0:
            print("Copying input files from folder={}"
                .format(staging_mets_dirname), flush=True,
                file=self.log_file)

        fpaths = sequence_paths(input_folders=staging_mets_folders,
            input_path_globs=["*.*"])

        for fpath in fpaths:
            input_file_name = fpath.resolve()

            if verbosity > 0 :
                print("{}: Copying input file '{}' to {}"
                    .format(me, input_file_name, inbound_mets_dirname)
                    ,flush=True, file=self.log_file )
            copy(input_file_name, inbound_mets_dirname)
        # end for fpath in fpaths

        return 1
    #end def valid_mets_copy

    def load(self, max_mets_items=0, verbosity=0):
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
            if max_mets_items > 0 and n_loaded >= max_mets_items:
                #maybe add code to print to log file here...
                break
        # end for path in paths

        return n_loaded

#end class Ufdc_loader
def run_ufdc_auto_loader(
    log_file=None,
    max_mets_items=10,
    verbosity=0,
    staging_folder=None, inbound_folder=None,
    ):

    me = 'run_ufdc_auto_loader'
    required_args = [staging_folder, inbound_folder]

    if not all(required_args):
        msg = ("{}: Some required args missing: {}"
            .format(me,required_args))
        raise ValueError(msg)

    if log_file is not None:
        print("{}:Starting".format(me), file=log_file)
        ufdc_loader = Ufdc_loader(staging_folder=staging_folder,
            inbound_folder=inbound_folder,verbosity=verbosity,
            log_file=log_file)
        # Run a loading run

        n_loaded = ufdc_loader.load(max_mets_items=max_mets_items)
        print("{}: loaded {} mets files".format(me, n_loaded),
            file=log_file)
    return
#end def run_ufdc_auto_loader

''' test cli runs:

Paste some example cli lines here:


Also see nice package 'schedule' in the accepted answer:
https://stackoverflow.com/questions/373335/how-do-i-get-a-cron-like-scheduler-in-python

'''
import schedule
import time

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    # Arguments
    parser.add_argument("-l", "--log_file",
     default="U:\\data\\run_logs\\ufdc_load_log.txt",
     help="Name of a log file to create and put processing messages in.")

    parser.add_argument("-r", "--maximum_runs",
     type=int, default=2,
     help="Maximum number of runs (0=no maximum, 1=default)")

    parser.add_argument("-p", "--pause_seconds",
     type=int, default=6,
     help="Number of seconds to pause between runs")

    parser.add_argument("-m", "--max_mets_items",
     type=int, default=10,
     help="If not 0, limit the MET items per run to copy from staging to UFDC inbound.")

    parser.add_argument("-v", "--verbosity",
     type=int, default=1,
     help="increase output verbosity")

    parser.add_argument("-s", "--staging_folder",
     default = "U:\\data\\elsevier\\output_exoldmets\\test_maw_loader\\",
     help="parent folder above subfolders with METS items to copy")

    parser.add_argument("-u", "--ufdc_inbound_folder",
     # default = "F:\\usf\\incoming\\test_inbound\\",
     default = "U:\\data\\elsevier\\output_exoldmets\\test_inbound\\",
     help="UFDC inbound folder to paste METS items for the builder")

    args = parser.parse_args()

    log_file = open(args.log_file, mode="w", encoding='utf8')

    if args.verbosity:
        print("STARTING: Using verbosity value={}".format(args.verbosity)
            , file=log_file)
        print("Using staging_folder={}".format(args.staging_folder)
            , file=log_file)
        print("Using ufdc_inbound_folder={}".format(args.ufdc_inbound_folder)
            , file=log_file)

    log_file.flush()
    # OVERWRITE log_file - had set it to stdout for some tests

    schedule.every(args.pause_seconds).seconds.do(

        run_ufdc_auto_loader,verbosity=args.verbosity,
            staging_folder=args.staging_folder,
            max_mets_items=args.max_mets_items,
            inbound_folder=args.ufdc_inbound_folder,
            log_file=log_file,

        )

    # Run pending runs
    runs = 0
    while 1:
        runs += 1
        if runs > args.maximum_runs:
            break

        print("Run cycle {} is starting:".format(runs) ,file=log_file)
        try:
            schedule.run_pending()
            time.sleep(args.pause_seconds)
        except Exception as ex:
            # If OS causes a kill, eg by task manager,
            # perhaps an exception will be  caught here first.
            print("Program is ending with exception='{}'."
                .format(ex) ,file=log_file)
    log_file.flush()
    log_file.close()
    #done!
    # Note: on windows you can use task manager to stop this task
    # once you know it pid.
