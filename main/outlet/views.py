from django.shortcuts import render, HttpResponse, get_object_or_404, redirect, reverse
from .forms import *
from managment.models import Vehicle
from .models import SaleOrder, SaleOrderProduct, SaleOrderGroup, VehicleSaleOrderGroup
from django.http import HttpResponse, HttpResponseBadRequest
from inlet.models import Product, Master
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from managment.decorators import unauth_user, allowed_users
from django.db.models import Sum, Count, Max, F, Value, Q
from .gen_pdf import pdf
from django.db import transaction
import json
import uuid
import calendar
import base64
import time
from .qr_gen import single_qr
from units.models import Unit
from django.utils import timezone
from django.http import HttpResponseRedirect
import datetime


@login_required(login_url='managment/login/')
@allowed_users(allowed_roles=['admins', 'outlet_user',])
def outlet_home(request):
    sale_order_groups = SaleOrderGroup.objects.filter(status='created')
    return render(request, 'outlet_home.html', {'sale_order_groups': sale_order_groups})


def sale_order_group_history(request):
    sale_order_groups = SaleOrderGroup.objects.all()
    return render(request, 'sale_order_group_history.html', context={'sale_order_groups': sale_order_groups})

# PDF START HERE


@login_required(login_url='managment/login/')
@allowed_users(allowed_roles=['admins', 'outlet_user',])
def sale_order_detail(request, order_no):
    sale_order = get_object_or_404(SaleOrder, order_no=order_no)
    total_products_required = sale_order.saleorderproduct_set.aggregate(
        total_required=Sum('quantity'))['total_required']
    total_products_added = len(sale_order.uuids)
    print(f"total_products_required : {total_products_required}")
    print(f"total_products_added     : {total_products_added}")
    remaning = total_products_required - total_products_added
    sale_order_product = sale_order.saleorderproduct_set.all()

    context = {
        'sale_order': sale_order,
        'total_products_required': total_products_required,
        'total_products_added': total_products_added,
        'remaning': remaning
    }

    return render(request, 'sale_order_detail.html', context)


def download_qrcode_pdf(request, order_no):
    response = pdf(order_no)
    return response

# PDF END HERE


@login_required(login_url='managment/login/')
@allowed_users(allowed_roles=['admins', 'outlet_user',])
def sale_order_product_detail(request, order_no, MaterialCode):
    sale_order = get_object_or_404(SaleOrder, order_no=order_no)
    sale_order_status = sale_order.status
    # product = Product.objects.filter(MaterialCode=MaterialCode)
    sale_order_product = get_object_or_404(
        SaleOrderProduct, product__MaterialCode=MaterialCode, sale_order=sale_order)
    inventory_count = sale_order_product.product.active_count
    selected_master_uuids = sale_order_product.uuids
    form = AddUUIDForm(request.POST)
    product = sale_order_product.product
    selected_master_uuids_count = len(selected_master_uuids)
    if selected_master_uuids_count == sale_order_product.quantity:
        sale_order_product.status = 'complete'
        sale_order_product.save()
    return render(request, 'sale_order_product_detail.html', {'sale_order': sale_order, 'sale_order_product': sale_order_product, 'inventory_count': inventory_count, 'selected_master_uuids': selected_master_uuids, 'form': form, 'product': product, 'selected_master_uuids_count': selected_master_uuids_count, 'sale_order_status': sale_order_status})


@login_required(login_url='managment/login/')
@allowed_users(allowed_roles=['admins', 'outlet_user',])
def add_uuid(request, order_no, MaterialCode):
    if request.method == 'POST':
        new_uuid = request.POST.get('new_uuid')
        print(f"NEW UUID : {new_uuid}")
        sale_order = get_object_or_404(SaleOrder, order_no=order_no)
        sale_order_product = get_object_or_404(
            SaleOrderProduct, product__MaterialCode=MaterialCode, sale_order=sale_order)
        sale_order_product_id = Product.objects.filter(
            MaterialCode=MaterialCode)
        print('SALE ORDERPRODUCT ID : {sale_order_product_id}')
        print(f"SALE ORDER PRODUCT : {sale_order_product}")
        print(f"SOP QUANTITY : {sale_order_product.quantity}")

        if sale_order_product.remaining_quantity == 0 and sale_order_product.product.is_insert:
            print("IN HOLDING UUIDS")
            add_holding_uuid(request, order_no, sale_order_product_id,
                             new_uuid, sale_order_product, sale_order)
            return redirect('sale_order_product_detail', order_no=order_no, MaterialCode=MaterialCode)
        else:
            if sale_order_product.product.is_insert and sale_order_product.remaining_quantity > 0:
                add_uuid_is_insert(
                    request, order_no, sale_order_product_id, new_uuid, sale_order_product, sale_order)
                return redirect('sale_order_product_detail', order_no=order_no, MaterialCode=MaterialCode)
            else:
                try:
                    add_uuid_not_insert(
                        request, order_no, sale_order_product_id, sale_order_product, new_uuid)
                    return redirect('sale_order_product_detail', order_no=order_no, MaterialCode=MaterialCode)

                except Exception as e:
                    messages.error(request, f"Error in ADD UUID : {e}")
                    return redirect('sale_order_product_detail', order_no=order_no, MaterialCode=MaterialCode)
                    print(e)


