from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from inlet.models import Master, Product, ProductIndex
from django.utils import timezone
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.urls import reverse
from rest_framework.renderers import TemplateHTMLRenderer
from inlet.models import ProductIndex, ProductIndexItem
from django.contrib.auth.decorators import login_required
from managment.decorators import *
from datetime import datetime, timedelta
from .forms import ActivationForm, BatchActivationForm, ReportUploadForm
from rest_framework import status, viewsets
from rest_framework.views import APIView
from django.db import models
from rest_framework.decorators import action
from .serializers import ProductIndexSerializer, SaleOrderSerializer, ItemSerializer
from outlet.models import SaleOrder
import uuid
import base64
from django.http import HttpResponseRedirect
import re
from outlet.qr_gen import single_qr
from django.db.models import Count, Q, Subquery, OuterRef, F
from uuid import UUID
from django.db import transaction
from units.models import Unit
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from .utility_api_calls import *


def is_valid_short_uuid(id_str):
    expected_length = 16
    # if len(id_str) == expected_length and re.match(r'^[a-fA-F0-9]+$', id_str):
    if len(id_str) == expected_length:
        return True
    else:
        return False


@api_view(['GET'])
def get_product_details(request, uuid):
    try:
        master = Master.objects.get(uuid=uuid)
        s = ItemSerializer(master)
        sd = s.data

        return render(request, 'get_product.html', {'data': sd})
    except Master.DoesNotExist:
        return Response({"message": "Master object not found"}, status=404)


def is_valid_id(id_str):
    # Ensure the ID is exactly 16 characters long
    if len(id_str) != 16:
        return False, "Identifier must be exactly 16 characters long."

    id_main = id_str[:12]
    year_code = id_str[-4:]
    current_year_int = datetime.now().year
    current_month = datetime.now().month

    if current_month >= 5:  
        current_fin_year = f"{str(current_year_int)[2:]}{str(current_year_int + 1)[2:]}"
        previous_fin_year = f"{str(current_year_int - 1)[2:]}{str(current_year_int)[2:]}"
    else: 
        current_fin_year = f"{str(current_year_int - 1)[2:]}{str(current_year_int)[2:]}"
        previous_fin_year = f"{str(current_year_int)[2:]}{str(current_year_int - 1)[2:]}"
    if year_code in [current_fin_year, previous_fin_year]:
        return True, "ID is valid."
    else:
        return False, f"ID is not valid. Year code '{year_code}' is incorrect (Expected: {current_fin_year} or {previous_fin_year})."


# PRODUCTS GETS ACTIVATED BELOW !!!!

