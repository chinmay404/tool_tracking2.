# Generated by Django 5.0 on 2024-02-15 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0022_remove_requisitionproduct_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='requisitionproduct',
            name='total_quantity',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]