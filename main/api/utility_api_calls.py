import requests
from tenacity import retry, stop_after_delay, wait_fixed
from django.contrib import messages
import logging
from inlet.models import Master
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from outlet.models import SaleOrderGroup, VehicleSaleOrderGroup, SaleOrderProduct, SaleOrder
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"

retry_settings = {
    'wait': wait_fixed(10),
    'stop': stop_after_delay(180)
}

# Get the logger
logger = logging.getLogger(__name__)

# Retry decorator


@retry(**retry_settings)
def make_api_call_with_retry(payload):
    active_product_info = 'http://10.10.1.18:8400/api/MaterialServices/grninspectioncreate'
    response = requests.post(active_product_info, json=payload, timeout=10)
    response.raise_for_status()
    return response


def inform_active_status(payload, request):
    try:
        response = make_api_call_with_retry(payload)
        if response.status_code == 200:
            messages.success(
                request, 'Active quantity information sent successfully.')
            logger.info('Active quantity information sent successfully.')
            print(f"{GREEN}Active quantity information sent successfully.{RESET}")
            return True
        else:
            messages.error(
                request, f'short_quantity_api : {response.status_code}')
            logger.error(
                f'ACTIVE QUANTITY UPLOAD API : {response.status_code}')
            print(f"{RED}ACTIVE QUANTITY UPLOAD API : {response.status_code}{RESET}")
            return False
    except Exception as e:
        messages.warning(request, f'Retrying API call: {e}')
        logger.warning(f'Retrying API call: {e}')
        print(f"{RED}Retrying API call: {e}{RESET}")
        return False


def group_response(payload, request):
    try:
        response = make_api_call_with_retry(payload)
        if response.status_code == 200:
            messages.success(request, 'Group data Sent sent successfully.')
            logger.info('Group data Sent ERP Successfully.')
            print(f"{GREEN}Group data Sent ERP Successfully.{RESET}")
            return True
        else:
            messages.error(
                request, f'short_quantity_api : {response.status_code}')
            logger.error(f'GROUP DATA UPLOAD API : {response.status_code}')
            print(f"{RED}GROUP DATA UPLOAD API : {response.status_code}{RESET}")
            return False
    except Exception as e:
        messages.warning(request, f'Retrying API call: {e}')
        logger.warning(f'Retrying API call: {e}')
        print(f"{RED}Retrying API call: {e}{RESET}")
        return False