@login_required(login_url='managment/login/')
@allowed_users(['admins', 'inlet_user'])
def activate_product(request, old_uuid, new_uuid):
    try:
        print(f"NEW ID : {new_uuid} {old_uuid}")
        # if Master.objects.filter(uuid=new_uuid).exists() and is_valid_id(new_uuid):
        if Master.objects.filter(uuid=new_uuid).exists():
            messages.error(
                request, f'UUID {new_uuid} is already in use. Please scan another qr code.')
        is_valid, message = is_valid_id(new_uuid)
        print(f"IS VALID : {is_valid} {message}")
        if not is_valid:
            messages.error(
                request, f'UUID {new_uuid} is in Invalid Format: {message}')
        else:
            master_product = get_object_or_404(Master, uuid=old_uuid)
            print(f"REQUESTE : {request}")
            # if request.user.has_perm('inlet.change_master'):
            if True:
                if master_product.status == 'active' and 'activation' in master_product.data_json:
                    messages.error(
                        request, f'Product with UUID {new_uuid} is already active.')
                else:
                    activator_name = request.user.username
                    activation_date = timezone.now()
                    activator_ip = request.META.get(
                        'REMOTE_ADDR', 'Unknown IP')
                    product = master_product.product
                    if product.material_UOM != "NOS":
                        new_master = Master(
                            product=product,
                            uuid=new_uuid,
                            batch_id=master_product.batch_id,
                            status='active',
                            added_date=master_product.added_date,
                            received_by=master_product.received_by,
                            data_json=master_product.data_json,
                            is_insert=product.is_insert,
                            quantity_per_box=master_product.quantity_per_box,
                            box_capacity=master_product.box_capacity,
                            weight=master_product.weight,
                            initial_weight=True
                        )
                    else:
                        new_master = Master(
                            product=product,
                            uuid=new_uuid,
                            batch_id=master_product.batch_id,
                            status='active',
                            added_date=master_product.added_date,
                            received_by=master_product.received_by,
                            data_json=master_product.data_json,
                            is_insert=product.is_insert,
                            quantity_per_box=master_product.quantity_per_box,
                            box_capacity=master_product.box_capacity
                        )

                    new_data = {
                        'activator_name': activator_name,
                        'activator_ip': activator_ip,
                        'activation_date': activation_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'status_changedstatus_changed_to_to': 'active'
                    }
                    if 'activation' not in new_master.data_json:
                        new_master.data_json['activation'] = new_data
                    else:
                        new_master.data_json['activation'].update(new_data)

                    try:
                        if product.is_insert:
                            product.in_progress_masters_count = max(
                                0, product.in_progress_masters_count - 1)
                        else:
                            product.active_count = product.active_count + 1
                            print(product.in_progress_masters_count)
                            if product.in_progress_masters_count == 0:
                                pass
                            else:
                                try:
                                    product.in_progress_masters_count = product.in_progress_masters_count - 1
                                except Exception as e:
                                    print(f"ERROR IN IN PROGRESS COUNT : {e}")
                                    product.in_progress_masters_count = 0
                            print(f"ACTIVAE COUNT : {product.active_count}")
                            print(
                                f"IN PROGRESS COUNT : {product.in_progress_masters_count}")
                        print(f"ACTIVATED : {old_uuid} ::TO:: {new_uuid}")
                        product.save()
                        new_master.save()
                        master_product.delete()
                        return True
                    except Exception as e:
                        messages.error(
                            request, f'ERROR IN ACTIVATION ERROR  : {e}')
            else:
                messages.error(
                    request, f'Error In Activation: UUID: {new_uuid} ')

    except Master.DoesNotExist as e:
        messages.error(
            request, f'Error In Activation: UUID: {new_uuid}\nError: {e}')

# from django.http import JsonResponse

# @login_required(login_url='managment/login/')
# @allowed_users(['admins', 'inlet_user'])
# def activate_product(request, old_uuid, new_uuid):
#     if request.method == 'POST' and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
#         try:
#             if Master.objects.filter(uuid=new_uuid).exists() and is_valid_id(new_uuid):
#                 return JsonResponse({'error': f'UUID {new_uuid} is already in use. Please scan another qr code.'})
#             else:
#                 master_product = get_object_or_404(Master, uuid=old_uuid)
#                 if request.user.has_perm('inlet.change_master'):
#                     if master_product.status == 'active' and 'activation' in master_product.data_json:
#                         return JsonResponse({'error': f'Product with UUID {new_uuid} is already active.'})
#                     else:
#                         activator_name = request.user.username
#                         activation_date = timezone.now()
#                         activator_ip = request.META.get('REMOTE_ADDR', 'Unknown IP')
#                         product = master_product.product
#                         new_master = Master(
#                             product=product,
#                             uuid=new_uuid,
#                             batch_id=master_product.batch_id,
#                             status='active',
#                             added_date=master_product.added_date,
#                             received_by=master_product.received_by,
#                             data_json=master_product.data_json,
#                             is_insert=product.is_insert,
#                             quantity_per_box=master_product.quantity_per_box
#                         )

#                         new_data = {
#                             'activator_name': activator_name,
#                             'activator_ip': activator_ip,
#                             'activation_date': activation_date.strftime('%Y-%m-%d %H:%M:%S'),
#                             'status_changed_to': 'active'
#                         }
#                         if 'activation' not in new_master.data_json:
#                             new_master.data_json['activation'] = new_data
#                         else:
#                             new_master.data_json['activation'].update(new_data)

#                         try:
#                             if product.is_insert:
#                                 product.in_progress_masters_count = max(0, product.in_progress_masters_count - 1)
#                             else:
#                                 product.active_count += 1
#                                 product.in_progress_masters_count -= 1
#                             product.save()
#                             new_master.save()
#                             master_product.delete()
#                             return JsonResponse({'success': True})
#                         except Exception as e:
#                             return JsonResponse({'error': f'ERROR IN ACTIVATION ERROR: {e}'})
#                 else:
#                     return JsonResponse({'error': f'Error In Activation: UUID: {new_uuid}'})
#         except Master.DoesNotExist as e:
#             return JsonResponse({'error': f'Error In Activation: UUID: {new_uuid}\nError: {e}'})
#     else:
#         return JsonResponse({'error': 'Invalid request method or not an AJAX request.'})


