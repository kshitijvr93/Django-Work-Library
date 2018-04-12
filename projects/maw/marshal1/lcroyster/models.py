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

#CUSTOM FIELD
'''
class SpaceTextField is a TextField that is modified to:
    (1) change newlines and tabs to spaces

    This facilitates saving models in tab-delimited text files that can
    be imported to Excel with minimum fuss.

    Problems averted:

    (1) Tab is used as the delimiter on output by the ExportTsvMixin class,
    and each occurrence of a tab will be replaced by a space character,
    so tabs  will not appear in the text data.
    Otherwise a tab in the data would make the output of the ExportTsvMixin
    un-importable to Excel

    (2) Newlines and returns will be replaced by a space character, which
    otherwise would make the ExportTsvMixin output unimportable to Excel.

    Even if the user or some other application modifies the correlated
    database field to include a tab, return, or newline, this will also replace
    it before appearing in the ExportTsvMixin's output file or in the
    SpaceTextField.

    A help_text may be apt to warn a user populating the field that any tab,
    newline, or return character will always be replaced by a space.

    A similar method may be used for SpaceCharField

'''
class SpaceTextField(models.TextField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def translate(self,value):
        v=(value.replace('\r','').replace('\n',' ').replace('\t',' ')
          )
        return v

    def from_db_value(self,value,expression,connection):
        if value is None:
            return value
        return(self.translate(value))

    def to_python(self, value):
        if value is None:
            return value;
        return(self.translate(value))


class SpaceCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def translate(self,value):
        v=(value.replace('\r','').replace('\n',' ').replace('\t',' ')
          )
        return v

    def from_db_value(self,value,expression,connection):
        if value is None:
            return value
        return(self.translate(value))

    def to_python(self, value):
        if value is None:
            return value;
        return(self.translate(value))
        

# Create your models here.

class Project(models.Model):
    project_id = models.AutoField(primary_key=True)

    project_website_code = models.CharField(max_length=16,unique=True,
      help_text="Short unique code for this project (up to 16 characters)"
      )

    name = models.CharField(max_length=255,unique=True,
      help_text="Long name for this project"
      )
    uf_award_id = models.CharField(max_length=200,
    unique=True, null=True,blank=True,
    help_text="This field should normally start AWD and followed by 5 digits.")
    sponsor_names = models.CharField(max_length=200,blank=True, null=True)
    sponsors_award_id = models.CharField(max_length=200,
      unique=True, blank=True, null=True)
    #Management ccommand inspect_db did not pick up the unique
    contact_investigator = models.CharField(max_length=255,
       blank=True, null=True)
    principal_investigators = SpaceTextField(max_length=255, blank=True,
      null=True, help_text='Usually this is a single investigator, but some sponsors '
      'like NSF allow multiple principal investigators'
      )
    co_principal_investigators = SpaceTextField(max_length=200,
      blank=True, null=True)
    collaborators = SpaceTextField(max_length=200,
      blank=True, null=True)

    award_start_date = models.DateField(blank=True, null=True,
      help_text='Notes about this project and related info free form.'
      )
    award_end_date = models.DateField(blank=True, null=True,
      help_text='Notes about this project and related info free form.'
      )
    responsible_unit = models.CharField(max_length=200,
      blank=True, null=True)
    department_id = models.CharField(max_length=200,
      blank=True, null=True)

    proposal_id = models.CharField(max_length=200,unique=True
        ,null=True,blank=True)
    notes = SpaceTextField(max_length=255, blank=True, null=True,
        help_text='Notes about this project and related info in free form.')

    def __str__(self):
        return '{}'.format(self.project_website_code)
#end class Project

class Location(models.Model):
    location_id = models.IntegerField(primary_key=True)
    # Mysql 5.7 load data local infile fails if csv file has empty
    # value for tile_id even though NULL is true, so we set
    # default to 0 so we can export this model and load it to
    # another mysql db connection
    tile_id = models.IntegerField(blank=True, null=True, default=None)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    name = models.CharField(unique=True, max_length=200, blank=True,
        null=True,
        help_text='Location name, eg LCR Buoy One.')
    alias1 = models.CharField(unique=True, max_length=200, blank=True,
        null=True,
        help_text='Alternative name designation of the location')
    alias2 = models.CharField(unique=True, max_length=200, blank=True,
        # may need default None here to remind/force mysql loader to allow
        # nulls when it loads data. # Using null=True alone does not do it.
        null=True, default=None,
        help_text='Alternative name designation of the location')

    notes = SpaceTextField(max_length=2550, blank=True, null=True,
        help_text='Notes about the location')

    def __str__(self):
        return '{}'.format(self.name)
#end class Location

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
    notes = SpaceTextField(max_length=255, null=True, blank=True)

    def __str__(self):
        return '{}:{}'.format(self.manufacturer, self.model_type)
# end class SensorType

#end class SpaceTextField


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
       unique=True,
       help_text='For example: VNNNN for a vanEssen:diver sensor '
       'or simply NNNN for a Star-Oddi:CT sensor. '
       'For example, one '
       'vanEssen:Diver sensor serial number is V5602 and one '
       'Star-Oddi:CT serial number is 8814.'
      )
    range_low_mS_cm = models.FloatField(blank=True, null=True)
    range_high_mS_cm = models.FloatField(blank=True, null=True)
    '''
    location = models.ForeignKey(Location, models.DO_NOTHING, blank=True,
        null=True,
        help_text='This field is reserved to report the most recent deployed '
        'location of this sensor. Value 0 or Null means sensor not in service.'
        'Unless and until a new database view is implemented, this '
        'field is reserved to be updated automatically by some '
        'program when table sensor_deploy is updated, '
        'so manual edits could be overwritten',
        )

    initial_deployment_datetime = models.DateTimeField(blank=True, null=True,
      help_text='Datetime of initial employment.',)
    '''

    manufacture_date = models.DateField(blank=True, null=True,)
    battery_expiration_date = models.DateField(blank=True, null=True, )

    '''
    Retire these fields: they may vary between readings, and in any case are
    inferable from the sensor reading datetimes themselves in the
    water_observation table. The most recent period between two measurements
    may be queried from the database and given in a report.

    observation_period_unit = models.CharField(max_length=50, blank=True,
        null=True, help_text="Examples: Minute, Hour, or Day, etc.")
    observation_period_unit_count = models.CharField(max_length=50, blank=True,
       null=True,
       help_text="The typical number of observation period units "
            "between observations or readings."
      )
      ##########
    These fields have no purpose now that we have
    new model SensorSerivce with fields 'active' and service_datetime.

    status_observation = models.CharField(max_length=150, blank=True, null=True,
      help_text=''
      )

    status_observation_datetime = models.DateTimeField(blank=True, null=True,
      help_text=''
      )
    '''

    notes = SpaceTextField(max_length=255, blank=True, null=True,
        help_text='More notes about the sensor'
        )

    # See how to support order by ForeignKey  on change list form
    # https://stackoverflow.com/questions/8992865/django-admin-sort-foreign-key-field-list
    # come back to this... still cannot order by location_id on the
    # sensor change list form in admin...

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "location_id":
            kwargs["queryset"] = Location.objects.order_by('name')
        return (super(MyModelAdmin, self)
            .formfield_for_foreignkey(db_field, request, **kwargs))

    def __str__(self):
        return '{}'.format(self.serial_number)

    class Meta:
        unique_together = (('sensor_type', 'serial_number'),)
        ordering = [ 'sensor_type', ]