def add_holding_uuid(request, order_no, MaterialCode, new_uuid, sale_order_product, sale_order):
    print("IN HOLDING")
    matching_master = Master.objects.filter(
        product=sale_order_product.product, uuid=new_uuid).first()
    if matching_master:
        print(f"MASTHICHNG MASTER FROM HOLDING QUANTITY : {matching_master}")
        if matching_master.status == 'active' and matching_master.quantity_per_box == 0:
            box_capacity = matching_master.box_capacity
            print(f"BOX CAPACITY FROM HOLDING QUANTITY : {box_capacity}")
            print(
                f"sale_order_product.holding_quantity : {sale_order_product.holding_quantity}")
            # Calculate how much to add to quantity per box and update holding quantity
            if sale_order_product.holding_quantity > 0:
                if sale_order_product.holding_quantity >= box_capacity:
                    matching_master.quantity_per_box += box_capacity
                    sale_order_product.holding_quantity -= box_capacity
                else:
                    matching_master.quantity_per_box += sale_order_product.holding_quantity
                    sale_order_product.holding_quantity = 0
                quantity_per_box = matching_master.quantity_per_box
                matching_master.save()
                sale_order_product.uuids.append({new_uuid: quantity_per_box})
                material_code = sale_order_product.product.MaterialCode
                try:
                    print(f"STARTING : {sale_order.uuids}")
                    if material_code not in sale_order.uuids:
                        print(f"INSIDE IF  : {sale_order.uuids[material_code]}")
                        print(f"MATERIAL CODE : {material_code}")
                        print("NOT EXITS")
                        sale_order.uuids[material_code] = []
                    else:
                        print("EXITS")
                        print(f"EXISTING : {sale_order.uuids[material_code]}")

                    quantity_per_box = matching_master.quantity_per_box
                    sale_order.uuids[material_code].append({new_uuid: quantity_per_box})
                    print(f"AFTER ADDING : {sale_order.uuids[material_code]}")
                    sale_order.save()

                except Exception as e:
                    messages.error(request, str(e))
                sale_order_product.save()
                # messages.success(request, f"Quantity per box updated to {matching_master.quantity_per_box}")
            else:
                messages.error(
                    request, "No holding quantity available to add to quantity per box")
        else:
            messages.error(request, "Box is Not Empty")
    else:
        messages.error(request, "No matching master found for the UUID")


def add_uuid_is_insert(request, order_no, sale_order_product_id, new_uuid, sale_order_product, sale_order):
    matching_master = Master.objects.filter(
        product=sale_order_product.product, uuid=new_uuid).first()
    if sale_order_product.product.is_insert and sale_order_product.quantity >= 1:
        quantity_per_box = matching_master.quantity_per_box
        print(
            f"quantity_per_box  FROM add_uuid_is_insert :{add_uuid_is_insert}")
        if quantity_per_box and matching_master.status == 'active':
            try:
                remaining_quantity = abs(
                    quantity_per_box - sale_order_product.remaining_quantity)
                adding_quantity = min(
                    quantity_per_box, sale_order_product.remaining_quantity)
                if remaining_quantity >= 0:
                    sale_order_product.remaining_quantity = sale_order_product.remaining_quantity - adding_quantity
                    sale_order_product.holding_quantity += adding_quantity
                    matching_master.quantity_per_box -= adding_quantity
                    matching_master.save()
                    sale_order_product.save()
                    messages.success(
                        request, "Quantity Taken Out Successfully From The Box")
                else:
                    messages.error(
                        request, "Not enough quantity in the sale order product")
            except Exception as e:
                messages.error(request, f"Error: {e}")
    else:
        messages.error(
            request, "Scaned UUID is not an insert or contain quantity is less than 1")


