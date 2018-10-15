# Generated by Django 2.0.7 on 2018-10-12 14:25

from django.db import migrations
import maw_utils


class Migration(migrations.Migration):

    dependencies = [
        ('dps', '0031_auto_20181012_1019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batchset',
            name='import_vidfield',
            field=maw_utils.SpaceCharField(blank=True, default='VID', help_text="Import file's field name for Volume ID (VID). If empty, value 00001 will be set for the VID value.", max_length=255, null=True, verbose_name='Import field with VID'),
        ),
    ]