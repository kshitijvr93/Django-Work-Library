# Generated by Django 2.0.4 on 2018-08-24 16:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cuba_libro', '0027_auto_20180824_1009'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='user',
        ),
        migrations.DeleteModel(
            name='Profile',
        ),
    ]
