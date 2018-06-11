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
class Cuba_LibroRouter:
    '''
    A router to control all db ops on models in the hathitrust Application.
    '''

    # app_label is really an app name. Here it is hathitrust.
    app_label = 'cuba_libro'

    # app_db is really a main settings.py DATABASES name, which is
    # more properly a 'connection' name
    app_db = 'cuba_libro_connection'

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

class Item(models.Model):

    # Field 'id' is 'special', and if not defined here, Django defines
    # it as I do below anyway.
    # However I do include it per python Zen:
    # explicit is better than implicit.
    id = models.AutoField(primary_key=True)

    # Many fields based on Jessica English UF email of 20180319
    # Jessica informed us that accession_number is or should be
    # unique to UF and all other cuba_libro partners.
    accession_number = models.CharField(max_length=255, unique=True,
        default="Enter accession number here", editable=True)

    # Add to these PARTNER_CHOICES as we learn of more partners.
    PARTNER_CHOICES = (
        ( 'UF' ,'University of Florida'),
        ( 'Available' ,'Available'),
        ( 'Harvard','Harvard'),
        ( 'NC State','North Carolina State University'),
    )

    agent = models.CharField('Partner', null=True, default='Available',
        blank=True, max_length=50, choices=PARTNER_CHOICES,
        help_text="Partner to verify or edit this item.")

    agent_modify_date = models.DateTimeField('Modify Date (UTC)',
        null=True, auto_now=True, editable=False)

    # Original source data for holding is of the form XXX[-NNN[-MMM]]
    # Later I may modify this model to separate them into: holder,
    # hold_count_low, hold_count_high values if needed.
    # If only NNN is given in imported input, then an import process will
    # set both hold_count_low and hold_count_high to NNN
    # If neither NNN nor MMM is given, set both to 0

    # import colum 0
    holding = models.CharField(null=True,max_length=20, default='',
        blank=True, editable=True)

    #reference type on imported files from UF and Harverd as of 20180320
    # seems to empirically comport with one of the values: [' Book, Whole', 'Journal Article', 'Map',
    #    'Web Page', 'Generic','Music Score', 'Book,Section']
    # New received from partners' import data may expand the list..

    # import column 1
    reference_type = models.CharField(null=True, default='',
        max_length=20, blank=True, editable=True)
    # import column 2
    authors_primary = models.TextField(null=True, default='',blank=True,
        editable=True)

    title_primary = models.TextField(null=True,
      default='', blank=True, editable=True)
    periodical_full = models.TextField(null=True,
      default='', blank=True, editable=True)

    # pub_year_span spreadsheet index = 5
    periodical_abbrev = models.TextField(null=True, default='', blank=True,
        editable=True)

    pub_year_span = models.CharField(null=True, max_length=50,default='2018',
        editable=True,)
    pub_date_free_from = models.TextField(null=True, default='', blank=True,
        editable=True)
    volume = models.CharField(null=True, max_length=30, default='', blank=True,
        editable=True)
    issue = models.CharField(null=True, max_length=30, default='', blank=True,
        editable=True)

    # index k =  10
    start_page = models.CharField(null=True, max_length=30, default='',
        blank=True, editable=True)
    other_pages = models.CharField(null=True, max_length=30, default='',
        blank=True, editable=True)
    keywords = models.TextField(null=True,  default='', blank=True,editable=True)
    abstract = models.TextField(null=True,  default='', blank=True,editable=True)
    personal_notes = SpaceTextField(null=True,  default='',
        blank=True,editable=True)

    authors_secondary = models.TextField(null=True,  default='',
        blank=True,editable=True)
    title_secondary = models.TextField(null=True,  default='',
        blank=True,editable=True)
    edition = models.TextField(null=True, default='',
        blank=True, editable=True)
    publisher = models.CharField(null=True, default='', max_length=255,
        blank=True, editable=True)
    place_of_publication = models.CharField(null=True, default='', max_length=255,
        blank=True, editable=True)

    #index 20
    authors_tertiary = models.TextField(null=True, default='',
        blank=True, editable=True)
    authors_quaternary = models.TextField(null=True, default='',
        blank=True, editable=True)
    authors_quinary = models.TextField(null=True, default='',
        blank=True, editable=True)
    titles_tertiary = models.TextField(null=True, default='',
        blank=True, editable=True)
    isbn_issn = models.CharField( "ISSN/ISBN",null=True, max_length=255,
        blank=True, editable=True)

    availability = models.TextField(null=True, default='',
        blank=True, editable=True)
    author_address = models.TextField( "Author/Address", null=True,default='' ,
        blank=True,editable=True)
    language = models.TextField(null=True, default='',
        blank=True,editable=True)
    classification = models.TextField(null=True, default='',
        blank=True,editable=True)

    #index=30
    original_foreign_title = models.TextField(null=True, default='',
        blank=True,editable=True)
    links = models.TextField(null=True, default='',
        blank=True,editable=True)
    url = models.TextField( 'URL',null=True, default='',
        blank=True,editable=True)
    doi = models.TextField( 'DOI',null=True, default='',
        blank=True,editable=True)
    pmid = models.TextField( 'PMID',null=True, default='',
        blank=True,editable=True)
    pmcid = models.TextField( 'PMCID',null=True, default='',
        blank=True,editable=True)

    call_number = models.TextField(null=True, default='',
        blank=True,editable=True)
    database = models.TextField(null=True, default='',
        blank=True,editable=True)
    data_source = models.TextField(null=True, default='',
        blank=True,editable=True)
    identifying_phrase = models.TextField(null=True, default='',
        blank=True,editable=True)
    retrieved_date = models.CharField(null=True, max_length=255,
        blank=True, editable=True)

    # index 40
    user_1 = models.TextField(null=True, default='', blank=True, editable=False)
    user_2 = models.TextField(null=True, default='', blank=True, editable=False)
    user_3 = models.TextField(null=True, default='', blank=True, editable=False)
    user_4 = models.TextField(null=True, default='', blank=True, editable=False)
    user_5 = models.TextField(null=True, default='', blank=True, editable=False)
    user_6 = models.TextField(null=True, default='', blank=True, editable=False)
    user_7 = models.TextField(null=True, default='', blank=True, editable=False)
    user_8 = models.TextField(null=True, default='', blank=True, editable=False)
    user_9 = models.TextField(null=True, default='', blank=True, editable=False)
    user_10 = models.TextField(null=True, default='', blank=True, editable=False)
    user_11 = models.TextField(null=True, default='', blank=True, editable=False)
    user_12 = models.TextField(null=True, default='', blank=True, editable=False)
    user_13 = models.TextField(null=True, default='', blank=True, editable=False)
    user_14 = models.TextField(null=True, default='', blank=True, editable=False)
    user_15 = models.TextField(null=True, default='', blank=True, editable=False)

    notes = SpaceTextField(null=True, default='',
        blank=True,editable=True)
    place_of_publication = models.CharField(null=True, max_length=255,
        blank=True, editable=True,)

    link_url = models.URLField( 'Link_URL', blank=True, null=True)
    edition_url = models.URLField( 'Edition_URL', blank=True, null=True)
    sub_file_database = models.CharField( "Sub file/database",
        blank=True, null=True, max_length=255, editable=True)

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

'''
Model Item_file will be a single file that a user uploads that will be
associated with a particular Hathitrust item.
So it will have a foreign key to a Hathitrust item.
'''
class Item_file(models.Model):
    #id is a default integer auto field, which is perfect, so let django make itself.
    item_id = models.ForeignKey('Item', on_delete=models.CASCADE,)

#end class Hathi_item