def master_detail(request, uuid):
    try:
        master = get_object_or_404(Master, uuid=uuid)
        data = {
            'uuid': master.uuid,
            'product': master.product.name,
            'status': master.status,
            'received_by': master.received_by.username if master.received_by else None,
            'quantity_per_box': master.quantity_per_box,
            'box_capacity': master.box_capacity,
            'static_quantity': master.static_quantity,
            'is_insert': master.is_insert,
            'resharped': master.resharped,
            'resharp_count': master.resharp_count,
            'requisition': master.requisition,
            'unit': master.unit.name if master.unit else None,
            'unit_status': master.unit_status,
            'machine': master.machine,
            'machine_added_date': master.machine_added_date,
            'machine_remove_date': master.machine_remove_date,
            'added_date': master.added_date,
            'received_by': master.received_by.username if master.received_by else None,
            'balancing_report': master.balancing_report.url if master.balancing_report else None,
            'drawing': master.drawing.url if master.drawing else None,
            'inspection_report': master.inspection_report.url if master.inspection_report else None,
            'data_json': master.data_json
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def group_details(request, group_id):
    group_id_numeric = group_id.split('-')[1]
    group = get_object_or_404(SaleOrderGroup, group_id=group_id_numeric)
    sale_orders = SaleOrder.objects.filter(group_id=group_id_numeric)

    tracking_id = group.tracking_id
    print(tracking_id)
    vehicle_group = None

    try:
        vehicle_group = VehicleSaleOrderGroup.objects.get(
            tracking_id=tracking_id)
    except VehicleSaleOrderGroup.DoesNotExist:
        pass

    if vehicle_group:
        data = {
            'PackingSlipNo': group_id,
            'TrackingId': group.tracking_id,
            'TransportId': '1010000002' if vehicle_group.TransporterName == 'dtdc' else '1010000001',
            'VehicleNo': vehicle_group.vehicle if vehicle_group.vehicle else None,
            'OrderSummary': [],
        }

        for sale_order in sale_orders:
            products_summary = {}
            for product in sale_order.saleorderproduct_set.filter(status='complete'):
                material_code = product.product.MaterialCode
                if material_code not in products_summary:
                    products_summary[material_code] = {
                        'OrderNo': str(sale_order.order_no),
                        'AmendNo': 0,
                        'MaterialCode': material_code,
                        'Quantity': 0,
                        'UIds': [],
                    }

                if product.product.material_UOM == "NOS":
                    products_summary[material_code]['Quantity'] += product.quantity

                uid_count = 0
                final_quantity= 0 
                for uid in product.uuids:
                    for uid_key, quantity in uid.items():
                        print(f"quantity : {quantity}") 
                        uid_info = {
                            'Uid': uid_key,
                            'Quantity': quantity
                        }
                        products_summary[material_code]['UIds'].append(
                            uid_info)
                        uid_count += 1
                        final_quantity += quantity
                        print(f"UID Count : {uid_count}")
                        print(f"Quantity : {final_quantity}")

                if product.product.material_UOM != "NOS":
                    products_summary[material_code]['Quantity'] += final_quantity

            for product_summary in products_summary.values():
                print(f"Product Summary : {product_summary}")
                data['OrderSummary'].append(product_summary)

        return JsonResponse(data)
    else:
        data = {"RESPONSE": "VEHICLE NOT ALLOCATED YET"}
        return JsonResponse(data)


# {"RESPONSE": "VEICHAL NOT ALLOCATED YET"}


def tracking_detail(request, tracking_id):
    vehicle_sale_order_group = get_object_or_404(
        VehicleSaleOrderGroup, tracking_id=tracking_id)

    sale_order_details = []
    for group in vehicle_sale_order_group.order_groups.all():
        for sale_order in group.sale_orders.all():
            order_products = SaleOrderProduct.objects.filter(
                sale_order=sale_order)
            products = []
            for order_product in order_products:
                product = {
                    'name': order_product.product.name,
                    'MaterialCode': order_product.product.MaterialCode,
                    'quantity': order_product.quantity
                }
                print(order_product.quantity)
                products.append(product)

            order_details = {
                'order_no': sale_order.order_no,
                'status': sale_order.status,
                'order_date': sale_order.order_date,
                'po_number': sale_order.po_number,
                'party_po_date': sale_order.party_po_date,
                'total_quantity': sale_order.total_quantity(),
                'products': products
            }
            sale_order_details.append(order_details)

    return render(request, 'tracking_detail.html', {'vehicle_sale_order_group': vehicle_sale_order_group, 'sale_order_details': sale_order_details})


# @method_decorator(csrf_exempt, name='dispatch')


@csrf_exempt
def update_invoice_numbers(request):
    if request.method == 'PUT':
        try:
            if not request.body:
                return JsonResponse({'error': 'Empty request body.'}, status=400)
            try:
                data = json.loads(request.body)
            except Exception as e:
                print(f"{RED}Invalid JSON format: {e}{RESET}")
                return JsonResponse({'error': 'Invalid JSON format.'}, status=400)

            if 'Group_id' in data:
                group_id = data.get('Group_id')
                group_id = group_id.split('-')[1]
            else:
                return JsonResponse({'error': 'Group_id is missing.'}, status=400)

            try:
                sale_orders_data = data.get('sale_orders', {})
            except Exception as e:
                return JsonResponse({'error': 'Invalid sale_orders data.'}, status=400)

            if sale_orders_data:
                sale_order_group = get_object_or_404(
                    SaleOrderGroup, group_id=group_id)

                if sale_order_group:
                    for order_uuid, invoice_no in sale_orders_data.items():
                        sale_order = get_object_or_404(
                            SaleOrder, order_no=order_uuid)
                        sale_order.invoice_no = invoice_no
                        sale_order.save()

                    return JsonResponse({'message': 'Invoice numbers updated successfully.'}, status=200)
                else:
                    return JsonResponse({'error': 'Sale order group not found.'}, status=404)
            else:
                return JsonResponse({'error': 'sale_orders data is empty.'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    else:
        return JsonResponse({'error': 'Only PUT requests are allowed.'}, status=405)
