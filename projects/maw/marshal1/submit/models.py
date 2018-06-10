from django.db import models
import uuid
#from django_enumfield import enum

#other useful model imports at times (see django docs, tutorials):
import datetime
from django.utils import timezone
from maw_utils import SpaceTextField, SpaceCharField, PositiveIntegerField
import django.contrib.postgres.fields as pgfields
from collections import OrderedDict
from django.core.serializers.json import DjangoJSONEncoder
#import maw_utils

'''
NOTE: rather than have a separate file router.py to host HathiRouter, I just
put it here. Also see settings.py should include this python import dot-path
as one of the listed strings in the list setting for DATABASE_ROUTERS.

'''
# Maybe move the HathiRouter later, but for now keep here
#
class SubmitRouter:
    '''
    A router to control all db ops on models in the hathitrust Application.
    '''

    # app_label is really an app name. Here it is hathitrust.
    app_label = 'submit'

    # app_db is really a main settings.py DATABASES name, which is
    # more properly a 'connection' name
    app_db = 'submit_connection'

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

# } end class SubmitRouter

class TypeModel(models.Model):
    id = models.AutoField(primary_key=True)
    name = SpaceCharField(max_length=255,
        unique=True, blank=False, null=False, default='',
        help_text="Unique name for this type.", editable=True)
    text = SpaceTextField(blank=False, null=False,
        default="Your text here.",
        help_text="Text for this type." )

    def __str__(self):
            return '{}'.format(self.name)

class MaterialType(TypeModel):
    pass
class ResourceType(TypeModel):
    pass
class LicenseType(TypeModel):
    pass
class NoteType(TypeModel):
    pass
class Affiliation(TypeModel):
    pass
class MetadataType(TypeModel):
    pass

# { start class Author}
class Author(models.Model):
    id = models.AutoField(primary_key=True)

    orcid = SpaceCharField(max_length=80,null=True, default='',
        blank=True,editable=True,
        help_text="Orcid ID for this author"
        )

    email_address = models.EmailField()

    surname = SpaceCharField( help_text="Also known as last name or family name",
      blank=False, null=False, default='',
      max_length=255, editable=True)

    given_name = SpaceCharField(
      help_text="Also known as first name. Please provide at least an initial.",
      blank=False, null=False, max_length=255, editable=True)

    create_datetime = models.DateTimeField(help_text='Author Insertion DateTime',
        null=True, auto_now=True, editable=False)

    ufdc_user_info = SpaceTextField(max_length=255,null=True, default='',
        blank=True, editable=True,help_text='UFDC user id info')

    def __str__(self):
        return '{}, {} with Orcid:{}'.format(
             self.surname, self.given_name, repr(self.orcid) )

# } end class Author


# { start class Submittal
class Submittal(models.Model):
    # Field 'id' is 'special', and if not defined here, Django defines
    # it as I do below anyway.
    # However I do include it per python Zen:
    # explicit is better than implicit.
    id = models.AutoField(primary_key=True)

    # See relation SubmittalAuthor for authorship, author ordering,
    # copyright license info for this submittal

    title_primary = SpaceTextField(max_length=255,
      default='', blank=False, null=False, editable=True,
      help_text="Title of the item you are submitting")

    submittal_datetime = models.DateTimeField(help_text='Submittal DateTime',
        null=False, auto_now=True, editable=False)

    license_type = models.ForeignKey('LicenseType', null=True,
        default=None,
        on_delete=models.CASCADE,)

    material_type = models.ForeignKey('MaterialType',
        on_delete=models.CASCADE,)

    resource_type = models.ForeignKey('ResourceType',
        on_delete=models.CASCADE,)
    # This will be automatically assigned in production
    bibid = SpaceCharField(max_length=255,  editable=True, blank=True, null=True,
        default=None,
        help_text = "This will be automatically assigned in production"
        )
    publisher = SpaceCharField(max_length=255, editable=True, blank=True,
        help_text = "This will be automatically assigned in production"
        )
    publication_date = models.DateField(blank=True, null=True,
      help_text='Date of publication.'
      )
    abstract = SpaceTextField(max_length=255,
      blank=False, null=False, default='',
      help_text='Abstract or summary of the content'
      )

    language = SpaceCharField(max_length=255,null=True, default='',blank=True,
      editable=True,
      help_text="The actual language.")

    def __str__(self):
        return str(self.title_primary)

    ''' WARNING FOR POSTERITY:
        Do -not- set db_table. Let Django do its thing
        and create the db table name via a prefix of the table
        class of AppConfig.name (see apps.py) and _.

        It makes future migrations and many management operations much easier
        down the line.

        Changing it after doing some migrations will
        confuse migrations, too, which can be very messy, and probably require
        substantial time for a refresher course in Django migrations.

        class Meta:
          db_table = 'item'
    '''
