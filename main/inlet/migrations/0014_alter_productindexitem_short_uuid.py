# Generated by Django 5.0 on 2024-01-07 14:51

import shortuuid.main
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inlet', '0013_master_units_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productindexitem',
            name='short_uuid',
            field=models.CharField(default=shortuuid.main.ShortUUID.uuid, max_length=22, unique=True),
        ),
    ]
