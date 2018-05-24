# Generated by Django 2.0.4 on 2018-05-24 13:12

from django.db import migrations
import maw_utils


class Migration(migrations.Migration):

    dependencies = [
        ('submit', '0002_auto_20180524_0906'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submittalnote',
            name='note_text',
        ),
        migrations.AddField(
            model_name='submittalnote',
            name='note',
            field=maw_utils.SpaceTextField(blank=True, default='', help_text='Your actual note text.', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='submittal',
            name='language',
            field=maw_utils.SpaceCharField(blank=True, default='', help_text='The actual language.', max_length=255, null=True),
        ),
    ]