# def add_uuid_is_insert(request, order_no, sale_order_product_id, new_uuid, sale_order_product,sale_order):
#     matching_master = Master.objects.filter(
#         product=sale_order_product.product, uuid=new_uuid).first()
#     print(f"Matching MASter : {matching_master}")
#     if sale_order_product.product.is_insert and sale_order_product.quantity > 1:
#         print("INSIDE IF")
#         quantity_per_box = matching_master.quantity_per_box
#         if quantity_per_box and matching_master.status == 'active':
#             try:
#                 sale_order_product.quantity -= quantity_per_box
#                 sale_order_product.holding_quantity += quantity_per_box
#                 matching_master.quantity_per_box -= quantity_per_box
#                 matching_master.save()
#                 sale_order_product.save()
#                 messages.success(request, f"Added Successful")
#             except Exception as e:
#                 messages.error(request, f"ERROR 1")
#         if new_uuid not in sale_order_product.uuids and new_uuid not in sale_order.uuids:
#             sale_order_product.uuids.append(new_uuid)
#             sale_order_product.save()
#             sale_order.uuids.append(new_uuid)
#             sale_order.save()


def add_uuid_not_insert(request, order_no, sale_order_product_id, sale_order_product, new_uuid):
    sale_order = get_object_or_404(SaleOrder, order_no=order_no)
    remaining_quantity = sale_order_product.remaining_quantity
    print(f"REMAIN QUANTITY : {remaining_quantity}")
    uuid_set = {uuid for d in sale_order_product.uuids for uuid in d}
    
    if new_uuid in uuid_set:
        messages.error(request, f"Product is already scanned and added to the list.")
        return  # Exit early if UUID is already in the list

    matching_master = Master.objects.filter(
        product=sale_order_product.product, uuid=new_uuid).first()
    
    if not matching_master:
        messages.error(request, f"ID: {new_uuid} does not match the product in the sale order product: {sale_order_product.product}.")
    elif matching_master.status != 'active':
        messages.error(request, f"UUID '{new_uuid}' is not in an allocation state.")
    elif matching_master.status == 'allocated':
        messages.error(request, f"UUID {new_uuid} is already allocated elsewhere.")
    else:
        try:
            if new_uuid not in sale_order_product.uuids and new_uuid not in sale_order.uuids:
                new_master = Master.objects.get(uuid=new_uuid)
                print(new_master.status)
                new_master.status = "allocated"
                print(new_master.status)
                new_master.save()
                sale_order_product.uuids.append({new_uuid: None})
                
                material_code = sale_order_product.product.MaterialCode
                
                if material_code not in sale_order.uuids:
                    sale_order.uuids[material_code] = {}

                quantity_per_box = matching_master.quantity_per_box
                sale_order.uuids[material_code][new_uuid] = quantity_per_box
                sale_order.save()
                
                print(f"Material data updated: {sale_order.uuids[material_code]}")
                remaining_quantity -= 1  # Decrement remaining quantity
                
                print(f"Remaining quantity updated: {remaining_quantity}")
            else:
                messages.error(request, f"UUID '{new_uuid}' is already added. Skipping.")
        except Exception as e:
            messages.error(request, str(e))
    
    # Save remaining quantity regardless of success or failure
    sale_order_product.remaining_quantity = remaining_quantity
    sale_order_product.save()

def save_and_return(request, order_no, MaterialCode):
    sale_order = get_object_or_404(SaleOrder, order_no=order_no)
    sale_order_product = get_object_or_404(
        SaleOrderProduct, product__MaterialCode=MaterialCode, sale_order=sale_order)
    print(f"SALE ORDER PRODUCT: {sale_order_product}")

    appended_data = {
        "added_by": request.user.username,
        "added_date_time": timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
        "order_no": sale_order.order_no,
        "Veichal_no": sale_order.vehicle_no,
        "po_number": sale_order.po_number,
    }

    if sale_order_product:
        for uuid in sale_order_product.uuids:
            if MaterialCode not in sale_order.uuids:
                sale_order.uuids[MaterialCode] = []  # Initialize the list if it doesn't exist

            sale_order.uuids[MaterialCode].append(uuid)  # Append each uuid to the list
            print(f"UUID added: {uuid}")

            master = Master.objects.filter(uuid=uuid, status='active').first()

            if master is not None:
                master_data = master.data_json or {}
                outlet_data = master_data.get('outlet', {})
                outlet_data[order_no] = appended_data
                master_data['outlet'] = outlet_data

                master.data_json = master_data
                master.save()

        sale_order.save()

        # Check conditions for marking sale_order_product as complete
        if sale_order_product.product.is_insert:
            if sale_order_product.remaining_quantity == 0 and sale_order_product.holding_quantity == 0:
                sale_order_product.status = 'complete'
                sale_order_product.save()
        else:
            if sale_order_product.quantity == len(sale_order_product.uuids):
                sale_order_product.status = 'complete'
                sale_order_product.save()

        # Check if all sale_order_products are complete to mark sale_order as complete
        if sale_order.saleorderproduct_set.filter(status='complete').count() == sale_order.saleorderproduct_set.count():
            with transaction.atomic():
                sale_order.status = 'complete'
                sale_order.save()
                messages.success(request, 'SaleOrder Marking successful.')
    else:
        messages.error(request, 'SaleOrderProduct not found.')

    return redirect('sale_order_detail', order_no=order_no)


