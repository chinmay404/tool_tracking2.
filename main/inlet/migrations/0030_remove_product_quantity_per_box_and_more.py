# Generated by Django 5.0 on 2024-02-02 02:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inlet', '0029_product_is_insert_product_quantity_per_box'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='quantity_per_box',
        ),
        migrations.AddField(
            model_name='productindex',
            name='is_insert',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='productindex',
            name='quantity_per_box',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]