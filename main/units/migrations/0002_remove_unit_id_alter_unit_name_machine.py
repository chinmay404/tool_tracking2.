# Generated by Django 5.0 on 2024-01-08 14:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='unit',
            name='id',
        ),
        migrations.AlterField(
            model_name='unit',
            name='name',
            field=models.CharField(max_length=100, primary_key=True, serialize=False, unique=True),
        ),
        migrations.CreateModel(
            name='Machine',
            fields=[
                ('name', models.CharField(max_length=100, primary_key=True, serialize=False, unique=True)),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='units.unit')),
            ],
        ),
    ]