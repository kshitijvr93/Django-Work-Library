# Generated by Django 2.0.2 on 2018-04-08 18:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lcroyster', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='project_name',
            new_name='name',
        ),
    ]