# alert-danger ERROR IN ACTIVATION ERROR E : new row for relation "inlet_product" violates check constraint "inlet_product_in_progress_masters_count_check" DETAIL: Failing row contains (SNGX, SNGX, Insert, -1, 1, 0, 0, t, f, 0).

#                                   ******************* API HOME *************

def api_home(request):
    product_indexes_with_in_progress_masters = ProductIndex.objects.filter(
        products__master__status='in_progress', status='verified', is_printed=True
    ).distinct()
    print(product_indexes_with_in_progress_masters)

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        product_indexes_with_in_progress_masters = product_indexes_with_in_progress_masters.filter(
            Q(gate_inward_No__icontains=search_query) |
            Q(grn_no__icontains=search_query) |
            Q(po_no__icontains=search_query) |
            Q(part_bill_no__icontains=search_query) |
            Q(batch_id__icontains=search_query) |
            Q(party_challan_no__icontains=search_query) |
            Q(status__icontains=search_query) |
            Q(received_by__username__icontains=search_query)
        )

    per_page = 15
    paginator = Paginator(product_indexes_with_in_progress_masters, per_page)
    page = request.GET.get('page', 1)

    try:
        product_indexes = paginator.page(page)
    except PageNotAnInteger:
        product_indexes = paginator.page(1)
    except EmptyPage:
        product_indexes = paginator.page(paginator.num_pages)

    context = {
        'product_indexes_with_in_progress_masters': product_indexes,
        'search_query': search_query,
    }
    return render(request, 'api_home.html', context)

# TODO: Add Active Count Incriment SA Active Via Btch


def activate_via_product(request):
    search_query = request.GET.get('search', '')

    subquery = Master.objects.filter(status='in_progress', product_id=OuterRef(
        'product_id')).values('product_id')[:1]
    products_in_progress = Product.objects.annotate(
        in_progress_count=Count(Subquery(subquery))
    ).filter(
        Q(name__icontains=search_query) |
        Q(product_id__icontains=search_query) |
        Q(productindex__arrive_date__icontains=search_query) |
        Q(in_progress_count__icontains=search_query)
    ).distinct()

    page = request.GET.get('page', 1)
    paginator = Paginator(products_in_progress, 10)

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        'products_with_in_progress_masters': products,
        'search_query': search_query,
    }

    return render(request, 'activate_via_product.html', context)


@never_cache
@login_required(login_url='managment/login/')
@allowed_users(['admins', 'inlet_user'])
def activate_via_batch(request, batch_id):
    try:

        product_index = ProductIndex.objects.get(batch_id=batch_id)
        products_with_masters = product_index.products.prefetch_related(
            'master_set').all()

        for product in products_with_masters:
            product.in_progress_count = product.master_set.filter(
                status='in_progress', batch_id=batch_id).count()
        product_names = [product.name for product in products_with_masters]

        context = {
            'batch': product_index,
            'products_with_masters': products_with_masters,
        }

        return render(request, 'activate_via_batch.html', context)

    except ProductIndex.DoesNotExist:
        messages.error(
            request, 'No Product Index Found. Check For Correct Input.')
        return redirect('activate_via_batch', batch_id=batch_id)


