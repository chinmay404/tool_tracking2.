# Generated by Django 5.0 on 2024-01-12 04:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0007_alter_requisition_tool'),
    ]

    operations = [
        migrations.AddField(
            model_name='requisition',
            name='is_completed',
            field=models.BooleanField(default=False),
        ),
    ]