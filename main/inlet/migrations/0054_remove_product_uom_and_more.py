# Generated by Django 5.0 on 2024-02-24 06:29

import inlet.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inlet', '0053_remove_product_uom_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='UOM',
        ),
        migrations.RemoveField(
            model_name='productindexitem',
            name='balancing_report',
        ),
        migrations.RemoveField(
            model_name='productindexitem',
            name='drwaing',
        ),
        migrations.RemoveField(
            model_name='productindexitem',
            name='inspection_report',
        ),
        migrations.AlterField(
            model_name='master',
            name='uuid',
            field=models.CharField(default=inlet.models.generate_short_uuid, editable=False, max_length=16, primary_key=True, serialize=False, unique=True),
        ),
    ]
