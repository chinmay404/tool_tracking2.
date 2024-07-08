import json
import logging
import os
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from outlet.models import SaleOrder, SaleOrderProduct
from inlet.models import Unit, Product
import requests
from main import settings

# Get logger instance
logger = logging.getLogger('utility_api')

@csrf_exempt
def create_sale_order(data):
    try:
        response_data = []
        for order_data in data:
            order_no = order_data.get('OrderNo')
            existing_order = SaleOrder.objects.filter(
                order_no=order_no).first()
            logger.debug(existing_order)
            if existing_order:
                logger.debug(
                    f"Order with order number {order_no} already exists. Skipping...")
                continue 
            else:
                so_creat(order_data)
                # Pass order_data to the function
    except Exception as e:
        logger.error(e)
        return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse(response_data, safe=False)

def so_creat(order_data):  
    sale_order = None
    try:
        order_no = order_data.get('OrderNo')
        order_date = order_data.get('OrderDate')
        po_number = order_data.get('PartyPoNo')
        party_po_date = order_data.get('PartyPoDate')
        customer_name = order_data.get('CustomerName')
        customer, created = Unit.objects.get_or_create(
            name=customer_name, address="Default")
        if created:
            logger.debug("UNIT CREATED")
        sale_order = SaleOrder.objects.create(
            order_no=order_no,
            order_date=order_date,
            po_number=po_number,
            party_po_date=party_po_date,
            unit=customer_name
        )
        logger.debug("SO created")
    except Exception as e:
        logger.error(f"SO ERROR : {e}")

    if sale_order:
        for item in order_data.get("ItemSummary", []):
            try:
                material_name = item.get('MaterialName')
                po_qty = item.get('PoQty')
                product_instance, created = Product.objects.get_or_create(name=material_name,
                                                                          product_id=material_name)
                if product_instance:
                    sale_order_product, created = SaleOrderProduct.objects.get_or_create(
                        sale_order=sale_order,
                        product=product_instance,
                        remaining_quantity=po_qty,
                        defaults={'quantity': po_qty}
                    )
                    if not created:
                        sale_order_product.quantity = po_qty
                        sale_order_product.save()
                else:
                    logger.debug(
                        f"No Product instance created for {material_name}")
            except Exception as e:
                logger.error(
                    f"Error creating/updating SaleOrderProduct: {e}")

        response_data.append({
            'uuid': str(sale_order.uuid),
            'order_no': sale_order.order_no
        })

    return True