# } end class Submittal


#{ start class Note
class Note(models.Model):
    id = models.AutoField(primary_key=True)

    submittal = models.ForeignKey('Submittal', on_delete=models.CASCADE,
        null=True,
        help_text='Id of Submittal authored by this author', )

    note_type = models.ForeignKey('NoteType',
        on_delete=models.CASCADE,)

    note = SpaceTextField(max_length=255,null=True, default='',blank=True,
      editable=True,
      help_text="Your actual note text.")

    def __str__(self):
        return '{}'.format(self.note)

# } end class Note


# { Start class SubmittalAuthor}
class SubmittalAuthor(models.Model):
    id = models.AutoField(primary_key=True)

    submittal = models.ForeignKey('Submittal', on_delete=models.CASCADE,
        null=True,
        help_text='Submittal authored by this author', )

    author = models.ForeignKey('Author', on_delete=models.CASCADE,
        help_text='Author of the associated submittal', )

    affiliation = models.ForeignKey('Affiliation', on_delete=models.CASCADE,
        help_text='Affiliation of the author at time of initial publication', )

    rank = PositiveIntegerField(blank=False, null=False, default=1,
      help_text='Primary author should have rank 1. '
        'This defines the order of author names in a citation.', )

    def __str__(self):
        return '{} {}'.format(self.author.given_name, self.author.surname)

    #Note we should add a 3-term composite unique index to submittal, author,
    #rank. We do NOT check for gaps in citation rank
    # May add affiliatin id here too.. to indicate the author's
    # institutional affiliation(s) to record for this submittal
    class Meta:
        unique_together = (('submittal', 'author', 'rank'),)
        pass
        # ordering = [ 'sensor_type', ]

# } end class SubmittalAuthor

'''
App submit - class File
This is an uploaded file.
It can be referenced by a submittal via a submittalfile
object.
'''

class File(models.Model):
    id = models.AutoField(primary_key=True)

    upload_datetime = models.DateTimeField(
       help_text='Original file upload dateTime',
        null=True, auto_now=True, editable=False)

    keywords = models.CharField(max_length=255,db_index=True,blank=True
        ,null=True)

    description = SpaceTextField(blank=False, null=False,
        default="Your description here.",
        help_text="Description for this file." )

    def __str__(self):
        return '{}'.format(str(self.keywords))

# end class File

def content_file_name(instance, filename):
    return '/'.joint(['submit_files', filename])


'''
Todo: May also try different directory structure, eg:
yyyy/mm/dd/sub_id/file_id to store each file...
Where the yyyymmdd is the creation date of the submittal,
sub_id is the submital id and file_id is the file_id
But a plain id number as a file name in a simple single directory
may be best.. or maybe per a (submitall) year string sub directory
for 2 levels.

'''

def upload_location(instance, filename):
    sub_dt = instance.submittal.submittal_datetime
    date_string = instance.upload_datetime.strftime('%Y/%m/%d/')
    sid = instance.submittal.id
    zid = str(instance.id).zfill(10)
    return ('submit/{}/{}/{}'.format(date_string,sid,zid))

'''
Upload instances are uploaded files with (1) a parent submittal,
and other fields to help manage uploads such as a download name per file,
a hash to avoid collisions, a content type.
'''
class Upload(models.Model):
    id = models.AutoField(primary_key=True)

    submittal = models.ForeignKey('Submittal', on_delete=models.CASCADE,
        blank=False, null=False, default='',
        help_text='Submittal authored by this author', )

    upload_datetime = models.DateTimeField(
       help_text='Original file upload dateTime',
        null=True, auto_now=True, editable=False)


    download_name = SpaceCharField(max_length=255,blank=True, null=True,
        help_text="Downlad Name for of this file." )

    description = SpaceTextField(blank=True, null=True,
        help_text="Optional Description of this file." )

    location = models.FileField(upload_to=upload_location)

    # murmur3  - insert field to hold murmur3 hash here.

    def __str__(self):
        return '{}:{}'.format(str(self.id), str(self.location))

