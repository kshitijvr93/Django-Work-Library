# Generated by Django 2.0.7 on 2018-10-15 15:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hathitrust', '0003_auto_20181015_1033'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jp2batch',
            name='creating_username',
        ),
        migrations.AddField(
            model_name='jp2batch',
            name='added_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]