def remove_uuid(request, order_no, sale_order_product_id):
    if request.method == 'POST':
        removed_uuid = request.POST.get('removed_uuid')
        sale_order = get_object_or_404(SaleOrder, order_no=order_no)
        sale_order_product = get_object_or_404(
            SaleOrderProduct, product_id=sale_order_product_id, sale_order=sale_order)

        if removed_uuid in sale_order_product.uuids:
            try:
                sale_order_product.uuids.remove(removed_uuid)
                specific_master = sale_order_product.product.master_set.filter(
                    uuid=removed_uuid).first()

                if specific_master:
                    master_data = specific_master.data_json or {}
                    outlet_data = master_data.get('outlet', {})

                    if order_no in outlet_data:
                        del outlet_data[order_no]

                    master_data['outlet'] = outlet_data
                    specific_master.data_json = master_data
                    specific_master.status = 'active'
                    if removed_uuid in sale_order.uuids:
                        sale_order.uuids.remove(removed_uuid)
                        sale_order.save()
                    sale_order_product.status = 'pending'
                    print(specific_master.save())
                    print(sale_order_product.save())
            except Exception as e:
                messages.warning(request, f"Failed To Remove ID \nError: {e} ")

    return redirect('sale_order_product_detail', order_no=order_no, sale_order_product_id=sale_order_product_id)


def out_verification(request):
    if request.method == 'POST':
        group_id = request.POST.get('group_id')

        if not group_id:
            messages.error(request, 'Group ID not provided')
            return redirect('out_verification')
        group_id_numeric = group_id.split(
            '-')[1] if '-' in group_id else group_id
        try:
            group_id_numeric = int(group_id_numeric)
        except ValueError:
            messages.error(request, 'Invalid group ID format')
            return redirect('out_verification')
        group = SaleOrderGroup.objects.filter(
            group_id=group_id_numeric).first()
        if group.status == 'recived' or group.status == 'dispatched':
            messages.error(request, f'Group Already {group.status}')
            return redirect('out_verification')
        if group.vehicle == None:
            messages.error(request, f'Veichal Not Assigned yet for this Group')
            return redirect('out_verification')

        else:
            sale_orders = SaleOrder.objects.filter(group_id=group_id_numeric)

            if not sale_orders.exists() or any(order.status != 'complete' for order in sale_orders):
                messages.error(request, f'Not all sale orders in group {group_id} are in the "complete" state. Cannot Proceed')
                return redirect('out_verification')
            elif any(not order.invoice_no for order in sale_orders):
                messages.error(request, f'Waiting For invoice No. To be Generated. Cannot Proceed')
                return redirect('out_verification') 

        context = {
            'sale_orders': sale_orders,
            'group_id': group_id_numeric,
        }

        return render(request, 'out_verification.html', context)

    return render(request, 'out_verification.html')


# def out_verification(request):
#     if request.method == 'POST':
#         tracking_id = request.POST.get('tracking_id')

#         if not tracking_id:
#             messages.error(request, 'Tracking ID not provided')
#             return redirect('out_verification')

#         vehicle_sale_order_group = get_object_or_404(VehicleSaleOrderGroup, tracking_id=tracking_id)
#         sale_order_groups = vehicle_sale_order_group.order_groups.all()

#         # Check if any sale order in any group is not in 'complete' state
#         for sale_order_group in sale_order_groups:
#             incomplete_sale_orders = sale_order_group.sale_orders.filter(status__in=['pending', 'queue_for_out'])
#             if incomplete_sale_orders.exists():
#                 messages.error(request, f"Some sale orders in group {sale_order_group.group_id} are not in 'complete' state")
#                 return redirect('out_verification')

#         context = {
#             'tracking_id': tracking_id,
#             'sale_order_groups': sale_order_groups,
#         }

#         return render(request, 'out_verification.html', context)

#     return render(request, 'out_verification.html')

