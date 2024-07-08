from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from inlet.models import ProductIndex, Master, Product
from django.contrib import messages
from .forms import *
from outlet.models import SaleOrder
from inlet.models import Master
from .models import *
from outlet.models import SaleOrder, SaleOrderGroup
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
import json
from .utitliy import *

# TODO: Add Unless Returen NOt Requision Scan For New UUIds

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required(login_url='managment/login/')
def home(request):
    unit = request.user.unit
    requisitions = Requisition.objects.filter(
        machine__unit=unit, is_completed=False)
    context = {'object_list': unit, 'requisitions': requisitions}
    return render(request, 'home.html', context)


@login_required(login_url='managment/login/')
def requisitions_history(request):
    unit = request.user.unit
    requisitions = Requisition.objects.filter(machine__unit=unit)
    context = {'object_list': unit, 'requisitions': requisitions}
    return render(request, 'requisitions_history.html', context)


@login_required(login_url='managment/login/')
def units_inlet_input(request):
    if request.method == 'POST':
        unit_name = request.user.unit
        group_id = request.POST.get('group_id')
        if not group_id:
            messages.error(request, 'Group ID not provided')
            return redirect('units_inlet_input')

        group_id_numeric = group_id.split(
            '-')[1] if '-' in group_id else group_id
        try:
            group_id_numeric = int(group_id_numeric)
        except ValueError:
            messages.error(request, 'Invalid group ID format')
            return redirect('units_inlet_input')
        try:
            group = SaleOrderGroup.objects.get(group_id=group_id_numeric)
        except SaleOrderGroup.DoesNotExist:
            messages.error(
                request, f'No sale orders found for group ID {group_id}')
            return redirect('units_inlet_input')
        if group.status == 'enterd_in_unit' or group.status == 'recived':
            messages.error(
                request, 'Unverified Group QR Scanned Actions Reported To Admins')
            return redirect('units_inlet_input')
        if group.status != 'dispatched':
            messages.error(
                request, 'Unverified Group QR Scanned Actions Reported To Admins')
            return redirect('units_inlet_input')

        if group.unit != unit_name:
            messages.error(request, 'This Group Not Belong To This unit Reported To Admins')
            return redirect('units_inlet_input')
        return redirect('units_inlet_group', group_id=group_id_numeric)

    else:
        return render(request, 'units_inlet_input.html')

        #    for sale_order_product in sale_order.saleorderproduct_set.all():
        #         masters = Master.objects.filter(uuid__in=sale_order_product.uuids)
        #         for master in masters:
        #             unit_instance = get_object_or_404(Unit, name=request.user.unit)
        #             master.unit = unit_instance
        #             print(unit_instance)
        #             master.unit_status = f'{request.user.unit} - in'

        #             master_data = master.data_json or {}
        #             unit_data = master_data.get('units', {})
        #             unit_data[request.user.unit] = {
        #                 'group_id': group_id,
        #                 'units_status': master.unit_status,
        #             }
        #             master_data['units'] = unit_data
        #             master.data_json = master_data

        #             master.save()


def accept_or_reject_all(request, uuid, action):
    sale_order = get_object_or_404(SaleOrder, uuid=uuid)

    if not sale_order:
        messages.error(request, "No sale order found")
        return redirect('units_inspection')

    masters = Master.objects.filter(uuid__in=sale_order.uuids)

    if action == 'accept':
        unit_instance = get_object_or_404(Unit, name=request.user.unit)
        for master in masters:
            master.unit = unit_instance
            master.unit_status = f'{request.user.unit} - in'
            master.save()
        sale_order.status = 'recived'
        sale_order.save()

        messages.success(request, "Accepted successfully")
    elif action == 'reject':
        masters.update(unit=None, unit_status='rejected')
        messages.success(request, "Rejected ")

    return redirect('units_inspection')


