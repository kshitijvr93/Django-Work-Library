import uuid
from django.db import models
#from django_enumfield import enum

#other useful model imports at times (see django docs, tutorials):
import datetime
from django.utils import timezone

'''
NOTE: rather than have a separate file router.py to host HathiRouter, I just
put it here. Also see settings.py should include this dot-path
as one of the listed strings in the list
setting for DATABASE_ROUTERS.

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

    # Field 'id' is 'special', and if not defined, Django defines
    # it as I do below.
    # However I do include it per python Zen: explicit is better than implicit.
    id = models.AutoField(primary_key=True)

    # Many fields based on Jessie English UF email of 20180319
    accession_id = models.CharField(max_length=255, unique=True
        , default="unique accession identifier", editable=True)

    PARTNER_CHOICES = (
        ( 'UF' ,'University of Florida'),
        ( 'Available' ,'Available'),
        ( 'Harvard','Harvard'),
        ( 'NC State','North Carolina State University'),
        ( 'Other1','Some other institutional partner(s)?')
    )

    agent = models.CharField('Agent', max_length=50,
        choices=PARTNER_CHOICES, default='Available')

    authors = models.TextField(max_length=255, default=''
        ,editable=True, null=True)

    title = models.TextField(max_length=255, default=''
        ,editable=True)
    pub_year = models.IntegerField(default=2018,editable=True,)
    modify_date = models.DateTimeField(auto_now=True, editable=False)
    notes = models.TextField(max_length=255, default='',
        blank=True,null=True,editable=True)
    place_of_publication = models.TextField(max_length=255,
        blank=True, null=True, editable=True,)

    link_url = models.URLField(blank=True, null=True)
    edition_url = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    sub_file_database = models.TextField("Sub file/database"
        ,blank=True,null=True,max_length=255,editable=True)

    publisher = models.TextField(max_length=255, null=True,
        blank=True,editable=True)

    def __str__(self):
        return self.accession_id

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

'''
Model Item_file will be a single file that a user uploads that will be
associated with a particular Hathitrust item.
So it will have a foreign key to a Hathitrust item.
'''
class Item_file(models.Model):
    #id is a default integer auto field, which is perfect, so let django make itself.
    item_id = models.ForeignKey('Item', on_delete=models.CASCADE,)

#end class Hathi_item
