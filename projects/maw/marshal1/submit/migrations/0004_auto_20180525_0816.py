# Generated by Django 2.0.4 on 2018-05-25 12:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('submit', '0003_remove_submittal_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submittalfile',
            name='file',
            field=models.ForeignKey(help_text='Component file of the associated submittal', on_delete=django.db.models.deletion.CASCADE, to='submit.File'),
        ),
        migrations.AlterField(
            model_name='submittalfile',
            name='rank',
            field=models.PositiveIntegerField(default=1, help_text='Rank order of this file within the set of component files of this submittal'),
        ),
    ]
