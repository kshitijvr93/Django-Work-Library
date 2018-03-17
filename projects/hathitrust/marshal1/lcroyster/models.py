from django.db import models

# Create your models here.
#from django_enumfield import enum
'''
NOTE: rather than have a separate file router.py to host HathiRouter, I just
put it here. Also see settings.py should include this dot-path
as one of the listed strings in the list
setting for DATABASE_ROUTERS.

'''
# Maybe move the HathiRouter later, but for now keep here
#
class OysterRouter:
    '''
    A router to control all db ops on models in the hathitrust Application.
    '''

    app_label = 'uflib_oyster'
    app_db = 'uflib_oyster_db'

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
#class HathiItemState(enum.Enum):
#       HAS_FOLDER = 0
#       FOLDER_LOADED = 1
#       FILES_EXAMINED = 2
#       FILES_NEED_CHANGES = 3
#       YAML_CREATED = 4

class Sensor_deployment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sensor_name = models.CharField(max_length=1024)
    deployment_datetime = models.DateTimeField()
    location_id = models.IntegerField()
