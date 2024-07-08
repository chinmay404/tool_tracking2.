import datetime
from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser

from .models import Order, Item

class OrderCreateView(APIView):
    """
    API view to receive and process order data.
    """

    def post(self, request):
        """
        Handles POST requests with order data in JSON format.
        """
        try:
            orders = JSONParser().parse(request)
            
           
            for order_data in orders:
                order, created = Order.objects.get_or_create(
                    order_no=order_data['OrderNo'],
                    defaults={
                        'order_date': datetime.datetime.strptime(order_data['OrderDate'], "%d/%m/%Y").date(),
                        'customer_name': order_data['CustomerName'],
                        'party_po_no': order_data.get('PartyPoNo', None),
                        'party_po_date': datetime.datetime.strptime(order_data.get('PartyPoDate', None), "%d/%m/%Y").date() if order_data.get('PartyPoDate', None) else None,
                        'company_short_name': order_data['CompanyShortName'],
                    }
                )
                for item_data in order_data['ItemSummary']:
                    Item.objects.create(
                        order=order,
                        material_name=item_data['MaterialName'],
                        material_uom=item_data['MaterialUom'],
                        po_qty=item_data['PoQty'],
                    )
            return JsonResponse({'message': 'Orders created successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

