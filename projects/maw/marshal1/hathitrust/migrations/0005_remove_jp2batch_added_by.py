# Generated by Django 2.0.7 on 2018-10-15 16:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hathitrust', '0004_auto_20181015_1142'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jp2batch',
            name='added_by',
        ),
    ]
