# Generated by Django 5.0 on 2024-01-08 03:28

import django.db.models.deletion
import shortuuid.main
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inlet', '0015_units_master_machine_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='master',
            name='Units',
        ),
        migrations.AlterField(
            model_name='productindexitem',
            name='short_uuid',
            field=models.CharField(default=shortuuid.main.ShortUUID.uuid, max_length=22, unique=True),
        ),
        migrations.AddField(
            model_name='master',
            name='units',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inlet.units'),
        ),
    ]