# Generated by Django 5.0 on 2024-02-20 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('managment', '0004_alter_vehicle_current_destination_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='last_location',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='current_destination',
            field=models.CharField(max_length=150, null=True),
        ),
    ]