import uuid
import os
from django.db import models
#from django_enumfield import enum

#other useful model imports at times (see django docs, tutorials):
import datetime
from django.utils import timezone
from maw_utils import SpaceTextField, SpaceCharField, PositiveIntegerField

'''
NOTE: rather than have a separate file router.py to host HathiRouter, I just
put it here. Also see settings.py should include this dot-path
as one of the listed strings in the list
setting for DATABASE_ROUTERS.

'''
# Maybe move the HathiRouter later, but for now keep here
#
class HathiRouter:
    '''
    A router to control all db ops on models in the hathitrust Application.
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


# end class DigitalBornYaml


# end class Meta
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

#end class Item(models.Model)

#end class Item

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

# end class File

'''
Legacy UploadFile object designed for more uses than is the leaner File model
used by the Hathitrust app.

If later will register with admin ... remember it has its own uploadform,
so do not enable the Add permissions via admin, but admin views are OK.
Can use the upload() method in views.py to invoke this if wanted.
'''

class UploadFile(models.Model):

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

# end class UploadFile
