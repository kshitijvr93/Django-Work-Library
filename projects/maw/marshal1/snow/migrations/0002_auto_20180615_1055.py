# Generated by Django 2.0.4 on 2018-06-15 14:55

from django.db import migrations, models
import django.db.models.deletion
import maw_utils
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('snow', '0001_squashed_0006_auto_20180612_1524'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', maw_utils.SpaceCharField(default='', help_text='Unique name for this attribute under this element.', max_length=255, verbose_name='Attribute name')),
                ('max_length', maw_utils.PositiveIntegerField(blank=True, default=255, help_text='Maximum number of characters in this field.', null=True)),
                ('is_required', models.BooleanField(default=False, help_text='Whether this field is required for a schema instance.')),
            ],
            options={
                'ordering': ['node', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', maw_utils.SpaceCharField(default='', help_text='Unique name for this batchSet, include owning org for now.', max_length=255)),
                ('create_datetime', models.DateTimeField(auto_now=True, help_text='Creation DateTime', null=True)),
                ('creator_role', maw_utils.SpaceCharField(default='', help_text="Unique name for this snowflake schema. Please include a version label suffix like 'V1.0'.", max_length=255, unique=True, verbose_name='Schema name')),
            ],
        ),
        migrations.CreateModel(
            name='BatchSet',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', maw_utils.SpaceCharField(default='', help_text='Unique name for this batchSet, include owning org for now.', max_length=255)),
                ('create_datetime', models.DateTimeField(auto_now=True, help_text='Creation DateTime', null=True)),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snow.Field')),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', maw_utils.SpaceCharField(default='', help_text='Unique name for this Role.', max_length=255)),
                ('create_datetime', models.DateTimeField(auto_now=True, help_text='Creation DateTime', null=True)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('creator_role', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_roles', to='snow.Role', verbose_name='Creator role')),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_roles', to='snow.Role', verbose_name='Parent role')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterModelOptions(
            name='node',
            options={'verbose_name': 'Element'},
        ),
        migrations.AlterField(
            model_name='node',
            name='name',
            field=maw_utils.SpaceCharField(default='', help_text='Unique name for this relation under this schema.', max_length=255, verbose_name='Element name'),
        ),
        migrations.AlterField(
            model_name='node',
            name='notes',
            field=maw_utils.SpaceTextField(blank=True, default='', help_text='Notes on this node.', max_length=2550, null=True),
        ),
        migrations.AddField(
            model_name='batchset',
            name='snow_node',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snow.Node'),
        ),
        migrations.AddField(
            model_name='batchset',
            name='vocabulary',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snow.Vocabulary'),
        ),
        migrations.AddField(
            model_name='batch',
            name='batch_set',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snow.BatchSet'),
        ),
        migrations.AddField(
            model_name='attribute',
            name='node',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snow.Node'),
        ),
        migrations.AlterUniqueTogether(
            name='attribute',
            unique_together={('node', 'name')},
        ),
    ]
