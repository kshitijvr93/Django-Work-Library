# Generated by Django 2.0.4 on 2018-08-23 22:13

from django.db import migrations, models
import maw_utils


class Migration(migrations.Migration):

    dependencies = [
        ('cuba_libro', '0025_auto_20180823_1807'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='agent',
            field=models.CharField(blank=True, choices=[('-', '-'), ('DUKE', 'Duke University'), ('FIU', 'Florida International'), ('HVD', 'Harvard'), ('NYP', 'New York Public'), ('UF', 'University of Florida'), ('UNC', 'U of North Carolina'), ('UMI', 'University of Miami')], default='-', help_text='Partner who claimed to verify or edit this item.', max_length=50, verbose_name='Claimed'),
        ),
        migrations.AlterField(
            model_name='item',
            name='holding',
            field=maw_utils.SpaceCharField(blank=True, choices=[('NDD', 'Duke University'), ('FXG', 'Florida International'), ('HLS', 'Harvard'), ('NYP', 'New York Public'), ('FUG', 'University of Florida'), ('FQG', 'University of Miami'), ('NOC', 'U of North Carolina')], default='', editable=False, max_length=255),
        ),
    ]