def indivisual_inspection(request, uuid):
    unit_instance = get_object_or_404(Unit, name=request.user.unit)
    if request.method == 'POST':
        sale_order = get_object_or_404(SaleOrder, uuid=uuid)
        for sale_order_product in sale_order.saleorderproduct_set.all():
            uuids = sale_order_product.uuids
            uuid_value = request.POST.get(
                'uuid_' + sale_order_product.product.name)
            print(f'uuid_value  :  {uuid_value}')
            input_field_name = f"uuid_{sale_order_product.product.name}"
            print(f'input_field_name : {input_field_name}')
            entered_uuid = request.POST.get(input_field_name)
            print(f'ENTERD UUID  : {entered_uuid}')
            if entered_uuid in uuids:
                with transaction.atomic():
                    sale_order_product.verified_uuids.append(entered_uuid)
                    sale_order_product.uuids.remove(entered_uuid)
                    sale_order_product.save()
                    master = Master.objects.get(uuid=entered_uuid)
                    master.unit = unit_instance
                    master.unit_status = f'{request.user.unit} - in'
                    master.save()

                messages.success(request, f"Verifide.")
                return redirect('indivisual_inspection', uuid)
            else:
                messages.error(
                    request, f"Invalid UUID for {sale_order_product.product.name}.")
                return redirect('indivisual_inspection', uuid)
        if all(len(product.uuids) == 0 for product in sale_order.saleorderproduct_set.all()):
            sale_order.saleorderproduct_set.update(status='complete')
            if all(product.status == 'complete' for product in sale_order.saleorderproduct_set.all()):
                sale_order.status = 'verified'
                sale_order.save()
    sale_order = get_object_or_404(SaleOrder, uuid=uuid )
    products_with_count = []

    for sale_order_product in sale_order.saleorderproduct_set.all():
        uuids = sale_order_product.uuids
        verified_uuids = sale_order_product.verified_uuids
        master_count = len(uuids)
        verified_masters_count = len(verified_uuids)
        products_with_count.append({'product': sale_order_product.product,
                                   'master_count': master_count, 'verified_masters_count': verified_masters_count})

    return render(request, 'indivisual_inspection.html', {'products_with_count': products_with_count, 'sale_order': sale_order, })


@login_required(login_url='managment/login/')
def units_inlet(request, group_id):
    unit = request.user.unit
    group_id_numeric = int(group_id)
    group = SaleOrderGroup.objects.get(group_id=group_id)
    sale_orders = SaleOrder.objects.filter(group_id=group_id_numeric)
    sale_orders_count = sale_orders.count()
    products_count = group.master_count
    # masters_count = sum(order.products.aggregate(total_masters=models.Count('master'))['total_masters'] for order in sale_orders)
    context = {
        'unit': unit,
        'sale_orders': sale_orders,
        'sale_orders_count': sale_orders_count,
        'products_count': products_count,
        # 'masters_count': masters_count,
        'group_id': group_id_numeric,
    }
    return render(request, 'units_inlet.html', context)


def mark_sale_order_checked(request):
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        uuid = request.POST.get('uuid')

        try:
            sale_order = SaleOrder.objects.get(group_id=group_id, uuid=uuid)
            sale_order.checked = True
            sale_order.checked_by = request.user
            sale_order.status = 'checked_at_gate'
            masters = Master.objects.filter(uuid__in=sale_order.uuids)
            unit_instance = get_object_or_404(Unit, name=request.user.unit)
            current_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            verified_by = str(request.user)
            for master in masters:
                master_data = master.data_json or {}
                unit_data = {
                    'unit': request.user.unit,
                    'reach_time': current_time,
                    'verified_by': verified_by
                }
                master_data['unit'] = unit_data
                master.data_json = master_data
                master.unit = unit_instance
                master.unit_status = f'{request.user.unit} - in'
                master.save()
            sale_order.save()

            # Check if all sale orders in the group are 'checked_at_gate'
            all_checked = SaleOrder.objects.filter(group_id=group_id).exclude(status='checked_at_gate').count() == 0

            if all_checked:
                group = SaleOrderGroup.objects.get(group_id=group_id)
                group.status = 'enterd_in_unit'
                group.save()
                messages.success(
                    request, f"All sale orders in the group marked as checked. Group status updated.")
                return redirect('units_inlet_input')
            else:
                messages.success(
                    request, f"Sale order with UUID {uuid} marked as checked.")
        except SaleOrder.DoesNotExist:
            messages.error(
                request, f"Sale order with UUID {uuid} not found in the group.")

        return redirect('units_inlet_group', group_id=group_id)
    else:
        return redirect('units_inlet_group', group_id=group_id)


