# Generated by Django 2.0.3 on 2018-04-02 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuba_libro', '0012_auto_20180329_1136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='agent',
            field=models.CharField(blank=True, choices=[('UF', 'University of Florida'), ('Available', 'Available'), ('Harvard', 'Harvard'), ('NC State', 'North Carolina State University')], default='Available', help_text='Partner to verify or edit this item.', max_length=50, null=True, verbose_name='Partner'),
        ),
    ]
