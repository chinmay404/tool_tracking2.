# Generated by Django 5.0 on 2024-03-16 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outlet', '0037_remove_vehiclesaleordergroup_unit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vehiclesaleordergroup',
            name='id',
        ),
        migrations.AddField(
            model_name='vehiclesaleordergroup',
            name='tracking_id',
            field=models.CharField(default='New', max_length=12, primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]