def done_verification(request, group_id):
    try:
        master_count = 0
        so = {}
        sale_orders = SaleOrder.objects.filter(group_id=group_id)
        group = SaleOrderGroup.objects.get(group_id=group_id)

        vehicle = group.vehicle

        for sale_order in sale_orders:
            so[sale_order.order_no] = True
            if sale_order.status == 'out':
                messages.error(
                    request, f'SaleOrder {sale_order.order_no} is already marked as out')
            elif sale_order.status == 'complete':
                with transaction.atomic():
                    sale_order.status = 'out'
                    for sale_order_product in sale_order.saleorderproduct_set.all():
                        sale_order_product.status = 'complete'
                        # sale_order_product.save()
                        masters = Master.objects.filter(
                            uuid__in=sale_order_product.uuids)
                        masters.update(status='deactive')
                        for master in masters:
                            master_data = master.data_json or {}
                            outlet_data = master_data.get('outlet', {})
                            outlet_data[sale_order.order_no] = {
                                'vehicle': vehicle,
                                'out_time': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'out_verified_by': str(request.user),
                            }
                            master_data['outlet'] = outlet_data
                            master.data_json = master_data
                            # master.save()
                            master_count += 1
            else:
                messages.warning(
                    request, f'SaleOrder {sale_order.order_no} is not complete. Check all products added.')

        # Update group status and master_count
        try:
            group.status = "dispatched"
            group.master_count = master_count
            group.save()

            # Update vehicle attributes
            # vehicle.on_path = True
            # vehicle.current_destination = group.destination
            # vehicle.driver_name = group.driver_name
            # vehicle.status = "dispatched"
            # ongoing_status_data = vehicle.ongoing_status or {}
            # ongoing_status_data['dispatch'] = timezone.now().strftime(
            #     '%Y-%m-%d %H:%M:%S')
            # vehicle.ongoing_status = ongoing_status_data
            # so_data = vehicle.current_carrying or {}
            # so_data[group_id] = so  # corrected assignment
            # vehicle.current_carrying = so_data
            # vehicle.save()

            vehicle_sale_order_group = VehicleSaleOrderGroup.objects.filter(order_groups__pk=group_id).first()
            vehicle_type = vehicle_sale_order_group.TransporterName
            print(vehicle_type)
            print(group.status)
            print(vehicle_sale_order_group.tracking_id)
            print(vehicle_sale_order_group)
            if vehicle_sale_order_group:
                all_verified = all(
                    group.status == 'dispatched' for group in vehicle_sale_order_group.order_groups.all())
                for group in vehicle_sale_order_group.order_groups.all():
                    print(group)
                print(f"ALL VERIFIED : {all_verified}")
                if all_verified:
                    TransporterName = vehicle_sale_order_group.TransporterName
                    print(f"TRANSPORTER NAME : {TransporterName}")
                    if vehicle_type == 'OWN VEHICLE':
                        vehicle = Vehicle.objects.filter(vehicle_number=vehicle)
                        ongoing_status_data = vehicle.ongoing_status or {}
                        dispatch_info = {
                            'dispatch_time': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'verified_by': str(request.user),
                            'user_ip': request.META.get('REMOTE_ADDR', None)
                        }
                        ongoing_status_data['Dispatched'] = dispatch_info
                        vehicle.ongoing_status = ongoing_status_data
                        vehicle.on_path = True
                        vehicle.current_destination = group.destination
                        vehicle.driver_name = group.driver_name
                        vehicle_sale_order_group_data_json = json.loads(
                            vehicle_sale_order_group.data_json) if vehicle_sale_order_group.data_json else {}
                        vehicle_sale_order_group_data_json['Dispatched'] = dispatch_info
                        vehicle_sale_order_group.data_json = json.dumps(
                            vehicle_sale_order_group_data_json)
                    # vehicle_sale_order_group.save()
                    # vehicle.save()
                    all_data = []
                    print(f"vehicle_sale_order_group : {vehicle_sale_order_group}")
                    sale_order_groups = vehicle_sale_order_group.order_groups.all()
                    print(f"sale_order_groups : {sale_order_groups}")
                    for vehicle_group in sale_order_groups:
                        print(f"groups : {vehicle_group}")
                        data = {
                            'PackingSlipNo': vehicle_group.group_id,
                            'TrackingId': vehicle_sale_order_group.tracking_id,
                            # 'products_count': vehicle_group.master_count,
                            'TransportId': '1010000002' if TransporterName == 'dtdc' else '1010000001',
                            'VehicleNo': vehicle_group.vehicle if vehicle_group.vehicle else None,
                            'OrderSummary': [],
                        }
                        for sale_order in vehicle_group.sale_orders.all():
                            for material, material_data in sale_order.uuids.items():
                                uid_list = []
                                for uid, quantity in material_data.items():
                                    uid_info = {
                                        "Uid": uid,
                                        "Quantity": quantity
                                    }
                                    uid_list.append(uid_info)
                                
                                sale_order_data = {
                                    'OrderNo': str(sale_order.order_no),
                                    "AmendNo": 0,
                                    "MaterialCode": material,
                                    'Quantity': len(material_data),
                                    'UIds': uid_list,
                                }
                                data['OrderSummary'].append(sale_order_data)

                        all_data.append(data)
                        print(f"ALL DATA :: {all_data}")
                    with open('group_res.json', 'w') as json_file:
                        json.dump(all_data, json_file, indent=4)
                        messages.success(request, 'Marking successful.')
                    messages.success(request, 'Veichal Dispatched successful.')
        except Exception as e:
            messages.error(request, f'ERROR done_verification: {e}')

    except Exception as e:
        messages.error(request, f'An error occurred: {e}')
        print(e)

    return render(request, 'out_verification.html')


