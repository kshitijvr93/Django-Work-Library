# Generated by Django 2.0.7 on 2018-09-12 12:20

from django.db import migrations, models
import django.db.models.deletion
import maw_utils
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DigitalBornYaml',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('creation_datetime', models.DateTimeField(db_index=True, help_text="Required: Creation time of original file/item. Eg, PDF file's date. <a  href='https://drive.google.com/file/d/0B0EHs5JWGUMLWjU2OHVhQzN5WEk/view'>More</a>")),
                ('creation_agent', maw_utils.SpaceCharField(help_text="Required: HathiTrust organization code who created digital file.<a  href='https://drive.google.com/file/d/0B0EHs5JWGUMLWjU2OHVhQzN5WEk/view'>More</a>", max_length=255)),
                ('digital_content_provider', maw_utils.SpaceCharField(blank=True, help_text="Optional File-specific content provider's HathiTrust organization code. <a  href='https://drive.google.com/file/d/0B0EHs5JWGUMLWjU2OHVhQzN5WEk/view'>More</a>", max_length=255)),
                ('tiff_artist', maw_utils.SpaceCharField(blank=True, help_text="Required if images lack TIFF Artist or XMP tiff:Artist header. <a  href='https://drive.google.com/file/d/0B0EHs5JWGUMLWjU2OHVhQzN5WEk/view'>More</a>", max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department', models.CharField(db_index=True, default='RVP', max_length=64, verbose_name='Dept')),
                ('public', models.BooleanField(default=False, verbose_name='Public')),
                ('date_time', models.DateTimeField(auto_now=True, db_index=True, verbose_name='datetime')),
                ('topic', models.CharField(blank=True, db_index=True, max_length=128, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('location', models.FileField(upload_to='hathitrust/')),
                ('sha512', models.CharField(blank=True, db_index=True, max_length=128, null=True)),
                ('up_name', models.CharField(default='tmpfile', max_length=128, verbose_name='up_name')),
                ('down_name', models.CharField(blank=True, default='tmpfile', max_length=128, null=True, verbose_name='down_name')),
                ('link_name', models.CharField(blank=True, default='click here', max_length=128, null=True, verbose_name='link_name')),
                ('size', models.IntegerField(default=0)),
                ('content_type', models.CharField(default='text/plain', max_length=128, verbose_name='content_type')),
                ('charset', models.CharField(blank=True, max_length=32, null=True, verbose_name='char_set')),
                ('url', models.CharField(default='tmpfile', max_length=256, verbose_name='url')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('uuid4', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('name', models.CharField(default='Hathitrust item name', max_length=255, unique=True)),
                ('modify_date', models.DateTimeField(auto_now=True)),
                ('bib_vid', models.CharField(default='AB12345678_12345', help_text='Bib_vid in format XX12345678_12345', max_length=255, unique=True)),
                ('selected_date', models.DateTimeField(auto_now=True)),
                ('packaged_date', models.DateTimeField(null=True)),
                ('zip_md5', models.CharField(blank=True, max_length=32)),
                ('status', models.CharField(choices=[('new', 'new'), ('compiling', 'compiling'), ('packaged', 'package is valid to send'), ('sent', 'sent'), ('evaluated', 'evaluated'), ('recompiling', 'recompiling'), ('done', 'done')], default='new', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='PrintScanYaml',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('capture_datetime', models.DateTimeField(db_index=True, help_text="Date and time of original print scan, estimate OK. <a  href='https://drive.google.com/file/d/0B0EHs5JWGUMLWjU2OHVhQzN5WEk/view'>More</a>")),
                ('scanner_make', maw_utils.SpaceCharField(blank=True, default='CopiBook', help_text="<a  href='https://drive.google.com/file/d/0B0EHs5JWGUMLWjU2OHVhQzN5WEk/view'>Help</a>", max_length=255)),
                ('scanner_model', maw_utils.SpaceCharField(default='', help_text="<a  href='https://drive.google.com/file/d/0B0EHs5JWGUMLWjU2OHVhQzN5WEk/view'>Help</a>", max_length=255)),
                ('scanner_user', maw_utils.SpaceCharField(blank=True, default='UF Digtal Processing Services', help_text="<a  href='https://drive.google.com/file/d/0B0EHs5JWGUMLWjU2OHVhQzN5WEk/view'>Help</a>", max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='UploadFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department', models.CharField(db_index=True, default='RVP', max_length=64, verbose_name='Dept')),
                ('public', models.BooleanField(default=False, verbose_name='Public')),
                ('date_time', models.DateTimeField(auto_now=True, db_index=True, verbose_name='datetime')),
                ('topic', models.CharField(blank=True, db_index=True, max_length=128, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('location', models.FileField(upload_to='hathitrust/')),
                ('sha512', models.CharField(blank=True, db_index=True, max_length=128, null=True)),
                ('up_name', models.CharField(default='tmpfile', max_length=128, verbose_name='up_name')),
                ('down_name', models.CharField(blank=True, default='tmpfile', max_length=128, null=True, verbose_name='down_name')),
                ('link_name', models.CharField(blank=True, default='click here', max_length=128, null=True, verbose_name='link_name')),
                ('size', models.IntegerField(default=0)),
                ('content_type', models.CharField(default='text/plain', max_length=128, verbose_name='content_type')),
                ('charset', models.CharField(blank=True, max_length=32, null=True, verbose_name='char_set')),
                ('url', models.CharField(default='tmpfile', max_length=256, verbose_name='url')),
                ('item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hathitrust.Item')),
            ],
        ),
        migrations.CreateModel(
            name='Yaml',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('bitonal_resolution_dpi', maw_utils.PositiveIntegerField(default=600, help_text="Required if images lack resolution information.<a  href='https://drive.google.com/file/d/0B0EHs5JWGUMLWjU2OHVhQzN5WEk/view'>More</a>")),
                ('contone_resolution_dpi', maw_utils.PositiveIntegerField(default=600, help_text="Required if images lack resolution information.<a  href='https://drive.google.com/file/d/0B0EHs5JWGUMLWjU2OHVhQzN5WEk/view'>More</a>")),
                ('image_compression_date', models.DateTimeField(db_index=True, help_text="Required if images were compressed before Submittal Item Package was generated.<a  href='https://drive.google.com/file/d/0B0EHs5JWGUMLWjU2OHVhQzN5WEk/view'>More</a>")),
                ('image_compression_agent', maw_utils.SpaceCharField(blank=True, help_text="Required if images were compressed before Submittal Item Package was generated. Eg, ImageMagick 6.7.8. <a  href='https://drive.google.com/file/d/0B0EHs5JWGUMLWjU2OHVhQzN5WEk/view'>More</a>", max_length=255)),
                ('scanning_order', maw_utils.SpaceCharField(choices=[('l2r', 'left-to-right'), ('r2l', 'right-to-left')], default='l2r', help_text="Either left-to-right or right-to-left... <a  href='https://drive.google.com/file/d/0B0EHs5JWGUMLWjU2OHVhQzN5WEk/view'>More</a>", max_length=255)),
                ('reading_order', maw_utils.SpaceCharField(choices=[('l2r', 'left-to-right'), ('r2l', 'right-to-left')], default='l2r', help_text="Example: use right-to-left ...<a  href='https://drive.google.com/file/d/0B0EHs5JWGUMLWjU2OHVhQzN5WEk/view'>More</a>", max_length=255)),
                ('item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hathitrust.Item')),
            ],
        ),
        migrations.AddField(
            model_name='printscanyaml',
            name='yaml',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hathitrust.Yaml'),
        ),
        migrations.AddField(
            model_name='file',
            name='item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hathitrust.Item'),
        ),
        migrations.AddField(
            model_name='digitalbornyaml',
            name='yaml',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hathitrust.Yaml'),
        ),
    ]
