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
    project_name = models.CharField(max_length=255,unique=True,
      help_text="UF name for this project"
      )
    proposal_id = models.CharField(max_length=200,unique=True,blank=True)
    sponsor_names = models.CharField(max_length=200,blank=True)
    sponsors_award_id = models.CharField(max_length=200,unique=True)
    uf_award_id = models.CharField(max_length=200,unique=True)
    #Management ccommand inspect_db did not pick up the unique
    contact_investigator = models.CharField(max_length=255,unique=True)
    principal_investigators = models.TextField(blank=True,null=True,unique=True,
      help_text='Usually this is a single investigator, but some sponsors '
      'like NSF allow multiple principal investigators'
      )
    co_principal_investigators = models.TextField(max_length=200,unique=True)
    collaborators = models.TextField(max_length=200,unique=True)

    award_start_date = models.DateField(blank=True, null=True,
      help_text='Notes about this project and related info free form.'
      )
    award_end_date = models.DateField(blank=True, null=True,
      help_text='Notes about this project and related info free form.'
      )
    responsible_unit = models.CharField(max_length=200,unique=True)
    department_id = models.CharField(max_length=200,unique=True)

    notes = models.TextField(blank=True, null=True,
        help_text='Notes about this project and related info in free form.')

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

class SensorType(models.Model):
    # NOTE: consider: make all these fields read-only and require manual
    # MySQL client updates rather than allow website users to update these
    # rows via MAW Admin.
    sensor_type_id = models.AutoField(primary_key=True)
    manufacturer = models.CharField(max_length=150, blank=True, null=True,
       help_text='For example: vanEssen or Star-Oddi.'
       )
    model_type = models.CharField(max_length=100, unique=True,
      help_text='For example: vanEssen usually has type Diver, '
         'and Star-Oddi usually has type CT. '
      )

    initial_deployment_date = models.DateField(blank=True, null=True,
      help_text='Date of initial employment.')

    serial_number = models.CharField(max_length=150, blank=True, null=True,
       help_text='For example: Vnnnn for a vanEssen diver or Snnnn for a Star-Oddi. '
       '\nThis must match exactly how the import program parses out the serial '
       'number from the *diver.Mon or *star.DAT files. See the first nine '
       'sensors and their serial numbers for examples.'
      )

class Sensor(models.Model):
    sensor_id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, models.DO_NOTHING, blank=True,
        null=True, help_text='Owner project of this sensor'
        )
    sensor_type = models.ForeignKey(SensorType, models.DO_NOTHING,
       blank=True, null=True,
       help_text='This identifies the manufacturer and sensor type.'
       )
    serial_number = models.CharField(max_length=150, blank=True, null=True,
       help_text='For example: Vnnnn for a diver or Snnnn for a Star ODDI. '
       'This must match exactly how the import program parses out the serial '
       'number from the *diver.Mon or *star.DAT files. See the first nine '
       'sensors and their serial numbers for examples.'
      )
    manufacture_date = models.DateField(blank=True, null=True)
    battery_expiration_date = models.DateField(blank=True, null=True)
    location = models.ForeignKey(Location, models.DO_NOTHING, blank=True,
        null=True,
        help_text='This field is reserved to report the most recent deployed '
          'location of this sensor. '
          'Unless and until a new database view is implemented, this '
          'field may be available to be updated automatically by some '
          'program when table sensor_deploy is updated.'
        )

    '''
    Retire these fields: they may vary between readings, and in any case are
    inferable from the sensor reading datetimes themselves in the
    water_observation table.

    observation_period_unit = models.CharField(max_length=50, blank=True,
        null=True, help_text="Examples: Minute, Hour, or Day, etc.")
    observation_period_unit_count = models.CharField(max_length=50, blank=True,
       null=True,
       help_text="The typical number of observation period units "
            "between observations or readings."
      )
      ##########
    Theswe fields have no purpose now that we have
    new model SensorSerivce with fields 'active' and service_datetime.

    status_observation = models.CharField(max_length=150, blank=True, null=True,
      help_text=''
      )

    status_observation_datetime = models.DateTimeField(blank=True, null=True,
      help_text=''
      )
    '''
    range_low_mS_cm = models.FloatField(blank=True, null=True,
      help_text='Lowest acceptable value of mS_cm')
    range_high_mS_cm = models.FloatField(blank=True, null=True,
      help_text='Highest acceptable value of mS_cm')

    notes = models.TextField(blank=True, null=True,
        help_text='More notes about the sensor'
        )

    class Meta:
        managed = True
        db_table = 'sensor'
# end class SensorService


class SensorDeploy(models.Model):
    sensor_deploy_id = models.AutoField(primary_key=True)
    sensor = models.ForeignKey(Sensor, on_delete=models.DO_NOTHING)
    deploy_datetime = models.DateTimeField()
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING,
        help_text='Location id where the sensor is deployed as of the '
            + 'deploy date-time, where special location 0 means not in service')
    meters_above_seafloor = models.FloatField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True,
        help_text='Notes about the deployment'
        )

    class Meta:
        managed = True
        db_table = 'sensor_deploy'


class SensorService(models.Model):
    sensor_service_id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING,
      help_text='ISSUE: Does only one project own a sensor for the lifetime of '
       'a sensor? If so, drop this project field from here. '
       '\nProject that owns/maintains the sensor.')
    sensor = models.ForeignKey(Sensor, on_delete=models.DO_NOTHING)
    service_datetime = models.DateTimeField(
      help_text='Date time that sensor was perturbed at start of extraction.'
      '\nNOTE:If the next measurement time for this sensor '
      'will be missed, also add two rows in '
      'sensor_deploy. Add one row using this sensor_datetime and deploy to location 0, '
      'and another row for the time and location the sensor is put back in serivce.'
      )
    download_datetime = models.DateTimeField(
      help_text='Date time that sensor data was downloaded to laptop. '
      '\nNOTE: Is this time needed in addition to the service_datetime?'
      )
    copper_tape = models.BooleanField(
      help_text='ISSUE: is this (1) whether copper tape time was present '
      'for the sensor, or (2) is this whether this servicing added copper tape?'
      )
    color_tape = models.CharField(max_length=150, blank=True, null=True,
      help_text='ISSUE: Is this (1) the tape color found at start of service, '
      'or (2) the color of tape applied to this sensor during service?'
      )
    active = models.BooleanField(
      help_text='ISSUE: is this (1) whether sensor was found to be '
      'active when extracted or (2) whether it was set to be active when '
      're-inserted at the end of this service? '
      )
    heavily_fouled = models.BooleanField(
      help_text='Y or N: Whether heavily fouled.'
      )
    battery_life_remaining_percent = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True,
      help_text='Notes about the deployment'
      '\nISSUE: Dropped download_time, next_download,measurements_downloaded, '
      'project, site, lat, lon, manufacurer, type date_deployed, time_started, '
      'and redeployed because this is coverd by water_observations, '
      'service_datetime and sensor_deploy data.'
        )

    class Meta:
        managed = True
        db_table = 'sensor_deploy'
# end class SensorService


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
