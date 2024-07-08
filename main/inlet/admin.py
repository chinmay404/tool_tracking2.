from django.contrib import admin
from django.forms import BaseInlineFormSet
from .models import Product, ProductIndex, Master, ProductIndexItem




class ProductIndexItemInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            if not form.cleaned_data.get('quantity_requested'):
                form.add_error('quantity_requested', 'Quantity requested is required.')

class ProductIndexItemInline(admin.TabularInline):
    model = ProductIndexItem
    extra = 0
    formset = ProductIndexItemInlineFormSet
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_id','MaterialCode','description')
    search_fields = ('name', 'product_id')

@admin.register(ProductIndex)
class ProductIndexAdmin(admin.ModelAdmin):
    exclude = ('batch_id',)
    list_display = ( 'grn_no','batch_id','arrive_date', 'received_by')
    list_filter = ('arrive_date',)
    search_fields = ('products__name', 'batch_id' ,'grn_no')

    inlines = [ProductIndexItemInline]

    



@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ('product', 'uuid', 'added_date', 'received_by', 'status','unit_status','quantity_per_box','is_insert')
    list_filter = ('status', 'added_date','unit_status')
    search_fields = ('product__name', 'uuid', 'batch_id','unit_status')
