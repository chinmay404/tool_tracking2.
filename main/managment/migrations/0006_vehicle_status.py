# Generated by Django 5.0 on 2024-02-25 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('managment', '0005_vehicle_last_location_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='status',
            field=models.CharField(blank=True, null=True),
        ),
    ]
