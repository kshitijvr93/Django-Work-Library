# Generated by Django 2.0.4 on 2018-06-12 17:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('snow', '0004_element'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Element',
            new_name='Node',
        ),
    ]
