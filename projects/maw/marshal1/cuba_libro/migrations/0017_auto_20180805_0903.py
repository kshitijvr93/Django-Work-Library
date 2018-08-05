# Generated by Django 2.0.4 on 2018-08-05 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuba_libro', '0016_item_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='status',
            field=models.CharField(blank=True, choices=[('U', 'Unclaimed'), ('IP', 'In Process'), ('DZ', 'Digitized')], default='Unclaimed', help_text='Status of processing for this item.', max_length=50, null=True, verbose_name='Status'),
        ),
    ]
