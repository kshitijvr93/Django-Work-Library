# Generated by Django 2.0.2 on 2018-03-20 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hathitrust', '0002_auto_20180320_1213'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='modify_user_name',
            field=models.CharField(default='name', max_length=1024),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='item',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
