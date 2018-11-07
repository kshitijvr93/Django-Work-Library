# Generated by Django 2.0.7 on 2018-10-17 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hathitrust', '0010_auto_20181017_0844'),
    ]

    operations = [
        migrations.AddField(
            model_name='jp2job',
            name='jp2_images_processed',
            field=models.IntegerField(default=0, help_text='Number of jp2 images packaged by this job.', null=True),
        ),
        migrations.AddField(
            model_name='jp2job',
            name='packages_created',
            field=models.IntegerField(default=0, help_text='Number of bib_vid packages created by this job.', null=True),
        ),
    ]