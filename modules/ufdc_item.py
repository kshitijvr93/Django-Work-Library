# python3.6 code for ufdc_item.py
import os
import sys

class UFDCItem():

    def get_file_system_path(self, path=None, log_file=None, verbosity=1 ):
        '''
        Given a path string (if None, then self.ufdc_resources_folder is used),
        use the items bib and vid to derive the ultimate item folder path
        and return that.
        '''
        me = 'UFDCItem:file_system_path'
        bib = self.bib
        vid = self.vid
        if path is None:
            path = self.resources_folder
        if log_file is None:
            log_file = sys.stdout
        sep = os.sep
        for i in range(0,10,2):
            path += (sep + bib[i:i+2])
        path += (sep + self.vid)

        if verbosity > 0:
            msg = f'{me}: For item bib={bib}, vid={vid}, made path={path}'
            print(msg, file=log_file, flush=True)
        return path
    # end def file_system_path()

    def __init__(self, bib=None, vid='00001',
        resources_folder='F:\\ufdc\\resources',
        log_file_name=None, log_file=None,verbosity=1):

        me = 'UFDCItem:__init__()'
        if bib is None: # error for now, but maybe add new bib here later?
            msg = f'{me}: Missing bib argument.'
            raise ValueError(msg)
        if log_file is None:
            log_file = sys.stdout

        self.log_file = log_file
        self.bib = bib
        vid = '00001' if vid is None else vid
        self.vid = vid
        self.resources_folder = resources_folder
        self.log_file_name = log_file_name
        self.folder_path = (self.get_file_system_path())
        self.mets_folder = self.folder_path

        self.d_mets_namespace = None
        self.mets_tree = None

        if verbosity > 0:
            msg = f'{me}:mets_folder={self.folder_path}'
            print(msg, flush=True)

        # Derive and set METS File Name
        # Change later to honor maw_settings.UFDC
        self.mets_file_name = ( self.folder_path
            + os.sep + bib + '_' + vid + '.mets.xml')
        if verbosity > 0:
            msg = f'{me}:Set mets_file_name={self.mets_file_name}'
            print(msg, file=log_file)
    #end def __init__

    def get_mets_tree(self):
        '''
        From self.file_path for the mets file, parse the mets tree
        and set self.mets_tree and self.d_mets_namespace

        Retun them as a possible convenience, but also set them in self.
        '''
        self.mets_tree = None
        self.d_mets_namepace = None

        return self.mets_tree, self.d_mets_namespace

    def sequence_by_glob(self, file_glob=None):
        '''todo
        For the given glob, return a sequence (generator) of the
        file(s) under the folder_path of this element
        '''
        pass
        return

    #end def get_mets_tree()

# end class UFDCItem
