# Generated by Django 2.0.7 on 2018-10-11 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dps', '0027_batchitem_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batchitem',
            name='id',
            field=models.AutoField(primary_key=True),
        ),
    ]