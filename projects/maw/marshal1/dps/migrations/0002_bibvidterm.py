# Generated by Django 2.0.7 on 2018-09-01 20:40

from django.db import migrations, models
import django.db.models.deletion
import maw_utils


class Migration(migrations.Migration):

    dependencies = [
        ('dps', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BibvidTerm',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('mets_element', maw_utils.SpaceCharField(default='name', help_text='METS element that contains this term.', max_length=255)),
                ('name', maw_utils.SpaceCharField(default='name', help_text='If no parent, name of thesaurus, else the name for this narrower term under the broader parent.', max_length=255, verbose_name='Related term name')),
                ('bibvid', models.ForeignKey(help_text='The Bib_vid now using this termsuggested terms', on_delete=django.db.models.deletion.CASCADE, to='dps.Bibvid')),
            ],
        ),
    ]