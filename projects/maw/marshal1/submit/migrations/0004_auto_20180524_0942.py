# Generated by Django 2.0.4 on 2018-05-24 13:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('submit', '0003_auto_20180524_0912'),
    ]

    operations = [
        migrations.RenameField(
            model_name='submittal',
            old_name='material_type_id',
            new_name='material_type',
        ),
        migrations.RenameField(
            model_name='submittal',
            old_name='metadata_type_id',
            new_name='metadata_type',
        ),
        migrations.RenameField(
            model_name='submittal',
            old_name='resource_type_id',
            new_name='resource_type',
        ),
        migrations.RenameField(
            model_name='submittalnote',
            old_name='note_type_id',
            new_name='note_type',
        ),
    ]