@login_required(login_url='managment/login/')
def units_done_verification(request, group_id):
    try:
        sale_orders = SaleOrder.objects.filter(group_id=group_id)
        group = SaleOrderGroup.objects.filter(group_id=group_id)

        try:
            for sale_order in sale_orders:
                if sale_order.status == 'recived':
                    messages.error(
                        request, f'SaleOrder {sale_order.bill_no} is already marked as recived')
                elif sale_order.status == 'verified_at_gate':
                    messages.error(
                        request, f'SaleOrder {sale_order.bill_no} is already Verified At Gate')
                elif sale_order.status == 'out':
                    with transaction.atomic():
                        sale_order.status = 'verified_at_gate'
                        sale_order.checked = True
                        sale_order.save()

                        messages.success(
                            request, f'SaleOrder {sale_order.bill_no} verified successful.')

                elif sale_order.status == 'complete':
                    messages.error(
                        request, f'Unverified Group QR Scanned Actions Reported To Admin')
                else:
                    messages.warning(
                        request, f'SaleOrder {sale_order.bill_no} {unit_instance} is not complete. Check all products added.')
            group.update(status="enterd_in_unit")
            messages.success(request, f'Group Marking Successful')
            return redirect('units_inlet_input')

        except Exception as e:
            messages.error(request, f'Error : {e}')
        return render(request, 'units_inlet.html')

    except Exception as e:
        messages.error(request, f'An error occurred: {e} ')
        return render(request, 'units_inlet.html')

@login_required(login_url='managment/login/')
def units_inspection(request):
    current_user_unit = request.user.unit
    sale_orders = SaleOrder.objects.filter(
        unit=current_user_unit, status='checked_at_gate')
    return render(request, 'units_inspection.html', {'sale_orders': sale_orders})


@login_required(login_url='managment/login/')  # Ensure user is authenticated
def units_inspection_saleorder_list(request):
    unit = request.user.unit  # Get the current user's unit
    sale_orders = SaleOrder.objects.filter(
        unit=unit, status='checked_at_gate')  # Retrieve sale orders for the unit
    context = {
        'unit': unit,
        'sale_orders': sale_orders,
    }
    return render(request, 'units_inspection_saleorder_list.html', context)


@login_required(login_url='managment/login/')
def units_inventory(request):
    try:
        unit_masters = Master.objects.filter(unit=request.user.unit)
        product_data = []

        for product_name in set(master.product.name for master in unit_masters):
            product_masters = unit_masters.filter(product__name=product_name)
            product_data.append({
                'product_name': product_name,
                'masters_count': product_masters.count(),
            })

        context = {
            'unit': request.user.unit,
            'product_data': product_data,
        }

        return render(request, 'units_inventory.html', context)
    except Exception as e:
        messages.error(request, f'An error occurred: {e} ')
        return render(request, 'units_inventory.html')
    return render(request, 'units_inventory.html')


@login_required(login_url='managment/login/')
def units_product(request, product_name):
    try:
        unit_masters = Master.objects.filter(
            unit=request.user.unit, product__name=product_name)
        context = {
            'product_name': product_name,
            'unit_masters': unit_masters,
        }

        return render(request, 'units_product.html', context)
    except Exception as e:
        messages.error(request, f'An error occurred: {e} ')
        return render(request, 'units_inventory.html')


@login_required(login_url='managment/login/')
def unit_machines(request):
    unit = request.user.unit
    machines = Machine.objects.filter(unit=unit)
    context = {
        'unit': unit,
        'machines': machines,
    }
    return render(request, 'unit_machines.html', context)


@login_required(login_url='managment/login/')
def unit_requisitions(request):
    unit = request.user.unit
    requisitions = Requisition.objects.filter(machine__unit=unit)
    context = {
        'unit': unit,
        'requisitions': requisitions,
    }
    return render(request, 'user_unit_requisitions.html', context)


