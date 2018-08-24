# Generated by Django 2.0.4 on 2018-08-24 16:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import maw_utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CubaLibro',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('agent', models.CharField(blank=True, choices=[('-', '-'), ('DUKE', 'Duke University'), ('FIU', 'Florida International'), ('HVD', 'Harvard'), ('NYP', 'New York Public'), ('UF', 'University of Florida'), ('UMI', 'University of Miami'), ('UNC', 'U of North Carolina')], default='UF', help_text='Partner who can claim to verify or edit this item.', max_length=50, verbose_name='Partner')),
                ('note', maw_utils.SpaceTextField(default='Your note here.', help_text='Optional note.')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]