# { Start class submittal author}
class SubmittalFile(models.Model):
    id = models.AutoField(primary_key=True)

    submittal = models.ForeignKey('Submittal', on_delete=models.CASCADE,
        null=False, default='',
        help_text='Submittal authored by this author', )

    file = models.ForeignKey('File', on_delete=models.CASCADE,
        null=False, default='',
        help_text='Component file of the associated submittal', )

    download_name = SpaceCharField(max_length=255,
        help_text="Name to use for this file as part of this submittal",
        default='',
        unique=True,
        blank=False, null=False, editable=True)
    rank = PositiveIntegerField(blank=False, null=False, default=1,
        help_text='Rank order of this file within the set of '
         'component files of this submittal')

    def __str__(self):
        return '{}'.format(self.id)

    # Limit choices of files to ones already explicitly uploaded
    # to this submittal (rather than allow choice from all files).
    # This limits plagiarism a bit and makes choices simpler for the user.
    # Consider: It may be simpler to have no choices, as users should
    # add a new file each time, actually...
    # reconsider: maybe just put a submittal field back into the File model
    # and not allow choices as I do for authors...

    #also see: https://stackoverflow.com/questions/21337142/django-admin-inlines-get-object-from-formfield-for-foreignkey#28270041
    def zzformfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request,**kwargs)
        # 'change' is at -1, and id is at -2...
        obj_id = request.META['PATH_INFO'].rstrip('/').split('/')[-2]
        print("GOT OBJ_ID={}".format(repr(obj_id)))
        # see also: https://stackoverflow.com/questions/32150088/django-access-the-parent-instance-from-the-inline-model-admin
        field_name = db_field.name
        print("ff_f_ff:Got field_name='{}'".format(field_name))
        if db_field.name =='file':
            obj = self.get_object(request, obj_id)
            if obj:
                kwargs['queryset'] = File.objects.filter(submittal=obj )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    #Note we should add a 3-term composite unique index to submittal, author,
    #rank. We do NOT check for gaps in citation rank
    # May add affiliatin id here too.. to indicate the author's
    # institutional affiliation(s) to record for this submittal
    class Meta:
        unique_together = (('submittal', 'file', 'rank'),)
        pass
        # ordering = [ 'sensor_type', ]
#end class SubmittalFile


'''
See https://fairuse.stanford.edu/overview/faqs/copyright-ownership/
May advise submitter to only submit items of which they are an author
and have not assigned-away their copyright to a publisher or another.

Also advise submitter to only submit items the whole of which they are
authors. For example, if they wrote only a chapter of a book, they are advised
to submit only the chapter, as they only have a right to issue a copyright
license for that chapter, not the whole book.

Also, advise them that they should list joint authors of the submittal, or
copyright assignees if they can, as they also may have active rights of
copyright and of credit for the work.

Also, ask the author(s) for assignment of the copyright to UF or even a
special license of their own design or agree to one from a multiple choice
list we provide, so that UF may copy, redistribute, etc.

Copyright law provides for any author to change the licensing statement(s)
over time, and even offer different licensing to different individuals or
segments of the public, etc.

So we may want to keep track of historical copyright licenses by date issued.
Also if there are multiple authors, multiple copyright licenses (at least one per
author per time span are possible.)

We should inform all authors for whom we have email addresses that their work
is provided in our repository and that they have the right to register their own
copyright license for the work at any time.
Each work should list assignees of copyrights, not just the author.
If the author assigns copyright to any other, we should record it and the contact
info so the public may ask permission of the assignee if wanted.

'''

# If an author assigns copyright to another, UF may want to provide that
# assignee an interface to add new licenses.
#

# { class Licensor
# A lcensor is assumed to be valie and could be an author or
# another who was assigned or authorized by author to grant licenses.
# UF does no validation of thelegal standing of the indicated Licensor,
# so user must beware of validity of listed licensor to grant licenes.
#class Licensor(models.Model):
    # id
    # submittal
    # licensor
    # assignor -- source SubmittalLicensor that added this row, and
    # value is either Null (if original author) or a Licensor of the
    # same submittal id (2-part composite key on submittal and licensor
    # that refers to another row in this table) active at the create_datetime
    # of this
    # row
    # if the assignment also rescinded author rights, the end_datetime is
    # populated, meaning that licensor not valid after that end_datetime.
    # None if this assignee is one of the original authors...
    #
    # start_datetime - dateime this Licensor was assigned
    #
    # author_rank - for referencing, crediting..
#End class
