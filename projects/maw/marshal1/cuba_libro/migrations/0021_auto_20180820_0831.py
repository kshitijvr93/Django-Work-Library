# Generated by Django 2.0.4 on 2018-08-20 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuba_libro', '0020_auto_20180819_1459'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='agent',
            field=models.CharField(blank=True, choices=[('UF', 'University of Florida'), ('Available', 'Available'), ('Harvard', 'Harvard'), ('UNC', 'University of North Carolina at Chapel Hill'), ('-', 'Unclaimed')], default='-', help_text='Partner who claimed to verify or edit this item.', max_length=50, null=True, verbose_name='Claimed'),
        ),
    ]