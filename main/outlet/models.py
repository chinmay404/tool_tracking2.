from django.db import models
from inlet.models import Product, Master
from django.urls import reverse
import uuid
from managment.models import CustomUser,Vehicle
from units.models import Unit
from django.db.models import JSONField
from django.utils import timezone

class SaleOrderProduct(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('complete', 'Complete'),
        ('verified', 'verified'),
    ]
    holding_quantity = models.PositiveIntegerField(default=0)
    sale_order = models.ForeignKey('SaleOrder', on_delete=models.CASCADE)
    remaining_quantity = models.PositiveIntegerField(default=0)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')
    uuids = models.JSONField(default=list, null=True, blank=True)
    verified_uuids = models.JSONField(default=list, null=True, blank=True)
    total_weight = models.FloatField(default=0.0 , null=True, blank=True )
    added_weight = models.FloatField(default=0.0 ,  null=True, blank=True)
    remaning_weight = models.FloatField(default=0.0 ,  null=True, blank=True)
    checked_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, editable=False, related_name='sale_order_product_checked')
    verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, editable=False, related_name='sale_order_product_verified')
    
    
    def save(self, *args, **kwargs):
        if not self.quantity:
            self.quantity = self.remaining_quantity
        super().save(*args, **kwargs)


class SaleOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('complete', 'Complete'),
        ('out','Out'),
        ('queue_for_out','queue_for_out'),
        ('checked_at_gate' , 'checked_at_gate'),
        ('recived','recived')
    ]
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    unit = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')
    order_date = models.CharField(max_length=50)
    # grn_number = models.CharField(max_length=50)
    po_number = models.CharField(max_length=50)
    party_po_date = models.CharField(max_length=50)
    vehicle_no = models.CharField(max_length=20, null=True, blank=True)
    driver_name = models.CharField(max_length=200, null=True, blank=True)
    destination = models.CharField(max_length=200, null=True, blank=True)
    order_no = models.CharField(max_length=50,null=True, blank=True)
    products = models.ManyToManyField(Product, through=SaleOrderProduct)
    uuids = models.JSONField(default=dict, null=True, blank=True)
    group_id = models.ForeignKey('SaleOrderGroup', on_delete=models.SET_NULL, null=True, blank=True)
    checked = models.BooleanField(default=False)
    checked_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, editable=False, related_name='checked_sale_order')
    verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, editable=False, related_name='verified_sale_orders')    
    invoice_no = models.CharField(null=True, blank=True)


    def total_quantity(self):
        return sum(item.quantity for item in self.saleorderproduct_set.filter(status='complete'))


class SaleOrderGroup(models.Model):
    STATUS_CHOICES = [
        ('created', 'created'),
        ('complete' , 'complete'),
        ('dispatched', 'dispatched'),
        ('checked','checked'),
        ('enterd_in_unit', 'enterd_in_unit'),
        ('recived', 'recived')

    ]
    tracking_id = models.CharField(max_length=12 ,null=True ,blank=True)
    unit = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='created')
    group_id = models.AutoField(primary_key=True)
    master_count = models.BigIntegerField(default=0)
    allocated = models.BooleanField(default=False)
    sale_orders = models.ManyToManyField(
        SaleOrder, related_name='sale_order_groups')
    vehicle = models.CharField(max_length=100 , null=True, blank=True)
    driver_name = models.CharField(max_length=200, null=True, blank=True)
    destination = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.group_id}"



class VehicleSaleOrderGroup(models.Model):
    tracking_id = models.CharField(max_length=12, primary_key=True)
    TransporterName = models.CharField(max_length=100 , null=True, blank=True)
    vehicle = models.CharField(max_length=100 , null=True, blank=True)
    driver_name = models.CharField(max_length=200, null=True, blank=True)
    order_groups = models.ManyToManyField(SaleOrderGroup, blank=True)
    data_json = JSONField(null=True)
    arrive_date = models.DateTimeField(default=timezone.now) 

    def __str__(self):
        if self.vehicle and self.order_groups.exists():
            group_ids = ', '.join(str(group.group_id) for group in self.order_groups.all())
            return f"Vehicle: {self.vehicle} - Sale Order Groups: {group_ids}"
        elif self.vehicle:
            return f"Vehicle: {self.vehicle} - Sale Order Groups: (No sale order groups assigned)"
        elif self.order_groups.exists():
            group_ids = ', '.join(str(group.group_id) for group in self.order_groups.all())
            return f"Sale Order Groups: {group_ids} (Vehicle not assigned)"
        else:
            return "Vehicle and Sale Order Groups not assigned"