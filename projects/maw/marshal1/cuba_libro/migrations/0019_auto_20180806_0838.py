# Generated by Django 2.0.4 on 2018-08-06 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuba_libro', '0018_auto_20180805_0920'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='status',
            field=models.CharField(blank=True, choices=[('', 'Pending'), ('IP', 'In Process'), ('DZ', 'Digitized')], default='', help_text='Status of processing for this item.', max_length=50, verbose_name='Status'),
        ),
    ]