@never_cache
@login_required(login_url='managment/login/')
@allowed_users(['admins', 'inlet_user'])
def activate_via_btach_single_product(request, batch_id, MaterialCode):
    product_index = ProductIndex.objects.filter(batch_id=batch_id).first()
    product = Product.objects.get(MaterialCode=MaterialCode)
    product_index_item = ProductIndexItem.objects.filter(
        product_index=product_index, product=product).first()
    in_progress_count = product_index_item.unactive_count
    print(in_progress_count)
    active_count = Master.objects.filter(
        status='active', batch_id=batch_id, product=product).count()
    if request.method == 'POST':
        new_uuids_str = request.POST.get('new_uuids')
        print(f"NEW UUIDS : {new_uuids_str}")
        new_uuids = [uuid.strip()
                     for uuid in new_uuids_str.split(',') if uuid.strip()]
        in_progress_masters = Master.objects.filter(
            product=product.name,
            batch_id=batch_id,
            status='in_progress',
        )

        if in_progress_masters:
            count = 0
            for master, new_uuid in zip(in_progress_masters, new_uuids):
                done = False
                print(f"OLD UUID : {master.uuid}  NEW UUID : {new_uuid} ")
                done = activate_product(request, master.uuid, new_uuid)
                if done:
                    # if product_index_item.unactive_count < 0:
                    #     product_index_item.unactive_count = 0
                    #     product_index_item.save()
                    product_index_item.unactive_count = product_index_item.unactive_count-1
                    product_index_item.save()
                    count = count + 1
            if done:
                pro = Product.objects.filter(MaterialCode=MaterialCode).first()
                pro.active_count = pro.active_count + count
                pro.save()
                if product_index_item.unactive_count == 0 and all([item.unactive_count == 0 for item in ProductIndexItem.objects.filter(product_index=product_index)]):
                    product_index.status = 'complete'
                    product_index.is_complete = True
                    messages.info(request, 'Making API Call To ERP')
                    if make_api_call(product_index, request):
                        product_index.complete_activated = timezone.now()
                        product_index.save()
                    else:
                        messages.error(
                            request, 'CRITICAL ERROR !!! API CALL FAILED CONTACT ADMIN IMMEDIATELY.')

                messages.success(
                    request, 'All Activation successful for the selected product.')

                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(
                request, 'No product found in progress for the specified batch and product.')
    context = {
        'product_index': product_index,
        'product_index_item': product_index_item,
        'product': product,
        'batch_id': batch_id,
        'in_progress_count': in_progress_count,
        'active_count': active_count,
        'total_count': product_index_item.actual_quantity,

    }

    return render(request, 'activate_via_btach_single_product.html', context)


def make_api_call(product_index, request):
    payload_list = []
    for item in product_index.productindexitem_set.all():
        all_master_uuids = []
        matching_masters = Master.objects.filter(
            batch_id=product_index.batch_id, product=item.product)
        for master in matching_masters:
            all_master_uuids.append(master.uuid)

        payload = {
            "TrnNo": product_index.grn_no,
            "GrnUid": str(product_index.batch_id),
            "MaterialCode": item.product.MaterialCode,
            "AcceptQty": item.quantity_received,
            "RejectedQty": item.short_quantity,
            "UIds": all_master_uuids
        }
        payload_list.append(payload)

    print("[PAYLOAD]:", payload_list)
    if inform_active_status(payload_list, request):
        return True
    else:
        return False


def input_ids_page(request, product_id):
    try:
        product = Product.objects.get(product_id=product_id)
        return render(request, 'input_ids_page.html', {'product': product})
    except Product.DoesNotExist:
        messages.error(request, 'Product not found.')
        return redirect('home')


#                                   ******************* API HOME END *************

def batch_detail(request, batch_id):
    masters = Master.objects.filter(batch_id=batch_id)
    product_index = ProductIndex.objects.filter(batch_id=batch_id).first()
    print(product_index.grn_no)
    qr_code_data = single_qr(batch_id, product_index.grn_no)
    encoded_qr_code_data = base64.b64encode(qr_code_data).decode()

    context = {
        'product_index': product_index,
        'batch_id': batch_id,
        'masters': masters,
        'qr_code': encoded_qr_code_data,
    }

    return render(request, 'batch_detail.html', context)


def activate_master(request, MaterialCode):
    product = get_object_or_404(Product, MaterialCode=MaterialCode)
    in_progress_masters = Master.objects.filter(
        product=product, status='in_progress')
    in_progress_masters_count = Master.objects.filter(
        product=product, status='in_progress').count()
    active_masters_count = Master.objects.filter(
        product=product, status='active').count()
    total_master_count = Master.objects.filter(product=product).count()

    context = {
        'active_masters_count': active_masters_count,
        'total_master_count': total_master_count,
        'in_progress_masters_count': in_progress_masters_count,
        'product': product,
        'in_progress_masters': in_progress_masters,
    }

    return render(request, 'activate_master.html', context)


@login_required(login_url='managment/login/')
@allowed_users(['admins', 'inlet_user'])
def activate_multiple_masters(request, product_id):
    if request.method == 'POST':
        new_uuids_str = request.POST.get('new_uuids', '')
        new_uuids = [uuid.strip()
                     for uuid in new_uuids_str.split(',') if uuid.strip()]
        if not all([UUID(new_uuid, version=4) for new_uuid in new_uuids]):
            return HttpResponse("Invalid UUIDs provided.")
        in_progress_masters = Master.objects.filter(
            product__product_id=product_id, status='in_progress')

        for master, new_uuid in zip(in_progress_masters, new_uuids):
            activate_product(request, master.uuid, new_uuid)

        return redirect('activate_master', product_id=product_id)

    return HttpResponse("Method Not Allowed")


