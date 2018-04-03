# Generated by Django 2.0.3 on 2018-03-23 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuba_libro', '0007_auto_20180323_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='abstract',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='agent_modify_date',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='author_address',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Author/Address'),
        ),
        migrations.AlterField(
            model_name='item',
            name='authors_primary',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='authors_quaternary',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='authors_quinary',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='authors_secondary',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='authors_tertiary',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='availability',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='call_number',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='classification',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='data_source',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='database',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='doi',
            field=models.TextField(blank=True, default='', null=True, verbose_name='DOI'),
        ),
        migrations.AlterField(
            model_name='item',
            name='edition',
            field=models.CharField(blank=True, default='', max_length=80, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='holding',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='identifying_phrase',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='isbn_issn',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='ISSN/ISBN'),
        ),
        migrations.AlterField(
            model_name='item',
            name='issue',
            field=models.CharField(blank=True, default='', max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='keywords',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='language',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='links',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='original_foreign_title',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='other_pages',
            field=models.CharField(blank=True, default='', max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='periodical_abbrev',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='periodical_full',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='personal_notes',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='place_of_publication',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='pmcid',
            field=models.TextField(blank=True, default='', null=True, verbose_name='PMCID'),
        ),
        migrations.AlterField(
            model_name='item',
            name='pmid',
            field=models.TextField(blank=True, default='', null=True, verbose_name='PMID'),
        ),
        migrations.AlterField(
            model_name='item',
            name='pub_date_free_from',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='pub_year_span',
            field=models.CharField(default='2018', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='publisher',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='reference_type',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='retrieved_date',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='start_page',
            field=models.CharField(blank=True, default='', max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='title_primary',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='title_secondary',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='titles_tertiary',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='url',
            field=models.TextField(blank=True, default='', null=True, verbose_name='URL'),
        ),
        migrations.AlterField(
            model_name='item',
            name='user_1',
            field=models.TextField(blank=True, default='', editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='user_10',
            field=models.TextField(blank=True, default='', editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='user_11',
            field=models.TextField(blank=True, default='', editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='user_12',
            field=models.TextField(blank=True, default='', editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='user_13',
            field=models.TextField(blank=True, default='', editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='user_14',
            field=models.TextField(blank=True, default='', editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='user_15',
            field=models.TextField(blank=True, default='', editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='user_2',
            field=models.TextField(blank=True, default='', editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='user_3',
            field=models.TextField(blank=True, default='', editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='user_4',
            field=models.TextField(blank=True, default='', editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='user_5',
            field=models.TextField(blank=True, default='', editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='user_6',
            field=models.TextField(blank=True, default='', editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='user_7',
            field=models.TextField(blank=True, default='', editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='user_8',
            field=models.TextField(blank=True, default='', editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='user_9',
            field=models.TextField(blank=True, default='', editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='volume',
            field=models.CharField(blank=True, default='', max_length=30, null=True),
        ),
    ]