from rest_framework import serializers
from inlet.models import *
from outlet.models import SaleOrder, SaleOrderProduct


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Master
        fields = '__all__'
        
        
class ProductIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductIndex
        fields = '__all__'
        
# class ProductIndexSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductIndex
#         fields = [
#             'gate_inward_No',
#             'product',
#             'quantity_requested',
#             'quantity_received',
#             'party_challan_no',
#             'part_bill_no',
#             'part_date',
#             'UOM',
#             'po_no',
#             'rate',
#             'ammount',
#         ]

#     def create(self, validated_data):
#         validated_data['batch_id'] = uuid.uuid4()
#         validated_data['status'] = 'unverified'
#         validated_data['arrive_date'] = timezone.now()

#         # You can also set the 'received_by' field here if needed
#         # validated_data['received_by'] = ...

#         return ProductIndex.objects.create(**validated_data)

class SaleOrderItemSerializer(serializers.Serializer):
    material_name = serializers.CharField()
    material_uom = serializers.CharField()
    po_qty = serializers.DecimalField(max_digits=10, decimal_places=3)

class SaleOrderSerializer(serializers.Serializer):
    order_no = serializers.CharField()
    order_date = serializers.CharField()
    customer_name = serializers.CharField()
    party_po_no = serializers.CharField()
    party_po_date = serializers.CharField()
    company_short_name = serializers.CharField()
    item_summary = SaleOrderItemSerializer(many=True)
