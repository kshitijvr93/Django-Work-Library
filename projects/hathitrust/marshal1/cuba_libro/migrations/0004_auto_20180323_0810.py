# Generated by Django 2.0.3 on 2018-03-23 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuba_libro', '0003_auto_20180322_1958'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='accession_number',
            field=models.CharField(default='unique accession number', max_length=255, unique=True),
        ),
    ]
