# Generated by Django 5.0 on 2024-02-07 16:50

import django.core.validators
import inlet.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inlet', '0043_product_is_unique_reports'),
    ]

    operations = [
        migrations.AddField(
            model_name='master',
            name='balancing_report',
            field=models.FileField(blank=True, null=True, upload_to='product_uploads/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'gif', 'csv', 'xls', 'xlsx']), inlet.models.ContentTypeValidator(allowed_types=['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 'text/csv', 'application/vnd.ms-excel'])]),
        ),
        migrations.AddField(
            model_name='master',
            name='drwaing',
            field=models.FileField(blank=True, null=True, upload_to='product_uploads/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'gif', 'csv', 'xls', 'xlsx']), inlet.models.ContentTypeValidator(allowed_types=['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 'text/csv', 'application/vnd.ms-excel'])]),
        ),
        migrations.AddField(
            model_name='master',
            name='inspection_report',
            field=models.FileField(blank=True, null=True, upload_to='product_uploads/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'gif', 'csv', 'xls', 'xlsx']), inlet.models.ContentTypeValidator(allowed_types=['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 'text/csv', 'application/vnd.ms-excel'])]),
        ),
    ]
