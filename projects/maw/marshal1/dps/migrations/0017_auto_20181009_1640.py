# Generated by Django 2.0.7 on 2018-10-09 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dps', '0016_auto_20181009_1415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batchset',
            name='import_filename',
            field=models.FileField(help_text='File containing a single spreadsheet to import saved as tab-separated text file', max_length=255, upload_to='', verbose_name='Import File'),
        ),
    ]