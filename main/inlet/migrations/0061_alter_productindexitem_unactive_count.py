# Generated by Django 5.0 on 2024-03-03 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inlet', '0060_productindexitem_unactive_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productindexitem',
            name='unactive_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
