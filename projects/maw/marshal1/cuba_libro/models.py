import uuid
from django.db import models
#from django_enumfield import enum
from django.contrib.auth import get_user_model
User = get_user_model()
#from django.contrib.auth.models import User

#other useful model imports at times (see django docs, tutorials):
import datetime
from django.utils import timezone
from maw_utils import SpaceTextField, SpaceCharField, PositiveIntegerField

'''
NOTE: rather than have a separate file router.py to host  a db router, I just
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
        """
        Allow relations if a model in the auth app is involved.
        """
        if obj1._meta.app_label == 'auth' or \
           obj2._meta.app_label == 'auth':
           return True

        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == self.app_label:
            return db == self.app_db
        return None

#end class

#  Start to define models here.

class Institution(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField('Institution name',
        max_length=255, unique=True,
        default='', editable=True)
    xl = 20
    name20 = models.CharField('Short Name',
        max_length=xl, unique=True,
        default='', editable=True,
        help_text=f'Short Institution name with a maximum of {xl} characters.'
       )
    link_url = models.URLField( 'Link_URL', blank=True, null=True)
    notes = SpaceTextField(null=True,  default='',
        blank=True,editable=True)

    # NB: might be need to have oclc_code here permanently,
    # but some versions of import program might make use of it

    oclc_name = models.CharField('OCLC name',
        max_length=xl, unique=False, blank=True,
        default='', editable=True,
        help_text='Optional Code used by OCLC for this Institution with a '
          f'maximum of {xl} characters.')

    def __str__(self):
        return str(self.name20)


# NB: Remember that Django 2.1 admin does NOT
# honor the user Foreign key to another db.
# IT is ai known issue that Django 2.1
# or lower does not support fkey to another db.
# So this app "Profile" uses username as a simple char field now.
# Whomever adds a row to this table must manually verify that the
# username value for a row matches an auth_user username, which matches
# the request.user value, which is a usernama - or we might add
# a separate validator program to check that

class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    # Note: Django gives hint that OneToOne field usually is
    # better than a unique ForeignKey, as we use here for field
    # 'user', but in the case of models in app 'profile',, we
    # anticipate many such models in this 'profile' app to have
    # this type of relationship with the User table, where
    # same field names would collide, if using a OneToOne field,
    # so this way seems better.
    #user = models.ForeignKey(User)
    username = models.CharField(max_length=255, unique=True, null=False,
      help_text="username of MAW user who is authorized to use the Cuba "
        "Libro Datbase.")

    # Field name should probably be agency, maybe later.
    '''
    agent = models.ForeignKey('Institution', on_delete=models.CASCADE,
      blank=True, null=True,
      db_index=True,
      help_text="Institution that this user is affiliated with."
      )
    '''
    agent = models.ForeignKey('Institution', on_delete=models.CASCADE,
      null=False,
      help_text="Institution that this user is affiliated with."
      )

    note = SpaceTextField(blank=False, null=False,
        default="Some note here.",
        help_text="Optional note." )

    def __str__(self):
            return '{}'.format(self.username)

# end class Profile

class Item(models.Model):

    # Field 'id' is 'special', and if not defined here, Django defines
    # it as I do below anyway.
    # However I do include it per python Zen:
    # explicit is better than implicit.
    id = models.AutoField(primary_key=True)

    # Many fields based on Jessica English UF email of 20180319
    # Jessica informed us that accession_number is or should beUniversity of
    # North Carolina at Chapel Hill
    # unique to UF and all other cuba_libro partners.
    accession_number = models.CharField('OCLC accession number',
        max_length=255, unique=True,
        default="Enter accession number here", editable=True)


    '''
    charagent = models.CharField('Institution', max_length=255,
      blank=True, null=True,
      db_index=True,
      help_text="Institution that claimed this item via an 'Action:' on the "
           "parent 'Items' web page."
      )
    '''

    agent = models.ForeignKey('Institution', on_delete=models.CASCADE,
      blank=True, null=True,
      db_index=True,
      help_text="Institution that claimed this item via an 'Action:' on the "
           "parent 'Items' web page."
      )

    agent_modify_date = models.DateTimeField('Modify Date (UTC)',
        null=True, auto_now=True, editable=False)

    STATUS_CHOICES = (
        ( '' ,'-'),
        ( 'PG' ,'Pending'),
        ( 'IP', 'In Process'),
        ( 'DZ', 'Digitized'),
    )

    status = models.CharField('Status',
        blank=True, default='', null=False,
        max_length=50,
        choices=STATUS_CHOICES,
        help_text="Status of processing for this item.")

    status_notes = SpaceTextField(null=True,  default='',
        blank=True,editable=True)

    # Original source data for holding is of the form XXX[-NNN[-MMM]]
    # Later I may modify this model to separate them into: holder,
    # hold_count_low, hold_count_high values if needed.
    # If only NNN is given in imported input, then an import process will
    # set both hold_count_low and hold_count_high to NNN
    # If neither NNN nor MMM is given, set both to 0

    # HOLDING CHOICES are long-standing OCLC codes, so they differ
    # from more friendly PARTNER_CHOICES codes above
    HOLDING_CHOICES = (
        ( 'NDD', 'Duke University'),
        ( 'FXG', 'Florida International'),
        ( 'HLS', 'Harvard'),
        ( 'NYP', 'New York Public'),
        ( 'FUG', 'University of Florida'),
        ( 'FQG' ,'University of Miami'),
        ( 'NOC', 'U of North Carolina'),
    )

    holding = SpaceCharField(max_length=255, default='',
        blank=True, null=False,editable=False,
        choices=HOLDING_CHOICES)

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
    user_1 = models.TextField(null=True, default='', blank=True,
      editable=False)
    user_2 = models.TextField(null=True, default='', blank=True,
      editable=False)
    user_3 = models.TextField(null=True, default='', blank=True,
      editable=False)
    user_4 = models.TextField(null=True, default='', blank=True,
      editable=False)
    user_5 = models.TextField(null=True, default='', blank=True,
      editable=False)
    user_6 = models.TextField(null=True, default='', blank=True,
      editable=False)
    user_7 = models.TextField(null=True, default='', blank=True,
      editable=False)
    user_8 = models.TextField(null=True, default='', blank=True,
      editable=False)
    user_9 = models.TextField(null=True, default='', blank=True,
      editable=False)
    user_10 = models.TextField(null=True, default='', blank=True,
      editable=False)
    user_11 = models.TextField(null=True, default='', blank=True,
      editable=False)
    user_12 = models.TextField(null=True, default='', blank=True,
      editable=False)
    user_13 = models.TextField(null=True, default='', blank=True,
      editable=False)
    user_14 = models.TextField(null=True, default='', blank=True,
      editable=False)
    user_15 = models.TextField(null=True, default='', blank=True,
      editable=False)

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
#end class Item
