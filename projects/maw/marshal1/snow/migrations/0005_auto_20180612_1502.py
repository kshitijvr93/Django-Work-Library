# Generated by Django 2.0.4 on 2018-06-12 19:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('snow', '0004_auto_20180612_1500'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='schema',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snow.Schema'),
        ),
        migrations.AlterField(
            model_name='relation',
            name='schema',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snow.Schema'),
        ),
    ]