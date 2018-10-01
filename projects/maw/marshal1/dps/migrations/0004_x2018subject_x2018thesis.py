# Generated by Django 2.0.7 on 2018-10-01 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dps', '0003_auto_20180905_0639'),
    ]

    operations = [
        migrations.CreateModel(
            name='X2018Subject',
            fields=[
                ('sn', models.IntegerField(primary_key=True, serialize=False)),
                ('subject', models.IntegerField(blank=True, null=True)),
                ('xtag', models.CharField(blank=True, max_length=8, null=True)),
                ('term', models.CharField(blank=True, max_length=40, null=True)),
                ('keep', models.CharField(blank=True, max_length=1, null=True)),
                ('marc', models.CharField(blank=True, max_length=1, null=True)),
                ('ind1', models.CharField(blank=True, max_length=1, null=True)),
                ('ind2', models.CharField(blank=True, max_length=1, null=True)),
            ],
            options={
                'db_table': 'x2018_subject',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='X2018Thesis',
            fields=[
                ('sn', models.IntegerField(primary_key=True, serialize=False)),
                ('thesis', models.IntegerField(unique=True)),
                ('uf_bibvid', models.CharField(blank=True, max_length=16, null=True)),
                ('title', models.TextField(blank=True, null=True)),
                ('au_fname', models.CharField(blank=True, max_length=40, null=True)),
                ('au_lname', models.CharField(blank=True, max_length=40, null=True)),
                ('pub_year', models.CharField(blank=True, max_length=16, null=True)),
                ('add_ymd', models.CharField(blank=True, max_length=16, null=True)),
                ('add_initials', models.CharField(blank=True, max_length=16, null=True)),
                ('change_ymd', models.CharField(blank=True, max_length=16, null=True)),
                ('change_initials', models.CharField(blank=True, max_length=16, null=True)),
            ],
            options={
                'verbose_name_plural': 'x2018 theses',
                'db_table': 'x2018_thesis',
                'managed': False,
            },
        ),
    ]