# TODO: IMpliment next Logic for Form And Scrap and Resharp
# TODO: Add Lofic For zero Resharp and scrap or one of them

def master_allocation(request, requisition_id):
    requisition = get_object_or_404(Requisition, req_no=requisition_id)
    # Accessing RequisitionProduct instances associated with the Requisition
    requisition_products = requisition.requisitionproduct_set.all()

    context = {
        'requisition_products': requisition_products,
        'requisition': requisition, 
    }
    return render(request, 'master_allocation.html', context)


def requisition_product_detail(request, requisition_id, product_id):
    requisition = get_object_or_404(Requisition, req_no=requisition_id)
    product = get_object_or_404(Product, pk=product_id)
    requisition_product = get_object_or_404(
        RequisitionProduct, requisition=requisition, product=product)
    requisition_product_total_quantity = requisition_product.total_quantity
    machine = requisition.machine
    has_active_tools_for_product = Master.objects.filter( machine=machine.name, status = 'on_machine' , unit=request.user.unit , product=product).count()
    print(has_active_tools_for_product)
    # has_active_tools_for_product =3
    master_to_req_form = Master_To_req()
    old_uuid_form = OldUUIDForm()

    context = {
        'requisition': requisition,
        'product': product,
        'requisition_product': requisition_product,
        'has_active_tools_for_product': has_active_tools_for_product,
        'master_to_req_form': master_to_req_form,
        'old_uuid_form': old_uuid_form,
    }
    return render(request, 'requisition_product_detail.html', context)

# Master_To_req PRCESS
def process_master_allocation(request, requisition_id, product_id):
    if request.method == "POST":
        requisition = get_object_or_404(Requisition, req_no=requisition_id)
        product = get_object_or_404(Product, pk=product_id)
        requisition_product = get_object_or_404(
            RequisitionProduct, requisition=requisition, product=product)
        print(requisition_product.total_quantity)
        print(requisition_product.allocate_quantity)

        # Assuming 'uuids' is the field name in your form
        uuids_str = request.POST.get('uuids', '')
        uuids_list = [uuid_str.strip()
                      for uuid_str in uuids_str.split(',') if uuid_str.strip()]
    if requisition_product.allocate_quantity == requisition_product.total_quantity:
        messages.error(request, f'MAlready Added All Material No Action Performed.')
    else:
        if not uuids_list:
            return HttpResponseBadRequest("No UUIDs provided")
        for entered_uuid in uuids_list:
            process_uuid(request, entered_uuid, requisition, product_id)

        return redirect('product_detail', requisition_id=requisition_id, product_id=product_id)


def process_uuid(request, entered_uuid, requisition, product_id):
    try:
        product = Product.objects.get(pk=product_id)
        master = Master.objects.get(uuid=entered_uuid)
        requisition_product = get_object_or_404(
            RequisitionProduct, requisition=requisition, product=product)
        print(master)
        if master.unit != requisition.unit:
            messages.error(
                request, f'Master with UUID {entered_uuid} is not in the same unit as the requisition. Action Reported To Admin.')
        elif master.product != product:
            messages.error(
                request, f'Master with UUID {entered_uuid} is not {product.name}.')
        elif master.machine:
            messages.error(
                request, f'Master with UUID {entered_uuid} is on machine can not allocate.')
        elif master.status == 'dead' or master.status == 'on_machine' or master.unit_status != f'{request.user.unit} - in':
            messages.error(
                request, f'Master with UUID {entered_uuid} is not mactch Certain Condition action not allowed.')
        else:
            try:
                update_master_assignment(request, requisition, master)
                # update_master_status(master , recived)
                messages.success(
                    request, f'Successfully verified and added')
                requisition_product.allocate_quantity += 1
            except Exception as e:
                messages.error(
                    request, f'Error during Master or RequisitionProduct update: {e}')
    except Master.DoesNotExist:
        messages.error(
            request, f'Entered UUID {entered_uuid} does not match the requested product or is not on the specified machine.')


