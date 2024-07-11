from django.contrib import admin
from .models import *
from .forms import SaleOrderForm


class SaleOrderProductInline(admin.TabularInline):
    model = SaleOrderProduct
    fields = ['product', 'quantity', 'uuids', 'status','remaining_quantity','holding_quantity']


class SaleOrderAdmin(admin.ModelAdmin):
    list_display = ( 'order_no','po_number',
                    'vehicle_no', 'group_id_display')
    list_filter = ('group_id',)
    search_fields = ('order_no' , 'uuid')
    inlines = [SaleOrderProductInline]

    form = SaleOrderForm  # Use your custom form

    def group_id_display(self, obj):
        return obj.group_id.group_id if obj.group_id else None

    group_id_display.short_description = 'Group ID'


admin.site.register(SaleOrder, SaleOrderAdmin)


class VehicleSaleOrderGroupAdmin(admin.ModelAdmin):
    list_display = ('tracking_id', 'vehicle', 'TransporterName', 'arrive_date')
    list_filter = ('tracking_id', 'vehicle', 'TransporterName')
    search_fields = ('tracking_id', 'vehicle', 'TransporterName')
    date_hierarchy = 'arrive_date'

admin.site.register(VehicleSaleOrderGroup, VehicleSaleOrderGroupAdmin)

class SaleOrderGroupAdmin(admin.ModelAdmin):
    list_display = ('group_id', 'status', 'vehicle',
                    'driver_name', 'destination')
    list_filter = ('status',)
    search_fields = ('group_id',)


admin.site.register(SaleOrderGroup, SaleOrderGroupAdmin)
