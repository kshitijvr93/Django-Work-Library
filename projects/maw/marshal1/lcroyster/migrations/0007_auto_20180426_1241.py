# Generated by Django 2.0.3 on 2018-04-26 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lcroyster', '0006_auto_20180426_1201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buoyobservation',
            name='buoy_observation_id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]