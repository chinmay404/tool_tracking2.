# Generated by Django 5.0 on 2024-01-28 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inlet', '0026_product_active_count_product_break_count_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='productindex',
            name='is_complete',
            field=models.BooleanField(default=False),
        ),
    ]