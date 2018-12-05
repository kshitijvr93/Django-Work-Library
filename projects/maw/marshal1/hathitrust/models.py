import uuid
import os, sys
from django.db import models
from django.utils import timezone
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
import zlib
import gzip
import tarfile
#from os import listdir
from pathlib import Path
from natsort import natsorted
from shutil import copy2, make_archive, move
import hashlib

class HathiRouter:
    '''
    A router to control all db ops on models in the hathitrust Application.

    NOTE: rather than have a separate file router.py to host HathiRouter, I just
    put it here. Also see settings.py should include this dot-path
    as one of the listed strings in the list
    setting for DATABASE_ROUTERS.
    '''

    # app_label is really an app name. Here it is hathitrust.
    app_label = 'hathitrust'

    # app_db is really a main settings.py DATABASES name, which is
    # more properly a 'connection' name
    app_db = 'hathitrust_connection'

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
class Yaml(models.Model):
    # Relation to edit the 'meta.yaml' settings required by the
    # HathiTrust Cloud Packaging Service
    # Name "Meta" used by Django, so to re-use that name here is too
    # troublesome for quick code text searches.

    id = models.AutoField(primary_key=True)
    item = models.ForeignKey('Item', on_delete=models.CASCADE,
      db_index=True, blank=True, null=True)

    #Fields required for all materials
    bitonal_resolution_dpi = PositiveIntegerField(null=False,
      default=600,
      help_text="Required if images lack resolution information."
      "<a  href="
      "'https://drive.google.com/file/d/0B0EHs5JWGUMLWjU2OHVhQzN5WEk/view'"
      ">More</a>",
      )

    contone_resolution_dpi = PositiveIntegerField(null=False,
      default=600,
      help_text="Required if images lack resolution information."
      "<a  href="
      "'https://drive.google.com/file/d/0B0EHs5JWGUMLWjU2OHVhQzN5WEk/view'"
      ">More</a>",)

    # Maybe make  fieldset?
    image_compression_date = models.DateTimeField(
      db_index=True, blank=False,
      help_text="Required if images were compressed before "
      "Submittal Item Package was generated."
      "<a  href="
      "'https://drive.google.com/file/d/0B0EHs5JWGUMLWjU2OHVhQzN5WEk/view'"
      ">More</a>",
      )

    image_compression_agent = SpaceCharField(max_length=255,
      blank=True,
      help_text="Required if images were compressed before "
      "Submittal Item Package was generated. Eg, ImageMagick 6.7.8. "
      "<a  href="
      "'https://drive.google.com/file/d/0B0EHs5JWGUMLWjU2OHVhQzN5WEk/view'"
      ">More</a>",
      )

    #
    ORDER_CHOICES = (
        ( 'l2r' ,'left-to-right'),
        ( 'r2l' ,'right-to-left'),
    )
    scanning_order = SpaceCharField(max_length=255,
      choices=ORDER_CHOICES,
      default='l2r',
      help_text="Either left-to-right or right-to-left... "
      "<a  href="
      "'https://drive.google.com/file/d/0B0EHs5JWGUMLWjU2OHVhQzN5WEk/view'"
      ">More</a>",
      )

    reading_order = SpaceCharField(max_length=255,
      choices=ORDER_CHOICES,
      default='l2r',
      help_text="Example: use right-to-left ..."
      "<a  href="
      "'https://drive.google.com/file/d/0B0EHs5JWGUMLWjU2OHVhQzN5WEk/view'"
      ">More</a>",
      )

    def __str__(self):
        return self.item.bib_vid
class PrintScanYaml(models.Model):
    id = models.AutoField(primary_key=True)
    yaml = models.ForeignKey('Yaml', on_delete=models.CASCADE,
      db_index=True, blank=True, null=True)

    capture_datetime = models.DateTimeField(
      db_index=True, blank=False,
      help_text="Date and time of original print scan, estimate OK. "
        "<a  href="
        "'https://drive.google.com/file/d/0B0EHs5JWGUMLWjU2OHVhQzN5WEk/view'"
        ">More</a>",
      )

    scanner_make = SpaceCharField(max_length=255,
      blank = True,
      help_text="<a  href="
      "'https://drive.google.com/file/d/0B0EHs5JWGUMLWjU2OHVhQzN5WEk/view'"
      ">Help</a>",
      default='CopiBook')

    scanner_model = SpaceCharField(max_length=255,
      help_text="<a  href="
      "'https://drive.google.com/file/d/0B0EHs5JWGUMLWjU2OHVhQzN5WEk/view'"
      ">Help</a>",
      default='' )

    scanner_user = SpaceCharField(max_length=255,
      blank = True,
      help_text="<a  href="
        "'https://drive.google.com/file/d/0B0EHs5JWGUMLWjU2OHVhQzN5WEk/view'"
        ">Help</a>",
     default='UF Digtal Processing Services')

    def __str__(self):
        return self.yaml.item.bib_vid
