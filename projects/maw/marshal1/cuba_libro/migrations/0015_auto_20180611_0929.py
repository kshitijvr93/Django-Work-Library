# Generated by Django 2.0.4 on 2018-06-11 13:29

from django.db import migrations
import maw_utils


class Migration(migrations.Migration):

    dependencies = [
        ('cuba_libro', '0014_auto_20180403_1310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='notes',
            field=maw_utils.SpaceTextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='personal_notes',
            field=maw_utils.SpaceTextField(blank=True, default='', null=True),
        ),
    ]