# def create_sale_order_group(request):
#     if request.method == 'POST':
#         selected_sale_orders = request.POST.getlist('selected_sale_orders')
#         if not selected_sale_orders:
#             messages.error(request, f'Select at least one Sale Order')
#         else:
#             existing_groups = SaleOrderGroup.objects.aggregate(Max('group_id'))['group_id__max']
#             new_group_id = existing_groups + 1 if existing_groups is not None else 1
#             new_group = SaleOrderGroup.objects.create(group_id=new_group_id)
#             SaleOrder.objects.filter(
#                 order_no__in=selected_sale_orders, group_id=None).update(group_id=new_group)
#             # Redirect after processing POST data
#             return redirect('sale_order_group_detail', new_group_id)
#     else:
#         # Fetch units for the initial render
#         units = Unit.objects.all()
#         form = UnitFilterForm(request.POST or None)
#         sale_orders_without_group = SaleOrder.objects.filter(
#             Q(status='complete') | Q(status='pending'), group_id=None)
#         # Apply unit filter if form is submitted
#         if form.is_valid():
#             selected_unit = form.cleaned_data['unitFilter']
#             if selected_unit:
#                 sale_orders_without_group = sale_orders_without_group.filter(unit=selected_unit)
#         sale_order_groups = SaleOrderGroup.objects.all()
#         context = {
#             'form': form,
#             'sale_orders': sale_orders_without_group,
#             'sale_order_groups': sale_order_groups,
#             'units': units,
#         }
#         return render(request, 'sale_order_group.html', context)


def create_sale_order_group(request):
    units = Unit.objects.all()
    form = UnitFilterForm(request.POST or None)
    sale_orders_without_group = SaleOrder.objects.filter(
        Q(status='complete') | Q(status='pending'), group_id=None)
    sale_order_groups = SaleOrderGroup.objects.all()

    if request.method == 'POST':
        form = UnitFilterForm(request.POST)
        if form.is_valid():
            selected_unit = form.cleaned_data['unitFilter']
            if selected_unit:
                sale_orders_without_group = sale_orders_without_group.filter(
                    unit=selected_unit.name)

            context = {
                'form': form,
                'sale_orders': sale_orders_without_group,
                'sale_order_groups': sale_order_groups,
                'units': units,
            }
            return render(request, 'sale_order_group.html', context)
    else:
        return render(request, 'sale_order_group.html', {'form': form, 'sale_orders': sale_orders_without_group, 'sale_order_groups': sale_order_groups, 'units': units})


