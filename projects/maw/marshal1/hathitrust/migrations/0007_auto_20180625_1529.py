# Generated by Django 2.0.4 on 2018-06-25 19:29

from django.db import migrations, models
import django.db.models.deletion
import maw_utils


class Migration(migrations.Migration):

    dependencies = [
        ('hathitrust', '0006_uploadfile'),
    ]

    operations = [
        migrations.CreateModel(
            name='DigitalBornYaml',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('creation_datetime', models.DateTimeField(db_index=True, help_text="Creation time of original file/item. Eg, PDF file's date")),
                ('creation_agent', maw_utils.SpaceCharField(help_text='HathiTrust organization code who created digital file.', max_length=255)),
                ('digital_content_provider', maw_utils.SpaceCharField(blank=True, help_text="Optional File-specific content provider's HathiTrust organization code.", max_length=255)),
                ('tiff_artist', maw_utils.SpaceCharField(blank=True, help_text='Required if images lack TIFF Artist or XMP tiff:Artist header.', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='PrintScanYaml',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('capture_datetime', models.DateTimeField(db_index=True, help_text='Date and time of original print scan, estimate OK.')),
                ('scanner_make', maw_utils.SpaceCharField(blank=True, default='CopiBook', max_length=255)),
                ('scanner_model', maw_utils.SpaceCharField(default='tbd', max_length=255)),
                ('scanner_user', maw_utils.SpaceCharField(blank=True, default='University of Florida Digtal Processing Services', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Yaml',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('bitonal_resolution_dpi', maw_utils.PositiveIntegerField(default=0, help_text='Required if images lack resolution information.')),
                ('contone_resolution_dpi', maw_utils.PositiveIntegerField(default=0, help_text='Required if images lack resolution information.')),
                ('image_compression_date', models.DateTimeField(db_index=True, help_text='Required if images were compressed before Submittal Item Package was generated.')),
                ('image_compression_agent', maw_utils.SpaceCharField(blank=True, help_text='Required if images were compressed before Submittal Item Package was generated. Eg, ImageMatick 6.7.8', max_length=255)),
                ('scanning_order', maw_utils.SpaceCharField(choices=[('l2r', 'left-to-right'), ('r2l', 'right-to-left')], default='l2r', help_text='Either left-to-right or right-to-left', max_length=255)),
                ('reading_order', maw_utils.SpaceCharField(choices=[('l2r', 'left-to-right'), ('r2l', 'right-to-left')], default='l2r', help_text='Example: use right-to-left ...', max_length=255)),
                ('item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hathitrust.Item')),
            ],
        ),
        migrations.AddField(
            model_name='printscanyaml',
            name='yaml',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hathitrust.Yaml'),
        ),
        migrations.AddField(
            model_name='digitalbornyaml',
            name='yaml',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hathitrust.Yaml'),
        ),
    ]
