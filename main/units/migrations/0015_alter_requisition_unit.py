# Generated by Django 5.0 on 2024-02-02 02:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0014_remove_requisition_break_count_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requisition',
            name='unit',
            field=models.ForeignKey(default='Shri Ram', on_delete=django.db.models.deletion.CASCADE, related_name='requisitions', to='units.unit'),
        ),
    ]