class DigitalBornYaml(models.Model):

    id = models.AutoField(primary_key=True)
    yaml = models.ForeignKey('Yaml', on_delete=models.CASCADE,
      db_index=True, blank=True, null=True)

    creation_datetime = models.DateTimeField(db_index=True,
      blank=False,
      help_text="Required: Creation time of original file/item. "
        "Eg, PDF file's date. <a  href="
        "'https://drive.google.com/file/d/0B0EHs5JWGUMLWjU2OHVhQzN5WEk/view'"
        ">More</a>",
      )

    creation_agent = SpaceCharField(max_length=255,
        blank=False,
        help_text ='Required: HathiTrust organization code who created digital file.'
        "<a  href="
        "'https://drive.google.com/file/d/0B0EHs5JWGUMLWjU2OHVhQzN5WEk/view'"
        ">More</a>",
        )

    digital_content_provider = SpaceCharField(max_length=255,
        blank=True,
        help_text="Optional File-specific content provider's "
          "HathiTrust organization code. "
          "<a  href="
          "'https://drive.google.com/file/d/0B0EHs5JWGUMLWjU2OHVhQzN5WEk/view'"
          ">More</a>",
          )
    tiff_artist = SpaceCharField(max_length=255,
        blank=True,
        help_text="Required if images lack TIFF Artist or XMP "
          "tiff:Artist header. "
          "<a  href="
          "'https://drive.google.com/file/d/0B0EHs5JWGUMLWjU2OHVhQzN5WEk/view'"
          ">More</a>",
        )

    def __str__(self):
        return self.yaml.item.bib_vid
class Item(models.Model):

    # Field 'id' is 'special', and if not defined, Django defines
    # it as below.
    # However I do include it per python Zen: explicit is better than implicit.
    id = models.AutoField(primary_key=True)
    #
    uuid4 = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=255, unique=True,
        default='Hathitrust item name')
    modify_date = models.DateTimeField(auto_now=True)

    bib_vid = models.CharField(max_length=255,
        default = "AB12345678_12345",
        unique=True,
        help_text="Bib_vid in format XX12345678_12345" )

    # selected data is really created date of this row -- when this item is
    # selected from a UFDC resource bib item.
    #
    selected_date = models.DateTimeField(auto_now=True)

    # Date when this item was lack packaged into a zip
    packaged_date = models.DateTimeField(null=True)
    # md5 hash of the zip file itself
    zip_md5 = models.CharField(max_length=32,null=False, blank=True)

    # submission_date -- potential future: when we handle item submissions here
    # and/or when we track milestons in the HathiTrust submission process

    # md5 value of the zip file associated with this item.
    # Upon save, if no associated zip file exists, it is created.
    # Or if 1 does exist, but its current md5 does not match this
    # value, then the zip is recreated, zip_md5 is recalculated,
    # and resets this column value.
    # This helps minimize accidental HathiTrust package changes.
    # It is not user editable.
    #zip_md5 = models.CharField(max_length=255,
    #    default = "AB12345678_12345",
    #    unique=True,
    #    help_text="Bib_vid in format XX12345678_12345" )

    STATUS_CHOICES = (
        ( 'new' ,'new'),
        ( 'compiling','compiling'),
        ( 'packaged','package is valid to send'),
        ( 'sent','sent'),
        ( 'evaluated','evaluated'),
        ( 'recompiling','recompiling'),
        ( 'done','done')
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
        default='new')

    def __str__(self):
        return self.bib_vid

    ''' note: DO not set db_table. Let Django do its thing
        and create the db table name via a prefix of the table
        class of app_name and _. It makes
        migrations and many management operations much easier down the line.
        Changing it after doing some migrations will
        confuse migrations, too, which can be somewhat messy, or require
        a refresher review of migrations docs.

        class Meta:
          db_table = 'item'
    '''
