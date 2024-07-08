from django.db import models
import uuid
from uuid import uuid4
from managment.models import CustomUser
from django.utils import timezone
from django.contrib.postgres.fields import JSONField
from shortuuid import ShortUUID
from units.models import Unit
from django.core.validators import FileExtensionValidator
from django.utils.deconstruct import deconstructible
from django.core.exceptions import ValidationError
import hashlib
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver



def generate_short_uuid():
    uuid_str = str(uuid.uuid4())
    sha1_hash = hashlib.sha1(uuid_str.encode()).hexdigest()
    current_year = datetime.now().year
    financial_year = str(current_year)[-2:] + str((current_year - 1))[-2:]
    return sha1_hash[:12] + financial_year




@deconstructible
class ContentTypeValidator:
    def __init__(self, allowed_types):
        self.allowed_types = allowed_types

    def __call__(self, value):
        content_type = getattr(value.file, 'content_type', '')
        if content_type not in self.allowed_types:
            raise ValidationError(f'File type not supported. Allowed types: {", ".join(self.allowed_types)}')

ALLOWED_FILE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 'text/csv', 'application/vnd.ms-excel']


class Product(models.Model):
    name = models.CharField(max_length=1000, unique=True)
    product_id = models.CharField(primary_key=True)
    description = models.TextField()
    active_count = models.PositiveIntegerField(default=0)
    in_progress_masters_count = models.PositiveIntegerField(default=0)
    deactive_count = models.PositiveIntegerField(default=0)
    break_count = models.PositiveIntegerField(default=0)
    is_insert = models.BooleanField(default=False)
    is_unique_reports = models.BooleanField(default=False)
    MaterialCode = models.PositiveIntegerField(null=False)
    


    def __str__(self):
        return self.name

class ProductIndex(models.Model):
    STATUS_CHOICES = [
        ('unverified','Unverified'),

        ('complete','Complete'),
        ('verified','verified'),
        ('active', 'Active'),
        ('deactive', 'Deactive'),
        ('in_progress', 'In Progress'),
        ('dead', 'Dead'),
    ]
    compny_name = models.CharField(max_length=100, null=True, blank=True)
    complete_activated = models.DateTimeField(default=None, null=True)
    supplier_name = models.CharField(max_length=100, null=True, blank=True)
    supplier_gstin = models.CharField(max_length=100, null=True, blank=True)
    is_printed = models.BooleanField(default=False)
    is_printed_by= models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, editable=False ,related_name='printed_product_indexes')
    is_complete = models.BooleanField(default=False)
    gate_inward_No = models.CharField(max_length=10 , null=True)      # Gate Inward No
    products = models.ManyToManyField(Product, through='ProductIndexItem')  # Material Name
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unverified')
    batch_id = models.UUIDField(default=uuid4, unique=True, editable=False) 
    received_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, editable=False, related_name='received_product_indexes')
    arrive_date = models.DateTimeField(default=timezone.now) #Gate Inward date
    party_name = models.CharField(max_length=200 , null=True)
    party_challan_no = models.CharField(max_length=50, null=True)
    part_bill_no = models.CharField(max_length=50, null=True,blank=True)
    SubGlAcNo = models.PositiveIntegerField(null=True)
    party_challan_date = models.CharField(null=True,blank=True)
    grn_no = models.CharField(max_length=50,unique=True)
    grn_date = models.DateField(null=True)
    po_no = models.CharField(max_length=20)
    po_date = models.DateField()
    # rate = models.PositiveIntegerField()
    # ammount = models.PositiveIntegerField()
    
    
    

    
    

    
    def __str__(self):
        return f"Batch ID: {self.batch_id}"

class ProductIndexItem(models.Model):
    UOM = models.CharField(max_length=10 ,null=True ,default=None)
    product_index = models.ForeignKey(ProductIndex, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    actual_quantity = models.PositiveIntegerField(default=0)
    quantity_requested = models.PositiveIntegerField()
    quantity_received = models.PositiveIntegerField()
    unactive_count = models.PositiveIntegerField(default=0)
    short_quantity = models.PositiveIntegerField(null=True,default=0)
    
    

class Master(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('deactive', 'Deactive'),
        ('in_progress', 'In Progress'),
        ('Allocated','allocated'),
        ('dead', 'Dead'),
        ('on_machine','on_machine'),
        ('removed_from_machine','removed_from_machine')
    ]
    quantity_per_box = models.PositiveIntegerField(null=True, blank=True)
    box_capacity = models.PositiveIntegerField(null=True, blank=True)
    static_quantity = models.PositiveIntegerField(null=True, blank=True)
    is_insert = models.BooleanField(default=False)
    resharped = models.BooleanField(default=False)
    resharp_count = models.PositiveIntegerField(default=0)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    uuid = models.CharField(max_length=16, default=generate_short_uuid,
                            unique=True, primary_key=True, editable=False)
    batch_id=models.CharField(max_length=255,editable=False)
    requisition = models.CharField(max_length=50, null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, null=True , blank=True)
    unit_status = models.CharField(max_length=20, default=None, null=True)
    machine = models.CharField(max_length=20, default=None, null=True ,blank=True)
    machine_added_date = models.DateTimeField(default=None, null=True, blank=True)
    machine_remove_date = models.DateTimeField(default=None, null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='in_progress')
    added_date = models.DateTimeField(default=timezone.now)
    received_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, editable=False)
    data_json = models.JSONField(default=dict, null=True)   
    balancing_report  = models.FileField(
        upload_to='~/Reports',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'gif', 'csv', 'xls', 'xlsx']),
            ContentTypeValidator(allowed_types=ALLOWED_FILE_TYPES)
        ]
    )
    drawing  = models.FileField(
        upload_to='~/Reports',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'gif', 'csv', 'xls', 'xlsx']),
            ContentTypeValidator(allowed_types=ALLOWED_FILE_TYPES)
        ]
    )
    inspection_report  = models.FileField(
        upload_to='~/Reports',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'gif', 'csv', 'xls', 'xlsx']),
            ContentTypeValidator(allowed_types=ALLOWED_FILE_TYPES)
        ]
    )
    def __str__(self):
        return f"{self.product.name} ({self.uuid})"





