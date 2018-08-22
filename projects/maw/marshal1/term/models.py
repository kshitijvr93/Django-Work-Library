import uuid
from django.db import models
#from django_enumfield import enum

#other useful model imports at times (see django docs, tutorials):
import datetime
from django.utils import timezone
from maw_utils import SpaceTextField, SpaceCharField, PositiveIntegerField

'''
NOTE: rather than have a separate file router.py to host HathiRouter, I just
put it here. Also see settings.py should include this python import dot-path
as one of the listed strings in the list setting for DATABASE_ROUTERS.

'''
# Maybe move the HathiRouter later, but for now keep here
#
class TermRouter:
    '''
    A router to control all db ops on models in this Application. See apps.py.
    '''

    # app_label is really an app name. Here it is hathitrust.
    app_label = 'term'

    # app_db is really a main settings.py DATABASES name, which is
    # more properly a 'connection' name
    app_db = 'default'

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
    class Meta:
        abstract = True

# NB: we accept the django default of prefixing each real
# db table name with the app_name.

class Resource(TypeModel):
    #todo: go ahead and descend the resources directory and do not add
    #a row to this table unless the named bibvid (AA12345678_00001) exists.
    #
    pass

class Thesaurus(TypeModel):
    pass

class Retrieval(models.Model):
    id = models.AutoField(primary_key=True)
    retrieval_datetime = models.DateTimeField('Retrieval DateTime (UTC)',
        null=False, auto_now=True, editable=False)

    # thesaurus name known to Access Innovations:
    # eg, 'floridathes', 'geofloridathes'
    thesaurus = models.ForeignKey('Thesaurus', null=False, on_delete=models.CASCADE)
    bibvid = models.ForeignKey('Bibvid', null=False, on_delete=models.CASCADE)

    # Note: when saving a retrieval row: (1) the bibvid is analyzed and
    # (2) an API GetSuggestedTerms request is sent to AI and
    # (3) a row in relation apiterm is added for each api-returned term
    # (4) a note is made here about how processing of the bibvid to produce
    # the document that was sent with the AI API GetSuggestedTerm request
    # future;
    #
    # (*) also value count_pages might be autopopulated..
    # (*) also note may be populated with a desc of the logic of the retrieval
    # formulation (just jp2, just txt files used, maybe count of files etc)
    # (*) also the mets file is parsed if any, and metsterm rows are populated

    note = SpaceTextField(max_length=255, null=True, default='', blank=True,
      editable=True,
    # Some value to consider adding here:
    # N  of pages, N of files of various types
    # time sent/received of api request/response
    # N of apiterms received
    #type of stratagy to produce text, eg if ocr even the tesseract or other
    #sofware version
    #Size in bytes of text document
    #Maybe allow stats per page sent, or one main retrieval for all text,
    #and a retrieval for each individual page... etc.. and on and on
    pass

class Apiterm(models.Model):
    retrieval = models.ForeignKey('Retrieval', null=False,
        on_delete=models.CASCADE,
        help_text="API Retrieval which generated this api term."
        )
    # Many fields based on Jessica English UF email of 20180319
    # Jessica informed us that accession_number is or should beUniversity of North Carolina at Chapel Hill
    # unique to UF and all other cuba_libro partners.

    name = models.SpaceCharField(max_length=255, unique=True,
        default="Term name", editable=True)

    # A user edits this field to record the decision whether to insert the
    # term as a subject into the item's mets file
    accepted_status = models.SpaceCharField('Status',
        blank=True, default='', null=False,
        max_length=50,
        help_text="Status of acceptance decision."

    def __str__(self):
        return str(self.id)

    ''' note: Do -not- set db_table. Let Django do its thing
        and create the db table name via a prefix of the table
        class of app_name and _.
        It makes future
        migrations and many management operations much easier down the line.
        Changing it after doing some migrations will
        confuse migrations, too, which can be somewhat messy, or require
        a refresher review of migrations docs.

        class Meta:
          db_table = 'item'
    '''

#end class Term