class File(models.Model):
  """
  Each row in the model File describes a file and metadata for it to be
  served by the Django webserver.

  This is not populated manually, but rather via the upload method.

  When a user uploads a file, the upload method uploads it and adds
  a row in model File to indicate that the file is now uploaded onto
  the webserver and available for linking via ../file/file_id, where
  file_id is the id of the model File row.

  The upload process physically puts the uploaded file to a file named
  MEDIA_URL/file_id.ext, where .ext only appears where some extension
  ".xxx" is given by the user inthe uploaded filename.

  This assumes use of the usergroups application that requires a department
  owner for each row of the model.

  The file name is simply the id number, perhaps followed by the content-type
  suffix, and it is stored in the host filesystem in MEDIA_URL directory.

  The name_upload is the name used by the original uploader for the file,
  saved to support a method that will re-download the file to the original
  uploader so that this may be used as a backup.

  The content_type is the purported content type by the uploader, possibly
  to be validated. It is aka "mimetype", eg: "image/jpeg" or
  "application/pdf", etc.

  The sha5 hash is to uniquely identify the file contents.
  This is useful to support an application to identify duplicate files
  both within the Django site and among other hosts that may be
  over-duplicating files and wasting space or retaining files too long.
  """

  # department owner of the uploaded file
  department = models.CharField('Dept',max_length=64,default='RVP',db_index=True)
  public     = models.BooleanField('Public',default=False)

  #date_time the file row was added
  date_time = models.DateTimeField('datetime',auto_now=True,db_index=True)

  # Key words or topical info about the file contents, context
  # It is meant to be a django-admin-searchable field
  topic = models.CharField(max_length=128,db_index=True,blank=True,null=True)

  item = models.ForeignKey('Item', on_delete=models.CASCADE,
      db_index=True, blank=True, null=True)

  description = models.TextField(null=True,blank=True)

  #Create a subdirectory under media_root for the containing item of this file
  #

  # Argument upload_to must be a relative path under MEDIA_ROOT to an
  # existing directory that is writer by the user who launched the webserver.
  # This is the 'Django' path, so slashes are required regardless of OS.

  location = models.FileField(upload_to="hathitrust/")

  # NB: Must use hashlib module to make the hash re-calculable across
  # operating systems, future releases of python, etc.
  # sha512 is 512bits, hench 128 'hex chars' each representing 4 bits.
  sha512 = models.CharField(max_length=128, db_index=True,null=True,blank=True)

  up_name = models.CharField('up_name',max_length=128,default='tmpfile');

  down_name= models.CharField('down_name',max_length=128,default='tmpfile',
      null=True,blank=True);

  link_name= models.CharField('link_name',max_length=128,default='click here',
      null=True,blank=True);

  # size of file in 8-bit bytes
  size = models.IntegerField(default=0)

  # uploadedfile objects - mirrored django1.1 attributes.
  content_type = models.CharField('content_type',max_length=128,
      default='text/plain')

  #charset applies to 'text/*' content types.
  charset = models.CharField('char_set',max_length=32,null=True,blank=True)

  # Url is the reference url to use to download the file
  url = models.CharField('url',max_length=256,default='tmpfile');

  def __str__(self):
        #2018
        return "File"
class UploadFile(models.Model):
  '''
  Legacy UploadFile object designed for more uses than is the leaner File
  model used by the Hathitrust app.

  If later will register with admin ... remember it has its own uploadform,
  so do not enable the Add permissions via admin, but admin views are OK.
  Can use the upload() method in views.py to invoke this if wanted.
  '''

  # department owner of the uploaded file
  department = models.CharField('Dept', max_length=64, default='RVP',
      db_index=True)
  public     = models.BooleanField('Public', default=False)

  #date_time the file row was added
  date_time = models.DateTimeField('datetime',auto_now=True,db_index=True)

  # Key words or topical info about the file contents, context
  # It is meant to be a django-admin-searchable field
  topic = models.CharField(max_length=128,db_index=True,blank=True,null=True)

  item = models.ForeignKey('Item', on_delete=models.CASCADE,
      db_index=True, blank=True, null=True)

  description = models.TextField(null=True,blank=True)

  # If you to change upload_to, make sure it is a writeable directory
  location = models.FileField(upload_to="hathitrust/")

  # NB: Must use hashlib module to make the hash re-calculable across
  # operating systems, future releases of python, etc.
  # sha512 is 512bits, hench 128 'hex chars' each representing 4 bits.
  sha512 = models.CharField(max_length=128, db_index=True,null=True,blank=True)

  up_name = models.CharField('up_name',max_length=128,default='tmpfile');

  down_name= models.CharField('down_name',max_length=128,default='tmpfile',
      null=True,blank=True);

  link_name= models.CharField('link_name',max_length=128,default='click here',
      null=True,blank=True);

  # size of file in 8-bit bytes
  size = models.IntegerField(default=0)

  # uploadedfile objects - mirrored django1.1 attributes.
  content_type = models.CharField('content_type',max_length=128,
      default='text/plain')

  #charset applies to 'text/*' content types.
  charset = models.CharField('char_set',max_length=32,null=True,blank=True)

  # Url is the reference url to use to download the file
  url = models.CharField('url',max_length=256,default='tmpfile');

  def __str__(self):
        #2018
        return "UploadFile"
