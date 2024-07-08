from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField


class Unit(models.Model):
    name = models.CharField(max_length=100, unique=True, primary_key=True)
    address = models.CharField(max_length=100)



class Machine(models.Model):
    unit = models.ForeignKey('units.Unit', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True, primary_key=True)
    active_tools = models.JSONField(default=dict, null=True, blank=True)

    def add_active_tool(self, product_name, master_uuid):
        """
        Add an active tool (product and its master UUID) to the machine.
        """
        if product_name in self.active_tools:
            # If the product already exists in the active tools, append the master UUID
            self.active_tools[product_name].append(master_uuid)
        else:
            # If the product doesn't exist in the active tools, create a new entry
            self.active_tools[product_name] = [master_uuid]
        self.save()

    def remove_active_tool(self, product_name, master_uuid):
        """
        Remove an active tool (product and its master UUID) from the machine.
        """
        if product_name in self.active_tools:
            self.active_tools[product_name].remove(master_uuid)
            if not self.active_tools[product_name]:
                del self.active_tools[product_name]
            self.save()

    def is_uuid_available(self, product_name, master_uuid):
        """
        Check if a given UUID is available under a specific product in active_tools.
        """
        if product_name in self.active_tools:
            return master_uuid in self.active_tools[product_name]
        return False





class Requisition(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE,default='Shri Ram',related_name='requisitions')
    is_completed = models.BooleanField(default=False)
    is_old_verified = models.BooleanField(default=False)
    req_no = models.PositiveBigIntegerField()
    # resharp_count = models.PositiveIntegerField(default=0)
    # break_count = models.PositiveIntegerField(default=0)
    products = models.ManyToManyField('inlet.Product', through='RequisitionProduct')
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    tool = models.JSONField(default=dict, null=True, blank=True) 
    date = models.DateTimeField(default=timezone.now)
    job = models.CharField(max_length=100)
    operation = models.CharField(max_length=100)

    def __str__(self):
        return f"Requisition {self.req_no} for {self.machine.name} in Unit {self.unit.name}"
    
    
    
    
class RequisitionProduct(models.Model):
    total_quantity = models.PositiveIntegerField(default=0 , null=True, blank=True)
    allocate_quantity = models.PositiveIntegerField(default=0 , null=True, blank=True)
    is_old_verified = models.BooleanField(default=False)
    requisition = models.ForeignKey(Requisition, on_delete=models.CASCADE)
    is_complete = models.BooleanField(default=False)
    product = models.ForeignKey('inlet.Product', on_delete=models.CASCADE)
    break_quantity = models.PositiveIntegerField(default=0)
    resharp_quantity = models.PositiveIntegerField(default=0)
    break_uuid = models.JSONField(default=dict, null=True ,blank=True)
    resharp_uuid = models.JSONField(default=dict, null=True ,blank=True)
    added_resharp_quantity = models.PositiveIntegerField(default=0)
    added_break_quantity = models.PositiveIntegerField(default=0)
    
# class Records(models.Model): 





class ReturnMaster(models.Model):
    BREAK = 'break'
    RESHARP = 'resharp'
    RETURN_TYPE_CHOICES = [
        (BREAK, 'Break'),
        (RESHARP, 'Resharp'),
    ]

    uuid = models.UUIDField(unique=True, primary_key=True)
    return_type = models.CharField(max_length=20, choices=RETURN_TYPE_CHOICES)
    machine_name = models.CharField(max_length=100)
    job = models.CharField(max_length=100)
    operation = models.CharField(max_length=100)
    requisition = models.ForeignKey(Requisition, on_delete=models.CASCADE)
    return_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"ReturnMaster {self.uuid} - {self.return_type} - Requisition {self.requisition.req_no}"