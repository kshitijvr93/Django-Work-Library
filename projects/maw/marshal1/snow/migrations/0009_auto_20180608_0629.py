# Generated by Django 2.0.4 on 2018-06-08 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snow', '0008_auto_20180608_0622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='field',
            name='is_required',
            field=models.BooleanField(default=False, help_text='Whether this field is required for a genre instance.'),
        ),
    ]