def resource_sub_path_by_bib_vid(bib_vid=None):
    '''
    return sub_path without leading / for a bib_vid folder under the
    resources directory:

    Note: recent finding is that some 'old' bibs have no vid, so may need to
    tweak this if users want to use thos old bibs at some point.
    Also: other new or non-UF bibs in the future may have a variable number of
    leading characters or total length.
    '''
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
def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
#def modification_utc_str_by_filename(filename):
def ltime_tzone_utime_by_filename(filename):
    # given a named file, return tuple of:
    # [0] str of local time of modification
    # [1] timezone in full hour count, of that local time
    # note: some non-full-hour timezones will be not accurate to the minute.
    # [2] utc string of the modification time
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
            msg += '\n' + (f'Processing {n_paths} files with extension {ext}.')

            # Sort the paths for this glob
            sorted_paths = natsorted(paths)
            #Copy each file to one with the HathiTrust-preferred name
            for i, in_path in enumerate(sorted_paths, 1):
                in_name = str(in_path)
                jp2_count += 1

                if verbosity > 1:
                  msg += '\n' + (
                      f'{me}: processing file {i} PACKAGE FOR '
                      f'bib_vid {bib_vid}.')
                print(msg, file=log_file)
                log_file.flush()

                if i == 1:
                    #dstr, tz, utcstr = modification_utc_str_by_filename(in_path)
                    dstr, tz, utcstr = ltime_zone_utime_by_filename(in_path)
                    # str_tz : Lop of the 'seconds' part of the tz
                    str_tz = str(tz)
                    index_last_colon = str_tz.rfind(':')
                    if index_last_colon > 0:
                        str_tz = str_tz[0:index_last_colon]

                    capture_date = f'{dstr}-{str_tz}'
                    if verbosity > 1:
                      msg += (f'\nGot dstr={dstr}\n')
                      msg += (f'\nGot tz={tz}\n')
                      msg += (f'\nGot utcstr={utcstr}\n')
                      msg += (f'\nGot capture_date={capture_date}\n')

                out_base = str(i).zfill(8)
                out_base_ext = out_base + ext
                out_name = out_dir_files + os.sep + out_base_ext

                in_base = in_name.split('.')[0]

                copy2(in_name, out_name)

                # Write checksum.md5 file line for this file in  package
                md5sum = md5(in_name)
                msg += ( f"\n{i}: {in_name} md5sum='{md5sum}'")
                out_file_md5.write(f'\n{md5sum} {out_base_ext}\n')

                #for ext_t in ['.pro','.txt']:
                # Copy txt files only now
                text_files_found = True
                for ext_t in ['.txt',]:
                    # seek similar file name ending .txt
                    try:
                        in_name = in_base + ext_t
                        out_base_ext = out_base + ext_t
                        out_name = out_dir_files + os.sep + out_base_ext
                        copy2(in_name, out_name)

                        # Write checksum.md5 file line for this package file.
                        md5sum = md5(in_name)
                        if verbosity > 1:
                          msg += (f"\n{i}: {in_name} md5sum='{md5sum}'")
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
        msg +=  f"\nYAML FILE: {yaml_file_name} md5sum='{md5sum}'"
        out_file_md5.write(f'{md5sum} {yaml_base_name}\n')
    #with open --- checksum.md5 as out_file_md5

    # TODO:move the checksum.md5 file from the bib dir to the files dir
    out_renamed_md5 = out_dir_files + os.sep + 'checksum.md5'
    move(out_name_md5, out_renamed_md5)

    # Create zip archive
    out_base_archive_file = out_dir_bib + os.sep +  bib_vid
    make_archive(out_base_archive_file, 'zip', out_dir_files)
    msg += (f'\nMade archive file {out_base_archive_file}.zip for '
                 f'directory {out_dir_files}')
    msg += (f'\n{me}: Finished package FOR bib_vid {bib_vid}.\n')

    print(msg, file=log_file)
    log_file.flush()
    return jp2_count

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
            in_dir = resources + os.sep + resource_sub_path_by_bib_vid(bib_vid)

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
      f"Finished:  {jp2_total} jp2 images in {item_count} packages in this"
      f" batch {obj.id} are complete at {str_now}. "
      f"See bib_vid output folders under {out_dir_batch}." )
    obj.save()
