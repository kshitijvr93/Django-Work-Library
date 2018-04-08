import uuid
import os
from django.db import models
#from django_enumfield import enum

#other useful model imports at times (see django docs, tutorials):
import datetime
from django.utils import timezone

'''
NOTE: rather than have a separate file router.py to host Router, I just
put it here. Also see settings.py should include this dot-path
as one of the listed strings in the list
setting for DATABASE_ROUTERS.

'''
# Maybe move the Router later, but for now keep here
#
class LcroysterRouter:
    '''
    A router to control all db ops on models in the lcroyster Application.
    '''

    # app_label is really an app name.
    app_label = 'lcroyster'

    # app_db is really a main settings.py DATABASES name, which is
    # more properly a 'connection' name
    app_db = 'lcroyster_connection'

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
#end class LCRoysterRouter

# Create your models here.

class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    #Management ccommand inspect_db did not pick up the unique
    name = models.CharField(max_length=200,unique=True)
    start_date = models.DateField(blank=True, null=True)
    primary_investigator = models.CharField(max_length=200,unique=True)
    notes = models.TextField(blank=True, null=True,
        help_text='Notes about this project and related info free form.')

    class Meta:
        managed = True
        db_table = 'project'
        #unique_together = (('name', 'start_date'),)

class Location(models.Model):
    location_id = models.IntegerField(primary_key=True)
    tile_id = models.IntegerField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    name = models.CharField(unique=True, max_length=200, blank=True,
        null=True,
        help_text='Location name, eg LC_WQ1, LC_WQ2. Shorter for reports.')
    alias1 = models.CharField(unique=True, max_length=200, blank=True,
        null=True,
        help_text='Possibly other name designation of the location')
    alias2 = models.CharField(unique=True, max_length=200, blank=True,
        null=True,
        help_text='Possibly other name designation of the location')

    notes = models.TextField(blank=True, null=True,
        help_text='Notes about the location')

    class Meta:
        managed = True
        db_table = 'location'

class Sensor(models.Model):
    sensor_id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, models.DO_NOTHING, blank=True,
        null=True, help_text="Owner project of this sensor")
    location = models.ForeignKey(Location, models.DO_NOTHING, blank=True,
        null=True,
        help_text="Reserved for the most recent deployed location of this "
            + "sensor. Maintaining this automatically by some method when "
            + "table sensor_deployment is updated may be convenient."
        )
    manufacturer = models.CharField(max_length=150, blank=True, null=True)
    serial_number = models.CharField(max_length=150, blank=True, null=True)
    model_type = models.CharField(max_length=150, blank=True, null=True)
    manufacture_date = models.DateField(blank=True, null=True)
    battery_expiration_date = models.DateField(blank=True, null=True)
    observation_period_unit = models.CharField(max_length=50, blank=True,
        null=True, help_text="Examples: Minute, Hour, or Day, etc.")
    observation_period_unit_count = models.CharField(max_length=50, blank=True,
        null=True,
        help_text="The typical number of observation period units "
            "between observations or readings.")
    status_observation = models.CharField(max_length=150, blank=True, null=True)
    status_observation_datetime = models.DateTimeField(blank=True, null=True)
    meters_above_seafloor = models.FloatField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'sensor'


class SensorDeploy(models.Model):
    sensor_deploy_id = models.AutoField(primary_key=True)
    sensor = models.ForeignKey(Sensor, on_delete=models.DO_NOTHING)
    deploy_datetime = models.DateTimeField()
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING,
        help_text='Location id where the sensor is deployed as of the '
            + 'deploy date-time, where special location 0 means not in service')
    notes = models.TextField(blank=True, null=True,
        help_text='Notes about the deployment'
        )
    testint=models.IntegerField()

    class Meta:
        managed = True
        db_table = 'sensor_deploy'


class WaterObservation(models.Model):
    water_observation_id = models.AutoField(primary_key=True)
    sensor = models.ForeignKey(Sensor, models.DO_NOTHING, blank=True, null=True)
    observation_datetime = models.DateTimeField(blank=True, null=True)
    in_service = models.IntegerField(blank=True, null=True)
    location = models.ForeignKey(Location, models.DO_NOTHING, blank=True,
        null=True)
    phosphorus_ug = models.FloatField(blank=True, null=True)
    nitrogen_ug = models.FloatField(blank=True, null=True)
    chlorophyll_ug = models.FloatField(blank=True, null=True)
    secchi_ft = models.FloatField(blank=True, null=True)
    color_pt_co = models.FloatField(blank=True, null=True)
    specific_conductance_us_cm_25c = models.FloatField(blank=True, null=True)
    specific_conductance_ms_cm_25c = models.FloatField(blank=True, null=True)
    salinity_g_kg = models.FloatField(blank=True, null=True)
    salinity_psu = models.FloatField(blank=True, null=True)
    temperature_c = models.FloatField(blank=True, null=True)
    pressure_psi = models.FloatField(blank=True, null=True)
    pressure_cm = models.FloatField(blank=True, null=True)
    conductivity_ms_cm = models.FloatField(db_column='conductivity_mS_cm',
        blank=True, null=True)  # Field name made lowercase.
    sound_velocity_m_sec = models.FloatField(blank=True, null=True)
    note = models.CharField(max_length=32, blank=True, null=True,
        help_text="Short note on observation, 32 characters or less."
        )

    class Meta:
        managed = True
        db_table = 'water_observation'
        unique_together = (('sensor', 'observation_datetime'),)
