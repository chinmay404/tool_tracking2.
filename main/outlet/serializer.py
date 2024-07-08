from rest_framework import serializers

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
