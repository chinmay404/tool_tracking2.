# Generated by Django 5.0 on 2024-03-03 06:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inlet', '0056_remove_productindex_ammount_remove_productindex_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='productindexitem',
            name='short_quantity',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]