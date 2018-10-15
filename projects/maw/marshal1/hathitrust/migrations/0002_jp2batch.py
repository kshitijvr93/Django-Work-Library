# Generated by Django 2.0.7 on 2018-10-12 18:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dps', '0034_auto_20181012_1152'),
        ('hathitrust', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Jp2Batch',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('create_datetime', models.DateTimeField(auto_now=True, verbose_name='Importing DateTime (UTC)')),
                ('batch_set', models.ForeignKey(blank=True, help_text='Imported BatchSet of which this row is a member.', null=True, on_delete=django.db.models.deletion.CASCADE, to='dps.BatchSet')),
            ],
            options={
                'verbose_name_plural': 'Jp2Batches',
            },
        ),
    ]