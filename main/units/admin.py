from django.contrib import admin
from .models import Unit, Machine, Requisition, RequisitionProduct  # Import the RequisitionProduct model


class UnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'address']
    search_fields = ['name']

class MachineAdmin(admin.ModelAdmin):
    list_display = ['name', 'unit']
    search_fields = ['name', 'unit__name']

    
    

class RequisitionProductInline(admin.TabularInline):
    model = RequisitionProduct
    extra = 1  # You can adjust the number of RequisitionProduct forms displayed

class RequisitionAdmin(admin.ModelAdmin):
    list_display = ['req_no', 'machine', 'quantity', 'date', 'job', 'operation']
    search_fields = ['req_no', 'machine__name']

    inlines = [RequisitionProductInline]  # Include the RequisitionProductInline inline form

admin.site.register(Unit, UnitAdmin)
admin.site.register(Machine, MachineAdmin)
admin.site.register(Requisition, RequisitionAdmin)
