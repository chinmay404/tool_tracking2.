# Generated by Django 5.0 on 2024-02-15 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0021_requisitionproduct_is_old_verified'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='requisitionproduct',
            name='status',
        ),
        migrations.AddField(
            model_name='requisitionproduct',
            name='is_complete',
            field=models.BooleanField(default=False),
        ),
    ]
