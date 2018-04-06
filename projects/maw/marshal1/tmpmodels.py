


from django.db import models


class Location(models.Model):
    location_id = models.IntegerField(primary_key=True)
    tile_id = models.IntegerField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    name = models.CharField(unique=True, max_length=200, blank=True, null=True)
    alias1 = models.CharField(unique=True, max_length=200, blank=True, null=True)
    alias2 = models.CharField(unique=True, max_length=200, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'location'


class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    start_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project'
        unique_together = (('project_id', 'name'),)


class Sensor(models.Model):
    sensor_id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, models.DO_NOTHING, blank=True, null=True)
    location = models.ForeignKey(Location, models.DO_NOTHING, blank=True, null=True)
    manufacturer = models.CharField(max_length=150, blank=True, null=True)
    serial_number = models.CharField(max_length=150, blank=True, null=True)
    model_type = models.CharField(max_length=150, blank=True, null=True)
    manufacture_date = models.DateTimeField(blank=True, null=True)
    battery_expiration_date = models.DateTimeField(blank=True, null=True)
    observation_period_unit = models.CharField(max_length=50, blank=True, null=True)
    observation_period_unit_count = models.CharField(max_length=50, blank=True, null=True)
    status_observation = models.CharField(max_length=150, blank=True, null=True)
    status_observation_date = models.DateTimeField(blank=True, null=True)
    meters_above_seafloor = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sensor'


class SensorDeploy(models.Model):
    sensor_deploy_id = models.AutoField(primary_key=True)
    sensor = models.ForeignKey(Sensor, models.DO_NOTHING)
    location = models.ForeignKey(Location, models.DO_NOTHING)
    event_datetime = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sensor_deploy'


class WaterObservation(models.Model):
    water_observation_id = models.AutoField(primary_key=True)
    sensor = models.ForeignKey(Sensor, models.DO_NOTHING, blank=True, null=True)
    observation_datetime = models.DateTimeField(blank=True, null=True)
    in_service = models.IntegerField(blank=True, null=True)
    location = models.ForeignKey(Location, models.DO_NOTHING, blank=True, null=True)
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
    conductivity_ms_cm = models.FloatField(db_column='conductivity_mS_cm', blank=True, null=True)  # Field name made lowercase.
    sound_velocity_m_sec = models.FloatField(blank=True, null=True)
    note = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'water_observation'
        unique_together = (('sensor', 'observation_datetime'),)
