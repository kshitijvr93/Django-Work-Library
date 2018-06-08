# Generated by Django 2.0.4 on 2018-06-08 17:50

from django.db import migrations, models
import django.db.models.deletion
import maw_utils


class Migration(migrations.Migration):

    dependencies = [
        ('snow', '0010_field_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lookup',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', maw_utils.SpaceCharField(default='', help_text='Unique name for this lookup.', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Regex',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', maw_utils.SpaceCharField(default='', help_text='Unique name for this field for this output relation.', max_length=255)),
                ('notice', maw_utils.SpaceTextField(blank=True, default='', help_text='Notice to explain a violation for this regex.', max_length=2550, null=True)),
                ('notes', maw_utils.SpaceTextField(blank=True, default='', help_text='Notes on this instance.', max_length=2550, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Vocabulary',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', maw_utils.SpaceCharField(default='', help_text='Unique name for this vocabulary with version suffix.', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('word', maw_utils.SpaceCharField(default='', help_text='Unique name for this vocabulation.', max_length=255)),
                ('vocabulary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snow.Vocabulary')),
            ],
        ),
        migrations.RemoveField(
            model_name='restriction',
            name='field',
        ),
        migrations.RemoveField(
            model_name='field',
            name='type',
        ),
        migrations.DeleteModel(
            name='Restriction',
        ),
        migrations.AddField(
            model_name='regex',
            name='field',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snow.Field'),
        ),
        migrations.AddField(
            model_name='lookup',
            name='field',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snow.Field'),
        ),
        migrations.AddField(
            model_name='lookup',
            name='vocabulary',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snow.Vocabulary'),
        ),
    ]
