# Generated by Django 5.0 on 2024-03-03 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inlet', '0061_alter_productindexitem_unactive_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='productindexitem',
            name='actual_quantity',
            field=models.PositiveIntegerField(default=0),
        ),
    ]