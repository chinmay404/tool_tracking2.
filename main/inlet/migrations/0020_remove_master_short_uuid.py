# Generated by Django 5.0 on 2024-01-10 13:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inlet', '0019_product_in_progress_masters_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='master',
            name='short_uuid',
        ),
    ]
