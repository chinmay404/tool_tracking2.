# Generated by Django 5.0 on 2024-03-07 06:56

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outlet', '0026_saleorder_id_alter_saleorder_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='saleorder',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]