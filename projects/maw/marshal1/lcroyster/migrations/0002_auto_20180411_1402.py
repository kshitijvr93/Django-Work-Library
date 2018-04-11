# Generated by Django 2.0.3 on 2018-04-11 18:02

from django.db import migrations, models
import django.db.models.deletion
import lcroyster.models


class Migration(migrations.Migration):

    dependencies = [
        ('lcroyster', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensortype',
            name='notes',
            field=lcroyster.models.SpaceTextField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='range_high_mS_cm',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='range_low_mS_cm',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='sensordeploy',
            name='location',
            field=models.ForeignKey(help_text='Location where the sensor is deployed as of the deploy date-time.', on_delete=django.db.models.deletion.DO_NOTHING, to='lcroyster.Location'),
        ),
        migrations.AlterUniqueTogether(
            name='sensordeploy',
            unique_together={('sensor', 'deploy_datetime')},
        ),
    ]