def create_group_for_selected_orders(request):
    if request.method == 'POST':
        selected_sale_orders = request.POST.getlist('selected_sale_orders')
        if not selected_sale_orders:
            messages.error(request, 'Select at least one Sale Order')
        else:
            # Check if any selected sale order already has a group_id assigned
            sale_orders_with_group = SaleOrder.objects.filter(
                order_no__in=selected_sale_orders, group_id__isnull=False
            ).exists()
            
            if sale_orders_with_group:
                messages.error(
                    request, 'One or more selected sale orders already belong to a group.'
                )
            else:
                selected_units = SaleOrder.objects.filter(
                    order_no__in=selected_sale_orders).values('unit').annotate(count=Count('id'))
                if len(selected_units) > 1:
                    messages.error(
                        request, 'Selected sale orders belong to different units. Please select sale orders from the same Company.')
                else:
                    selected_unit_name = selected_units[0]['unit']
                    try:
                        selected_unit = Unit.objects.get(name=selected_unit_name)
                    except Unit.DoesNotExist:
                        messages.error(
                            request, f'Selected unit "{selected_unit_name}" does not exist.')
                    else:
                        existing_groups = SaleOrderGroup.objects.aggregate(Max('group_id'))[
                            'group_id__max']
                        new_group_id = existing_groups + 1 if existing_groups is not None else 1
                        new_group = SaleOrderGroup.objects.create(
                            group_id=new_group_id, unit=selected_unit_name, destination=selected_unit.address)
                        try:
                            SaleOrder.objects.filter(
                                order_no__in=selected_sale_orders, group_id=None).update(group_id=new_group)
                        except Exception as e:
                            messages.error(
                                request, f'An error occurred while creating the group: {str(e)}')
                            print(e)
                            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                        else:
                            messages.success(
                                request, f'Group created successfully with ID: {new_group_id}')
                            return redirect('sale_order_group_detail', new_group_id)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def sale_order_group_detail(request, group_id):
    sale_orders_in_group = SaleOrder.objects.filter(group_id=group_id)
    sale_order_group = get_object_or_404(SaleOrderGroup, group_id=group_id)
    group_ids = group_id
    g_id = 'G-' + str(group_ids)
    error_message = ""
    generate_qr_code = True
    vehicles = Vehicle.objects.all()
    all_sale_orders_complete = all(
        sale_order.status == 'complete' for sale_order in sale_orders_in_group)
    if all_sale_orders_complete:
        sale_order_group.status = "complete"
        sale_order_group.save()
    selected_vehicle = sale_order_group.vehicle

    if request.method == 'POST':
        if 'delete_group' in request.POST:
            delete_group_and_associated_data(group_id)
            return JsonResponse({'success': True})

        vehicle_no = request.POST.get('vehicle_no')
        if vehicle_no:
            final_vehicle = get_object_or_404(
                Vehicle, vehicle_number=vehicle_no)
        else:
            final_vehicle = sale_order_group.vehicle

        driver_name = request.POST.get(
            'vehicle_driver_name', sale_order_group.driver_name)
        destination = request.POST.get(
            'destination', sale_order_group.destination)

        sale_orders = SaleOrder.objects.filter(group_id=group_id)
        for sale_order in sale_orders:
            sale_order.vehicle_no = vehicle_no
            sale_order.driver_name = driver_name
            sale_order.destination = destination
            sale_order.save()

        sale_order_group.vehicle = final_vehicle
        sale_order_group.driver_name = driver_name
        sale_order_group.destination = destination
        sale_order_group.save()

    # Check the flag before generating the QR code
    qr_code_data = None
    encoded_qr_code_data = None
    if generate_qr_code:
        qr_code_data = single_qr(str(g_id), dotted_style=True)
        encoded_qr_code_data = base64.b64encode(qr_code_data).decode()

    return render(request, 'sale_order_group_detail.html', {
        'sale_orders_in_group': sale_orders_in_group,
        'group_id': group_ids,
        'qr_code': encoded_qr_code_data,
        'sale_order_group': sale_order_group,
        'error_message': error_message,
        'vehicles': vehicles,
        'selected_vehicle': selected_vehicle,
        'all_sale_orders_complete': all_sale_orders_complete,
    })


def delete_sale_order_group(request, group_id):
    sale_order_group = get_object_or_404(SaleOrderGroup, group_id=group_id)

    if request.method == 'POST':
        for sale_order in sale_order_group.sale_orders.all():
            sale_order.group_id = None
            sale_order.vehicle_no = None
            sale_order.save()
        sale_order_group.delete()

        return redirect('create_sale_order_group')

    return render(request, 'delete_sale_order_group.html', {'sale_order_group': sale_order_group})


def generate_short_id():
    uuid_str = str(uuid.uuid4())
    short_id = uuid_str.replace("-", "")[:7]
    month_name = calendar.month_name[datetime.datetime.now().month][:3]
    final_id = f"{month_name}{short_id}"
    return final_id


def veichal_allocation(request):
    if request.method == 'POST':
        selected_groups = request.POST.getlist('selected_groups')
        print(f"Selected groups: {selected_groups}")
        try:
            with transaction.atomic():
                # vehicle_sale_order_group, created = VehicleSaleOrderGroup.objects.get_or_create(tracking_id=generate_short_id(), data_json={})
                vehicle_sale_order_group = VehicleSaleOrderGroup.objects.create(
                    tracking_id=generate_short_id(), data_json={})

                print(f"TRACKING ID : {vehicle_sale_order_group.tracking_id}")

                if vehicle_sale_order_group is None:
                    raise ValueError("Failed to create VehicleSaleOrderGroup")
                routes = {}
                for group_id in selected_groups:
                    group = SaleOrderGroup.objects.get(group_id=int(group_id))
                    group.allocated = True
                    group.tracking_id = vehicle_sale_order_group.tracking_id
                    group.save()
                    vehicle_sale_order_group.order_groups.add(group)
                    routes[group.unit] = False
                vehicle_sale_order_group.data_json['routes'] = routes
                vehicle_sale_order_group.save()

                messages.success(
                    request, f"Sale Order Groups added to Vehicle Sale Group")
                return redirect('veichal_allocation_details', tracking_id=vehicle_sale_order_group.tracking_id)
        except Exception as e:
            print("VEICHAL ALLOCATION EXCEPTION", e)
            return redirect('veichal_allocation')
    else:
        groups = SaleOrderGroup.objects.filter(
            status='complete', vehicle=None, allocated=False)
        context = {'groups': groups}
        return render(request, 'veichal_allocation.html', context)


