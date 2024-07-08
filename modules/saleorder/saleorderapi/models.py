from django.db import models

# Create your models here.

from django.db import models

class Order(models.Model):
    order_no = models.CharField(max_length=255, unique=True)
    order_date = models.DateField()
    customer_name = models.CharField(max_length=255)
    party_po_no = models.CharField(max_length=255, null=True, blank=True)
    party_po_date = models.DateField(null=True, blank=True)
    company_short_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.order_no} - {self.customer_name}"

class Item(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)  # Link Item to Order model
    material_name = models.CharField(max_length=255)
    material_uom = models.CharField(max_length=255)
    po_qty = models.FloatField()

    def __str__(self):
        return f"{self.order.order_no} - {self.material_name}"

