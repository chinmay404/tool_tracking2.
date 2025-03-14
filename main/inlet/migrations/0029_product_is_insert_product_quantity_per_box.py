# Generated by Django 5.0 on 2024-02-02 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inlet', '0028_master_resharp_count_master_resharped'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_insert',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='quantity_per_box',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