class Jp2Job(models.Model):
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
        memorable value in the notes field upon initial saving so it can be
        sought later to re-check the row.

    '''

    id = models.AutoField(primary_key=True)

    batch_set = models.ForeignKey(BatchSet, blank=False, null=False,
      db_index=True,
      help_text="BatchSet to input to generate Hathitrust JP2 Packages",
      on_delete=models.CASCADE,)


    create_datetime = models.DateTimeField('Run Start DateTime (UTC)',
        null=True, editable=False)

    #consider to populate user value later.. middleware seems best approach
    # https://stackoverflow.com/questions/862522/django-populate-user-id-when-saving-a-model
    user = models.ForeignKey(User, on_delete=models.CASCADE,
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
        me = "jp2_job.save()"

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


class Jp2Job2(models.Model):
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

    batch_set = models.ForeignKey(BatchSet, blank=False, null=False,
      db_index=True,
      help_text="BatchSet for which to generate Hathitrust JP2 Packages",
      on_delete=models.CASCADE,)


    create_datetime = models.DateTimeField('Run Start DateTime (UTC)',
        null=True, editable=False)

    #consider to populate user value later.. middleware seems best approach
    # https://stackoverflow.com/questions/862522/django-populate-user-id-when-saving-a-model
    user = models.ForeignKey(User, on_delete=models.CASCADE,
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
        me = "jp2_job.save()"

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




    class Meta:
        verbose_name_plural='Jp2Jobs'
def make_items_zip(obj, verbosity=1):
    '''
    Given a batch_set_id fkey into db table dps_batch_set,
    for each the batchset of items,  generate a tar file of of those complete
    items.

    This is usually called via thread in the background.

    It is developed to support a call from
    a save() or add method for new row to be added to model
    hathitrust_items_zip.

    '''
    me = 'make_items_zip'
    if verbosity > 0:
      print(f"{me}: Making items zip file for batch_set {obj.batch_set}")
      sys.stdout.flush()

    ufdc = maw_settings.HATHITRUST_UFDC
    # input dir
    resources = os.path.join(ufdc,'resources')

    # make output dirs
    # out_dir_bib = os.path.join(resources,'maw_work','hathitrust',bib_vid)
    out_dir_zip = os.path.join(resources,
        'maw_work','itemszip', f'job_{str(obj.id)}',)

    os.makedirs(out_dir_zip, exist_ok=True)
    log_filename = os.path.join(out_dir_zip,'log.txt')

    # Recommendation: This tar file is to be untarred within a parent folder
    # with last directory named 'resources', to help minimize confusion and
    # maintain a conceptual relation to the required source input folder
    tar_filename = os.path.join(out_dir_zip,'resource_items.tar')

    print(f"{me}: Making zip file for batch_set {obj.batch_set}"
        f" in {out_dir_zip}.")
    sys.stdout.flush()

    batch_items = BatchItem.objects.filter(batch_set=obj.batch_set_id)
    item_count = len(batch_items)
    files_total = 0
    # create and write to tarfile...
    #import tarfile
    with (
        open(log_filename,'w')) as log_file, (
        tarfile.open(name=tar_filename, mode='w')) as tarfile_out:

        # tar.add(name)
        if verbosity > 0:
          print(f"{me}: Starting with ItemsZip id={obj.id}, "
            f"batch_set_id={obj.batch_set} "
            f"Items(bibvid) count={item_count} ",
            file=log_file)
          log_file.flush()

        items_count = len(batch_items)
        for item_count, batch_item in enumerate(batch_items, start=1):
            bib_vid = f"{batch_item.bibid}_{batch_item.vid}"
            #utc_now = datetime.datetime.utcnow()
            utc_now = timezone.now()
            str_now = secsz_start = utc_now.strftime("%Y-%m-%dT%H-%M-%SZ")
            msg = (
              f"Archived {files_total} files. Archiving bibvid {bib_vid},"
              f" item {item_count} of {items_count} bibvids at {str_now}"
            )

            # UPDATE batchset values at the time of processing
            # this bib_vid
            obj.file_count = files_total
            obj.items_count = item_count
            obj.status = msg
            obj.save()

            resource_sub_path = resource_sub_path_by_bib_vid(bib_vid)
            input_dir = resources + os.sep + resource_sub_path

            msg = f'{me}: Tarring files for bib_bid {bib_vid}...'
            if verbosity > 0:
                print(msg, file=log_file)
                log_file.flush()

            file_count = 0
            try:
                for path in list(Path(input_dir).glob(obj.glob)):
                    file_count += 1
                    input_file_name = input_dir + os.sep + path.name
                    archive_name = ( resource_sub_path + os.sep
                      + path.name )
                    msg = (f'Tarring input file name={input_file_name} '
                      f'to {archive_name}')
                    print(msg, file=sys.stdout)
                    print(msg, file=log_file)
                    log_file.flush()
                    tarfile_out.add(input_file_name, archive_name)
                # end for file in in_dir
            except Exception as ex:
                # Possible glob syntax error, maybe others?
                # todo: Create Django user message later..
                print(f'***** exception={repr(ex)}',file=sys.stdout)

                raise ValueError(f'Exception={repr(ex)}')

            files_total += file_count
        # end for bach_item in batch_items
    # end with open log_file, tarfile_out

    # Here, now all bibvid items have been visited and files added to tar_file
    # TODO: simply make a zip file from the tar file and delete the tar_file

    # By design, we MUST set status to non-Null, else will get into recursive
    # loop. #utc_now = datetime.datetime.utcnow()
    utc_now = timezone.now()
    str_now =  utc_now.strftime("%Y-%m-%d %H:%M:%SZ")
    obj.end_datetime = utc_now
    obj.item_count = item_count
    obj.status = (
      f"Finished:  {files_total} files in {item_count} bib_vids in "
      f"this batch {obj.id} "
      f"are complete at {str_now}. See output folder "
      f"{out_dir_zip}.")
    obj.save()
class ItemsZip(models.Model):
    '''
    Each row represents a run of the Items file zip generator,
    make_items_zip().

    Very simple relation that represents the running of a batch job to create
    A zipped package of items (from UFDC resources) suitable for unzipping into
    a destination resources key-pair folder hierarchy.

    The web user:
    (1) uses admin to add a row to table hathitrust_job_zip,
    (2) sets a batch_set id for the row, and
    (3) when the user saves this row, the batch job to create zip file
    for the resource items in the batch is launched.
    To see that the batch job is completed, the user can either:
    (1) check the log file in the output folder for proof that
        the batch job is running or completed, assuming the user has permission
        to check the output folder
    (2) refresh the view of the hathitrust_job_zip row to see if the status
        field reports it is finished. It may be convenient for users to save a
        memorable value in the notes field upon initial saving so it can be
        sought later to re-check the row.

    '''

    id = models.AutoField(primary_key=True)

    batch_set = models.ForeignKey(BatchSet, blank=False, null=False,
      db_index=True,
      help_text="BatchSet for which to generate a zip file of resource items",
      on_delete=models.CASCADE,)

    glob = SpaceCharField(max_length=255,
      help_text= "Glob file selector (Eg, *.* or *.jp2 or *.mets.xml, etc)",
      default='*.mets.xml' )


    create_datetime = models.DateTimeField('Run Start DateTime (UTC)',
        null=True, editable=False)

    #consider to populate user value later.. middleware seems best approach
    # https://stackoverflow.com/questions/862522/django-populate-user-id-when-saving-a-model
    user = models.ForeignKey(User, on_delete=models.CASCADE,
      db_index=True, blank=True, null=True)

    item_count = models.IntegerField(default=0, null=True,
      help_text='Number of bib_vid items zipped by this job.')

    file_count = models.IntegerField(default=0, null=True,
      help_text='Total number of files zipped by this job.')

    uncompressed_bytes = models.IntegerField(default=0, null=True, help_text=
      'Total number of uncompressed bytes encodded in this zip file.')

    compressed_bytes = models.IntegerField(default=0, null=True, help_text=
      'Total number of compressed bytes encodded in this zip file.')

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
        me = "ItemsZip.save()"

        super().save(*args, **kwargs)
        # if self.status is None or len(self.status) == 0:
        if self.status is None or len(self.status) == 0:
            # Only start this thread if status is not set
            # Note: we super-saved before this clause becaue
            # the thread uses/needs the autoassigne jp2batch.id value
            # Note: may prevent row deletions later to preserve history,
            # to support graphs of work history, etc.
            thread = threading.Thread(target=make_items_zip, args=(self,))
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
