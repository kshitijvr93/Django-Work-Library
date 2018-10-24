# Generated by Django 2.1.2 on 2018-10-23 22:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cuba_libro', '0034_remove_item_agent'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='agent',
            field=models.ForeignKey(blank=True, help_text="Institution that claimed this item via an 'Action:' on the parent 'Items' web page.", null=True, on_delete=django.db.models.deletion.CASCADE, to='cuba_libro.Institution'),
        ),
    ]