def update_master_assignment(request, requisition, master):
    try:
        allocation_date_iso = timezone.now().isoformat()
        print(allocation_date_iso)
        master.status = 'on_machine'
        master.unit_status = 'on_machine'
        master.machine = requisition.machine.name
        master.requisition = requisition.req_no
        master.machine_added_date = allocation_date_iso
        master_data = master.data_json or {}
        master_data['requisition_info'] = {
            'requisition_no': requisition.req_no,
            'quantity': requisition.quantity,
            'job': requisition.job,
            'operation': requisition.operation,
            'allocation_date': allocation_date_iso,
            'ip_address': get_client_ip(request),
        }
        master_data['machine_allocation'] = {
            'ip_address': get_client_ip(request),
            'allocated_by ': request.user.username,
            'machine_name': requisition.machine.name,
            'machine_added_date': allocation_date_iso,
        }
        try:
            master.data_json = master_data
            master.save()
            messages.success(
                request, f'Written data  : {master_data} ')
        except Exception as e:
            messages.error(
                request, f'ERROR IN MASTER DATA WRITING : {e} ')

    except Exception as e:
        messages.error(
            request, f'Entered UUID {master.uuid} has some Error\n Error : {e} ')

    try:
        allocation_date_iso = timezone.now().isoformat()
        tool_data = {
            'machine_name': requisition.machine.name,
            'allocation_date': allocation_date_iso,
            'ip_address': get_client_ip(request),
        }
        tool_data_json = json.dumps(tool_data)
        requisition.tool[str(master.uuid)] = tool_data_json
        requisition.save()
        machine_data = {
            'allocation_date': allocation_date_iso,
            'ip_address': get_client_ip(request),
        }
        machine_data_json = json.dumps(machine_data)

        machine = requisition.machine
        machine.active_tools[str(master.uuid)] = machine_data_json
        machine.save()
    except Exception as e:
        messages.error(request, f'Error In Machine Save State\n Error : {e} ')

# Master_To_req PRCESS END 





def update_requisition_product(request, requisition_product, uuid_type, entered_uuid):
    if uuid_type == 'break':
        requisition_product.break_uuid['uuids'].append(entered_uuid)
        requisition_product.added_break_quantity += 1
    elif uuid_type == 'resharp':
        requisition_product.resharp_uuid['uuids'].append(entered_uuid)
        requisition_product.added_resharp_quantity += 1
    requisition_product.save()


def update_master_status(master):
    master.status = 'dead'
    master.machine = None
    master.machine_remove_date = timezone.now()
    master.save()


def process_master_to_req_form(request, requisition, form):
    if form.is_valid():
        entered_uuids = form.cleaned_data['uuids']
        for entered_uuid in entered_uuids:
            process_master_assignment(request, requisition, entered_uuid)


def process_master_assignment(request, requisition, entered_uuid):
    try:
        master = Master.objects.get(
            uuid=entered_uuid, machine=None, product__in=requisition.products.all())

        if master.unit != requisition.unit:
            messages.error(
                request, f'Master with UUID {entered_uuid} is not in the same unit as the requisition. Action Reported To Admin.')
        elif master.machine is not None:
            messages.error(
                request, f'Master with UUID {entered_uuid} is already assigned to a machine.')
        else:
            update_master_assignment(request, requisition, master)
            if not Master.objects.filter(product__in=requisition.products.all(), machine=None).exists():
                requisition.is_completed = True
                requisition.save()
            messages.success(
                request, f'Successfully updated Master status for UUID: {entered_uuid}')
    except Master.DoesNotExist:
        messages.error(
            request, f'Entered UUID {entered_uuid} does not match the requested product or is already assigned to another machine.')


@login_required(login_url='managment/login/')
def machine_details(request, name):
    machine = get_object_or_404(Machine, name=name)
    current_tools = Master.objects.filter(machine=name, status='on_machine')
    past_tools = Master.objects.filter(
        machine=name).exclude(status='on_machine')
    context = {
        'machine': machine,
        'current_tools': current_tools,
        'past_tools': past_tools,
    }
    return render(request, 'machine_details.html', context)
