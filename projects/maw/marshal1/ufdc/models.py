import uuid

from django.db import models
#from django_enumfield import enum
from django.forms import ModelForm, Textarea

#other useful model imports at times (see django docs, tutorials):
import datetime
from django.utils import timezone
from maw_utils import SpaceTextField, SpaceCharField, PositiveIntegerField
from mptt.models import MPTTModel, TreeForeignKey

#suppoort per field custom widget sizes for admin and inline admin
from django import forms

from django.contrib.auth import get_user_model
User = get_user_model()

'''
NOTE: rather than have a separate file router.py to host HathiRouter, I just
put it here. Also see settings.py should include this python import dot-path
as one of the listed strings in the list setting for DATABASE_ROUTERS.
'''

# Maybe move the HathiRouter later, but for now keep here
#
class UfdcRouter:
    '''
    A router to control all db ops on models in this Application. See apps.py.
    '''

    # Model django_migration database rows use app_label as the 'app' value,
    # and app_label followed by '_', is the db table name prefix
    # for all models of this app.
    app_label = 'ufdc'

    # Main settings.py file will set up a DATABASES[app_db] dictionary to
    # specify this app's database connectiom.
    app_db = 'ufdc_connection'

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
# end class DpsRouter

# NB: we accept the django default of prefixing each real
# db table name with the app_name.

'''
Consider utility that takes an mptt row-node or a root folder of xml files
and applies an xml2rdb config to gen a zip file of sql creation script to
download to apply to local postgres database.
'''

class Aggregation(models.Model):
    '''
    Use id as unique index
    consider bibvid as alternate unique index that allows NULL because
    may consider items 'being constructed' might not have bibvids assigned.

    Todo: add utility to go ahead and descend the resources directory and
    add a row to this table where the named bibvid folder (...AA12345678/00001)
    exists. Maybe it will also get extra data from sobek, if extant.

    Fields to consider:
      bibid, vid, bibvid(with underbar separator)
      resource_subpath
      counts of various file types, pdf, jpeg, etc.
      total file count, including mets, etc in main folder
      count of subfolders, maybe a count
      mets (foreignkey of a mptt model's row that reps the top node
            of the mets file)
    '''
    id = models.AutoField(primary_key=True)

    name = SpaceCharField(verbose_name='Aggregation Name',
        max_length=255, unique=True, blank=False, null=False, default='sample aggregation name',
        help_text= ("Unique name for this aggregation"),
        editable=True)
    created_datetime = models.DateTimeField('Created DateTime (UTC)',
        null=False, auto_now=True, editable=False)
    note = SpaceTextField(max_length=2550, null=True, default='note', blank=True,
      help_text= ("General note"),
      editable=True,
      )

    def __str__(self):
        return str(self.name)
#end class Aggregation


class AggTree(MPTTModel):
    '''
    Directed Acyclic Graph Tree of aggregation hierarchy.

    Each row with a null parent value (ie without a parent), is a 'root node'
    or a 'top level node' of a separate aggregation hierarchy tree

    '''

    id = models.AutoField(primary_key=True)

    # Only one relation in a schema has a null parent
    parent = TreeForeignKey('self', null=True, blank=True,
      related_name='children', db_index=True,
      verbose_name = "Parent relation",
      on_delete=models.CASCADE,)

    # Note, internally a unique suffix for the relation name
    # NOTE: it must be unique within the snow flake tree
    name = SpaceCharField(verbose_name='Aggregation name', max_length=255,
        unique=False, blank=False, null=False, default='name',
        help_text= ("help text here"
          "")
        , editable=True)

    def __str__(self):
        return str(self.name)

    class MPTTMeta:
        order_by = ['name']
# end class AggTree(MPTTModel)