def veichal_allocation_details(request, tracking_id):
    try:
        vehicles = Vehicle.objects.filter(on_path=False)
        vh = VehicleSaleOrderGroup.objects.get(tracking_id=tracking_id)
        if isinstance(vh.data_json, str):
            data_json = json.loads(vh.data_json)
            routes = data_json.get('routes', {})
        else:
            routes = vh.data_json.get('routes', {})

        if request.method == 'POST':
            vehicle_id = None
            print(f"REQUEST L {request.POST}")
            vehicle_type = request.POST.get('vehicle_type')
            print(f"TYPE : {vehicle_type}")
            if vehicle_type == 'dtdc':
                vehicle_id = request.POST.get('dtdc_vehicle_no')
                driver_name = request.POST.get('vehicle_driver_name')
            elif vehicle_type == 'own_vehicle':
                print("IN OWN VEICHAL MAIN")
                vehicle_id = request.POST.get('vehicle_no')
                driver_name = request.POST.get('vehicle_driver_name')

            if vehicle_id:
                if vehicle_type == 'own_vehicle':
                    print("IN OWN VEICHAL")
                    try:
                        vehicle = Vehicle.objects.get(id=vehicle_id)
                        vehicle_id = vehicle.vehicle_number
                    except Exception as e:
                        print("EXCEPTION IN VEICHAL ALLOCATION  : {e}")
                    print(vehicle)
                else:
                    print("NOT IN OWN VEICHAL")
                    vehicle = vehicle_id
                vh.vehicle = vehicle_id
                vh.TransporterName = vehicle_type
                print(vh.vehicle , vh.TransporterName)
                vh.save()
                sog = {}
                try:
                    for sale_order_group in vh.order_groups.all():
                        if not sale_order_group.vehicle:
                            if tracking_id not in sog:
                                sog[tracking_id] = []
                            sog[tracking_id].append(sale_order_group.group_id)
                            print(sog)
                            sale_order_group.driver_name = driver_name
                            sale_order_group.vehicle = vehicle_id
                            # sale_order_group.destination = unit.address
                            sale_order_group.save()

                    # Update SaleOrders within the SaleOrderGroup
                    print(f"SOG : {sog}")
                    for sale_order in sale_order_group.sale_orders.all():
                        sale_order.vehicle_no = vehicle_id
                        sale_order.driver_name = driver_name
                        # sale_order.destination = unit.address
                        sale_order.save()
                except Exception as e:
                    print(f"EXCEPTION : {e}")
                try:
                    current_time = timezone.now()
                    data_json = {
                        "SaleOrderGroup_id": sog,
                        "driver_name": driver_name,
                        "TransporterName":vehicle_type,
                        # "current_destination": unit.address,
                        # Add other relevant information here
                    }
                    if vehicle_type == 'own_vehicle':
                        vehicle.on_path = True
                        vehicle.driver_name = driver_name
                        vehicle.current_carrying = sog  # Assuming vh.id is the SaleOrderGroup number
                        vehicle.state = "Allocated"
                        vehicle.ongoing_status = {
                            "Allocated": {
                                "allocated_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                                "status": "Allocated",
                                # "company name": unit.name,
                                # "current_destination": unit.address
                            },
                            "Dispatched": {},
                            "Reached": {},
                            "Returned": {},
                            "Total_time": {}
                        }
                        vehicle.data_json = json.dumps(data_json)
                        vehicle.save()
                    vh.data_json = json.dumps(data_json)
                    vh.save()
                except Exception as e:
                    messages.error(
                        request, f'Error In Veichal Allocation. {e}')

                messages.success(
                    request, 'Vehicle successfully assigned to all associated SaleOrderGroups.')
                return redirect('veichal_allocation_details', tracking_id=tracking_id)

        context = {'vehicles': vehicles, 'vh': vh, 'routes': routes}
        return render(request, 'veichal_allocation_details.html', context)

    except VehicleSaleOrderGroup.DoesNotExist:
        messages.error(request, 'Vehicle Sale Order Group does not exist.')
        return redirect('veichal_allsale_order_group_historyocation')

    except Vehicle.DoesNotExist:
        messages.error(request, 'Selected vehicle does not exist.')
        return redirect('sale_order_group_history')

    # except Unit.DoesNotExist:
    #     messages.error(request, 'Unit does not exist.')
    #     return redirect('veichal_allocation_details', id=id)

    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('veichal_allocation')


def veichal_allocation_history(request):
    all_vehicle_sale_orders = VehicleSaleOrderGroup.objects.all()
    return render(request, 'veichal_allocation_history.html', {'all_vehicle_sale_orders': all_vehicle_sale_orders})