# end class Sensor


class SensorDeploy(models.Model):
    sensor_deploy_id = models.AutoField(primary_key=True)
    sensor = models.ForeignKey(Sensor, on_delete=models.DO_NOTHING)
    deploy_datetime = models.DateTimeField()
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING,
        help_text='Location where the sensor is deployed as of the '
            + 'deploy date-time.')
    notes = SpaceTextField(max_length=255, blank=True, null=True,
        help_text='Notes about the deployment'
        )

    def __str__(self):
        return '{}:{}'.format(self.sensor.serial_number, self.deploy_datetime)

    class Meta:
        unique_together = (('sensor', 'deploy_datetime'),)
# end class SensorDeploy


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
    measurements_downloaded = models.IntegerField(blank=True, null=True)
    heavily_fouled = models.BooleanField(
      help_text='Y or N: Whether heavily fouled.'
      )
    battery_life_remaining_percent = models.IntegerField(blank=True, null=True,
      help_text="Enter an integer from 0 to 100."
      )
    notes = SpaceTextField(max_length=255, blank=True, null=True,
      help_text='Notes about the deployment'
      '\nISSUE: Dropped download_time, next_download,measurements_downloaded, '
      'project, site, lat, lon, manufacurer, type date_deployed, time_started, '
      'and redeployed because this is coverd by water_observations, '
      'service_datetime and sensor_deploy data.'
        )

    def __str__(self):
        return '{}:{}'.format(self.sensor.serial_number, self.service_datetime)
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
        unique_together = (('sensor', 'observation_datetime'),)

    def __str__(self):
        return '{}:{}'.format(self.sensor.serial_number,
          self.observation_datetime)
#end class waterobservation
