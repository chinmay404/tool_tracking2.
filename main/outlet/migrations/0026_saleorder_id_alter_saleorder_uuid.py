# Generated by Django 5.0 on 2024-03-05 21:38

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outlet', '0025_alter_saleorder_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='saleorder',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('85ca3d2d-b61f-42f7-b5ba-42d1492fd15c'), editable=False, unique=True),
        ),
    ]
