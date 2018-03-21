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

class Item(models.Model):

    # Field 'id' is 'special', and if not defined, Django defines
    # it as I do below.
    # However I do include it per python Zen: explicit is better than implicit.
    id = models.AutoField(primary_key=True)

    #
    uuid4 = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=255, unique=True,
        default='Hathitrust item name')
    modify_date = models.DateTimeField(auto_now=True)
    folder_path = models.CharField(max_length=1024)

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
        return self.name

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
