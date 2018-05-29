# Generated by Django 2.0.4 on 2018-05-29 14:51

from django.db import migrations
import maw_utils


class Migration(migrations.Migration):

    dependencies = [
        ('submit', '0010_auto_20180529_1032'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='typemodel',
            name='description',
        ),
        migrations.AddField(
            model_name='typemodel',
            name='text',
            field=maw_utils.SpaceTextField(default='Your text here.', help_text='Text for this type.'),
        ),
        migrations.AlterField(
            model_name='submittalfile',
            name='download_name',
            field=maw_utils.SpaceCharField(blank=True, default='', help_text='Name to use for this file as part of this submittal', max_length=255, null=True),
        ),
    ]