#  API END POINTS

@api_view(['POST'])
def create_product_indexes(request):
    data = request.data  # Assuming JSON data is sent in the request body

    for entry in data:
        # Extract relevant fields from the entry
        supplier_name = entry.get('CompanyShortName')
        gate_inward_no = entry.get('GateInwardNo')
        party_name = entry.get('PartyName')
        party_challan_no = entry.get('PartyChallanNo')
        po_no = entry.get('PoNo')
        rate = entry.get('SubGlAcNo')  # Assuming this is the rate field

        # Create ProductIndex instance
        product_index = ProductIndex.objects.create(
            supplier_name=supplier_name,
            gate_inward_no=gate_inward_no,
            party_name=party_name,
            party_challan_no=party_challan_no,
            po_no=po_no,
            rate=rate,
            # Add other fields as needed
        )

        # Iterate over ItemSummary and create ProductIndexItem instances
        item_summary = entry.get('ItemSummary', [])
        for item_data in item_summary:
            material_code = item_data.get('MaterialCode')
            material_name = item_data.get('MaterialName')
            material_uom = item_data.get('MaterialUom')
            quantity_requested = item_data.get('ChallanQty')
            quantity_received = item_data.get('ReceivedQty')

            # Fetch or create Product instance based on material code
            product, created = Product.objects.get_or_create(
                MaterialCode=material_code,
                # Assuming name is a required field
                defaults={'name': material_name}
            )

            # Create ProductIndexItem instance
            ProductIndexItem.objects.create(
                product_index=product_index,
                product=product,
                quantity_requested=quantity_requested,
                quantity_received=quantity_received,
                UOM=material_uom,
            )

    return Response({'message': 'Product indexes created successfully'})


def upload_reports(request):
    master = None
    if request.method == 'POST':
        master_uuid = request.POST.get('master_uuid')
        try:
            master = Master.objects.get(uuid=master_uuid)
        except Master.DoesNotExist:
            messages.error(
                request, 'Master with provided UUID does not exist.')
            return redirect('upload_reports')

        form = ReportUploadForm(request.POST, request.FILES)
        if form.is_valid():
            for field_name, file_item in request.FILES.items():
                if hasattr(master, field_name):
                    setattr(master, field_name, file_item)

            # Check if any report needs to be removed
            for field_name in ['balancing_report', 'drawing', 'inspection_report']:
                if request.POST.get(f'remove_{field_name}', False):
                    print("FOUND REPOST IN REQUEST")
                    setattr(master, field_name, None)
                    messages.success(
                        request, f'{field_name.replace("_", " ").capitalize()} removed successfully.')

            master.save()
            messages.success(request, 'Reports uploaded successfully.')
        else:
            messages.error(
                request, 'Form is not valid. Please check your inputs.')
    else:
        form = ReportUploadForm()

    return render(request, 'upload_reports.html', {'form': form, 'master': master})


class CreateSaleOrderAPIView(APIView):
    def get(self, request):
        url = "http://10.10.1.18:8400/api/matservices/getsaleapilist"

        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for any HTTP error
            sale_orders_data = response.json()

            created_sale_orders = []

            # for order_data in sale_orders_data:
            #     order_summary = order_data.get('ItemSummary', [])

            #     # Create SaleOrder instance
            #     sale_order = SaleOrder.objects.create(
            #         order_no=order_data['OrderNo'],
            #         order_date=order_data['OrderDate'],
            #         party_po_no=order_data['PartyPoNo'],
            #         party_po_date=order_data['PartyPoDate'],
            #         # Add other fields as needed
            #     )

            #     # Create SaleOrderProduct instances
            #     for item_data in order_summary:
            #         product_name = item_data.get('MaterialName', '')
            #         product_uom = item_data.get('MaterialUom', '')
            #         product_qty = item_data.get('PoQty', 0)
            #         product, _ = Product.objects.get_or_create(
            #             name=product_name)
            #         SaleOrderProduct.objects.create(
            #             sale_order=sale_order,
            #             product=product,
            #             quantity=product_qty,
            #             # Add other fields as needed
            #         )

            #     created_sale_orders.append(sale_order)

            # serializer = SaleOrderSerializer(created_sale_orders, many=True)
            # return Response(serializer.data)

        except requests.RequestException as e:
            return Response({"error": str(e)}, status=500)
