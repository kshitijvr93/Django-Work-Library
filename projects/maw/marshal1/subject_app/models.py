from django.db import models

# Create your models here.
import uuid
import os, sys
from django.db import models
from django.utils import timezone
import datetime
#from django_enumfield import enum

#other useful model imports at times (see django docs, tutorials):
import datetime
from django.utils import timezone
from maw_utils import SpaceTextField, SpaceCharField, PositiveIntegerField

from dps.models import BatchSet, BatchItem
#from django.apps import apps
#BatchSet = apps.get_model('dps','BatchSet')
#BatchItem = apps.get_model('dps','BatchSet')

import threading
import maw_settings
from time import sleep
from django.contrib.auth import get_user_model
User = get_user_model()

#BatchSet = apps.get_model('dps','BatchSet')
#BatchItem = apps.get_model('dps','BatchSet')

'''
NOTE: rather than have a separate file router.py to host HathiRouter, I just
put it here. Also see settings.py should include this dot-path
as one of the listed strings in the list
setting for DATABASE_ROUTERS.

'''
# Maybe move the HathiRouter later, but for now keep here
#
class SubjectAppRouter:
    '''
    A router to control all db ops on models in the hathitrust Application.
    '''

    # app_label is really an app name. Here it is hathitrust.
    app_label = 'subject_app'

    # app_db is really a main settings.py DATABASES name, which is
    # more properly a 'connection' name
    app_db = 'subject_app_connection'

    '''
    See: https://docs.djangoproject.com/en/2.0/topics/db/multi-db/
    For given 'auth' model (caller insures that the model is always an auth
    model ?),  return the db alias name (see main DATABASES setting in
    settings.py) to use.
    '''
    def db_for_read(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return self.app_db
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return self.app_db
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (   obj1._meta.app_label == self.app_label
           or  obj2._meta.app_label == self.app_label):
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == self.app_label:
            return db == self.app_db
        return None

#end class

# Create your models here.
#
# NB: we accept the django default of prefixing each real
# db table name with the app_name, hence the model names
# below do not start with hathi or hathitrust.
# class HathiItemState(enum.Enum):
#       HAS_FOLDER = 0
#       FOLDER_LOADED = 1
#       FILES_EXAMINED = 2
#       FILES_NEED_CHANGES = 3
#       YAML_CREATED = 4


from pathlib import Path
from natsort import natsorted
from shutil import copy2, make_archive, move

def line(s=''):
    return '\n>' + s
def resource_path_by_bib_vid(bib_vid=None):
    if not bib_vid:
        raise ValueError(f'Bad bib_vid={bib_vid}')
    parts = bib_vid.split('_')
    count = len(parts)
    if count != 2:
        raise ValueError(f'Bad count of parts for bib_vid={bib_vid}')
    if len(parts[0]) != 10:
        raise ValueError(f'Bib is not 8 characters in bib_vid={bib_vid}')
    if len(parts[1]) != 5:
        raise ValueError(f'Vid is not 5 characters in bib_vid={bib_vid}')
    path = ''
    sep = ''
    for i in range(0,10,2):
        path = path + sep + parts[0][i:i+2]
        sep = os.sep
    path += sep
    path += parts[1]
    return path

import hashlib
def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

import os
import datetime
def modification_utc_str_by_filename(filename):
    t = os.path.getmtime(filename)
    d = datetime.datetime.fromtimestamp(t)
    du = datetime.datetime.utcfromtimestamp(t)
    tz = du - d
    utc_str = du.strftime("%Y-%m-%dT%H:%M:%SZ")
    d_str = d.strftime("%Y-%m-%dT%H:%M:%S")
    return d_str, tz, utc_str

def make_jp2_package(in_dir=None, out_dir_bib=None, resources=None, bib=None,
    vid=None,log_file=None, verbosity=0):
    me = 'make_jp2_package'
    jp2_count = 0
    bib_vid = f"{bib}_{vid}"

    msg = ( f'{me}: PROCESSING {bib_vid}:')
    print(msg, file=log_file)
    log_file.flush()

    # output dir for files
    out_dir_files = os.path.join(out_dir_bib,'files')

    # make the files output directory if not exists
    os.makedirs(out_dir_files, exist_ok=True)

    # We will output md5 info to this file in the bib dir.
    # After it is completed we will move it to the files dir.
    out_name_md5 = out_dir_bib + os.sep + 'checksum.md5'
    capture_date = ''

    with open(out_name_md5, mode='w') as out_file_md5:
        #Find all jp2 files in the input dir, in sorted order
        # NOTE: each file will be copied to a renamed output file, per
        # Hathitrust file naming requirements
        # First get the paths for all files in input directory;
        # hathi_image_tuples = [('*.tif*','.tif'), ('*.jp2','.jp2') ]
        # 20180806 - Now we only do jp2 images.
        hathi_image_tuples = [('*.jp2','.jp2') ]
        for tuple in hathi_image_tuples:
            # Copy image files of this glob
            glob = tuple[0]
            ext = tuple[1]
            paths = list(Path(in_dir).glob(glob))
            n_paths = len(paths)
            msg += line(f'Processing {n_paths} files with extension {ext}.')

            # Sort the paths for this glob
            sorted_paths = natsorted(paths)
            #Copy each file to one with the HathiTrust-preferred name
            for i, in_path in enumerate(sorted_paths, 1):
                in_name = str(in_path)
                jp2_count += 1

                if verbosity > 1:
                  msg += line(
                      f'{me}: processing file {i} PACKAGE FOR '
                      f'bib_vid {bib_vid}.')
                print(msg, file=log_file)
                log_file.flush()

                if i == 1:
                    dstr, tz, utcstr = modification_utc_str_by_filename(in_path)
                    # str_tz : Lop of the 'seconds' part of the tz
                    str_tz = str(tz)
                    index_last_colon = str_tz.rfind(':')
                    if index_last_colon > 0:
                        str_tz = str_tz[0:index_last_colon]

                    capture_date = f'{dstr}-{str_tz}'
                    if verbosity > 1:
                      msg += line(f'\nGot dstr={dstr}\n')
                      msg += line(f'\nGot tz={tz}\n')
                      msg += line(f'\nGot utcstr={utcstr}\n')
                      msg += line(f'\nGot capture_date={capture_date}\n')

                out_base = str(i).zfill(8)
                out_base_ext = out_base + ext
                out_name = out_dir_files + os.sep + out_base_ext

                in_base = in_name.split('.')[0]
                #msg += line()
                #msg += line( f'{i}: Copying in_name ={in_name} '
                #    f'to output_name={out_name}')

                copy2(in_name, out_name)

                # Write checksum.md5 file line for this file in  package
                md5sum = md5(in_name)
                msg += line( f"{i}: {in_name} md5sum='{md5sum}'")
                out_file_md5.write(f'{md5sum} {out_base_ext}\n')

                #for ext_t in ['.pro','.txt']:
                # Copy txt files only now
                text_files_found = True
                for ext_t in ['.txt',]:
                    # seek similar file name ending .txt
                    try:
                        in_name = in_base + ext_t
                        out_base_ext = out_base + ext_t
                        out_name = out_dir_files + os.sep + out_base_ext
                        #msg += line( f'{i}: Copying in_name ={in_name}, '
                        #    f'to output_name={out_name}')
                        copy2(in_name, out_name)

                        # Write checksum.md5 file line for this package file.
                        md5sum = md5(in_name)
                        if verbosity > 1:
                          msg += line( f"{i}: {in_name} md5sum='{md5sum}'")
                        out_file_md5.write(f'{md5sum} {out_base_ext}\n')

                    except FileNotFoundError:
                        msg = (f'File {in_name} not found. '
                          f'SKIPPING this bib_vid {bib_vid}')
                        print(f"ERROR:{msg}",file=log_file)
                        log_file.flush()
                        return jp2_count
                # end for ext- in .txt
            #end for i, path in glob type (jp2)
        #end for hathi_image_tuples

        # output required HathiTrust meta.yml file
        yaml_base_name = 'meta.yml'
        yaml_file_name = out_dir_files + os.sep + yaml_base_name
        with open(yaml_file_name, mode='w') as yaml_file:
          yaml_file.write(f"capture_date:{capture_date}")

        md5sum = md5(yaml_file_name)
        msg += line( f"YAML FILE: {yaml_file_name} md5sum='{md5sum}'")
        out_file_md5.write(f'{md5sum} {yaml_base_name}\n')
    #with open --- checksum.md5 as out_file_md5

    # TODO:move the checksum.md5 file from the bib dir to the files dir
    out_renamed_md5 = out_dir_files + os.sep + 'checksum.md5'
    move(out_name_md5, out_renamed_md5)

    # Create zip archive
    out_base_archive_file = out_dir_bib + os.sep +  bib_vid
    make_archive(out_base_archive_file, 'zip', out_dir_files)
    msg += line( f'Made archive file {out_base_archive_file}.zip for '
                 f'directory {out_dir_files}')
    msg += line('')
    msg += line(f'{me}: Finished package FOR bib_vid {bib_vid}.\n')

    print(msg, file=log_file)
    log_file.flush()
    return jp2_count

#end def make_jp2_package

def make_jp2_packages(obj):
    '''
    Given a batch_set_id fkey into db table dps_batch_set,
    for each bibvid item in the batch, generate a jp2-style Hathitrust
    package under the UFDC maw_work directory.

    This is usually called via multiprocess in the background to
    generate Hathitrust jp2 packages. It is developed to support a call from
    a save() or add method for new row to be added to model
    hathitrust_jp2_job.

    This process may require up to a second per bibvid jp2 page image to
    execute.
    So if a single bibvid has 500 pages, it can take 10 minutes.
    So small batches of 10 or fewer bib_vids are highly reommended until a
    regulator/feeder process/feature is implemented.

    Later: Also provide caller jp2_job_id as an argument, so
    this method can update the row for it along with misc status info.

    Consider: add sub_batch_size argument .. ?

    '''
    me = 'make_jp2_packages'
    jp2_total = 0
    print(f"{me}: Making jp2 packages for batch_set {obj.batch_set}")
    sys.stdout.flush()

    ufdc = maw_settings.HATHITRUST_UFDC
    # input dir
    resources = os.path.join(ufdc,'resources')
    # msg += line(f'INPUT dir={in_dir}')

    # make output dirs
    # out_dir_bib = os.path.join(resources,'maw_work','hathitrust',bib_vid)
    out_dir_batch = os.path.join(resources,'maw_work','hathitrust','batch',
        str(obj.id))
    os.makedirs(out_dir_batch, exist_ok=True)
    log_filename = os.path.join(out_dir_batch,'log.txt')

    print(f"{me}: Making jp2 packages for batch_set {obj.batch_set}"
        f" in {out_dir_batch}.")
    sys.stdout.flush()

    batch_items = BatchItem.objects.filter(batch_set=obj.batch_set_id)
    item_count = len(batch_items)
    with open(log_filename,'w') as log_file:
        print(f"{me}: Starting with jp2_job_set={obj.id}, "
          f"batch_set_id={obj.batch_set} "
          f"bibvid count={item_count} ",
          file=log_file)
        log_file.flush()
        item_count = len(batch_items)
        for count, batch_item in enumerate(batch_items, start=1):
            bib_vid = f"{batch_item.bibid}_{batch_item.vid}"
            #utc_now = datetime.datetime.utcnow()
            utc_now = timezone.now()
            str_now = secsz_start = utc_now.strftime("%Y-%m-%dT%H-%M-%SZ")
            msg = (
              f"Processed {jp2_total} images. Processing bibvid {bib_vid},"
              f" item {count} of {item_count} bibvids at {str_now}"
            )
            obj.jp2_images_processed = jp2_total
            obj.packages_created = item_count
            obj.status = msg
            obj.save()
            in_dir = resources + os.sep + resource_path_by_bib_vid(bib_vid)

            out_dir_bib = os.path.join(out_dir_batch, bib_vid)
            os.makedirs(out_dir_bib, exist_ok=True)

            jp2_count = make_jp2_package(in_dir=in_dir, out_dir_bib=out_dir_bib,
                bib=batch_item.bibid, vid=batch_item.vid, log_file=log_file)
            jp2_total += jp2_count
        # end for bach_item in batch_items
    # end with... log_file
    # By design, we MUST set status to non-Null, else will get into recursive
    # loop. #utc_now = datetime.datetime.utcnow()
    utc_now = timezone.now()
    str_now =  utc_now.strftime("%Y-%m-%d %H:%M:%SZ")
    obj.end_datetime = utc_now
    obj.jp2_images_processed = jp2_total
    obj.packages_created = item_count
    obj.status = (
      f"Finished:  {jp2_total} jp2 images in {item_count} packages in this batch {obj.id} "
      f"are complete at {str_now}. See bib_vid output folders under "
      f"{out_dir_batch}.")
    obj.save()

# end def make_jp2_packages()

class SubjectJob(models.Model):
    '''
    Each row represents a run of the Hathitrust jp2_job package generator,
    make_jp2_packages()

    Very simple relation that represents the running of a batch job to create
    HathiTrust packages for a set of bib_vids.

    The web user:
    (1) uses admin to add a row to table hathitrust_jp2_job ,
    (2) sets a batch_set id for the row, and
    (3) when the user save this row, the batch job to create Hathitrust packages
    for the bib_vid in the package is launched.
    To see that the batch job is completed, the user can either:
    (1) check the log file in the output folder for proof that
        the batch job is running or completed, assuming the user has permission
        to check the output folder
    (2) refresh the view of the jp2batch row to see if the status
        field is completed. It may be convenient for the user to save a
        memorable value in the notes field upon initial saving so it can be sought
        later to re-check the row.

    '''

    id = models.AutoField(primary_key=True)

    batch_set = models.ForeignKey(BatchSet,related_name="subject_app_batch_set", blank=False, null=False,
      db_index=True,
      help_text="BatchSet for which to generate SubjectApp JP2 Packages",
      on_delete=models.CASCADE,)

    thesaurus = SpaceTextField('Thesaurus',max_length=2550, null=True, default='',
      blank=True, help_text= (
        "Enter Value for Thesaurus"),
      editable=True,
      )
    create_datetime = models.DateTimeField('Run Start DateTime (UTC)',
        null=True, editable=False)

    #consider to populate user value later.. middleware seems best approach
    # https://stackoverflow.com/questions/862522/django-populate-user-id-when-saving-a-model
    user = models.ForeignKey(User,related_name="subject_app_user", on_delete=models.CASCADE,
      db_index=True, blank=True, null=True)

    packages_created = models.IntegerField(default=0, null=True,
      help_text='Number of bib_vid packages created by this job.')

    jp2_images_processed = models.IntegerField(default=0, null=True,
      help_text='Number of jp2 images packaged by this job.')

    '''
    jp2_images_per_minute = models.IntegerField(default=0, null=True,
      help_text='Approximate number of jp2 images packaged per minute so far '
          f'for this batch.')

    run_seconds = models.IntegerField(default=0, null=True,
      help_text='Approximate number of jp2 images packaged per minute so far '
          f'for this batch.')
    '''

    notes = SpaceTextField(max_length=2550, null=True, default='note',
      blank=True, help_text= ("General notes about this batch job run"),
      editable=True,
      )
    # Todo: batch job updates the end_datetime and status fields
    end_datetime = models.DateTimeField('End DateTime (UTC)',
        null=True,  editable=False)
    status = SpaceTextField('Run Status',max_length=2550, null=True, default='',
      blank=True, help_text= (
        "Status of ongoing or completed run. Check for status updates "
        "as packages are being built."),
      editable=True,
      )

    def save(self,*args,**kwargs):
        me = "SubjectJob.save()"

        super().save(*args, **kwargs)
        #if self.status is None or len(self.status) == 0:
        if self.status is None or len(self.status) == 0:
            # Only start this thread if status is not set
            # Note: we super-saved before this clause becaue
            # the thread uses/needs the autoassigne jp2batch.id value
            # Note: may prevent row deletions later to preserve history,
            # to support graphs of work history, etc.
            thread = threading.Thread(target=make_jp2_packages, args=(self,))
            thread.daemon = False
            #process.start()
            thread.start()
            print(f"{me}: started thread.")
            sys.stdout.flush()
            #utc_now = datetime.datetime.utcnow()
            utc_now = timezone.now()
            self.create_datetime = utc_now
            str_now = secsz_start = utc_now.strftime("%Y-%m-%dT%H-%M-%SZ")
            self.status = f"Started processing at {str_now}"
            # Save again so starting status appears immediately
            super().save(*args, **kwargs)

        # super().save(*args, **kwargs)
    # end def save()



class Thesaurus(models.Model):
    '''
    Creating a thesaurus table which references subjects tables

    '''

    id = models.AutoField(primary_key=True)

    subject_job_id = models.ForeignKey(SubjectJob,related_name="thesaurus_ref_id", blank=False, null=False,
      db_index=True,
      help_text="Subject ID refrenced from SubjectJob Table",
      on_delete=models.CASCADE,)

    name = SpaceTextField('Name',max_length=2550, null=True, default='',
      blank=True, help_text= (
        "Enter Name for Thesaurus"),
      editable=True,
      )



