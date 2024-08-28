from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from managment.decorators import *
from .models import ProductIndex, Master,Product
from .forms import *
from django.shortcuts import render, get_object_or_404
from django.db.models import Q,Sum, F
import csv
from django.utils import timezone
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count
import uuid,json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from math import ceil
import hashlib
from api.utility_api_calls import *
from outlet.qr_gen import single_qr,single_qr_main ,generate_qr_code_grn
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.template.loader import render_to_string
import base64
from .models import generate_short_uuid
import pandas as pd
import io
from openpyxl import Workbook
from openpyxl.drawing.image import Image as ExcelImage
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
from reportlab.lib.utils import ImageReader

# TODO: InProgress master Count Add When Verified
# Create your views here.




def generate_qr_page(request):
    if request.method == 'POST':
        count = int(request.POST.get('count'))
        if count <= 30:
            short_uuids = [generate_short_uuid() for _ in range(count)] 
            qr_codes = [single_qr(uuid,dotted_style=True,logo=False) for uuid in short_uuids] 
            
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="qr_codes.pdf"'
            
            c = canvas.Canvas(response, pagesize=letter)
            
            for qr_code in qr_codes:
                img_buffer = BytesIO(qr_code)
                img = Image.open(img_buffer)
                width, height = img.size
                c.setPageSize((width, height))
                reportlab_img = ImageReader(img)
                c.drawImage(reportlab_img, 0, 0, width, height)
                c.showPage() 
            
            c.save()
            return response
        else:
            messages.error(request, 'Number Must Be Below 30')
    return render(request, 'generate_qr_page.html')



@login_required(login_url='managment/login/')
@allowed_users(['admins', 'inlet_user'])
def home(request):
    product_indexes = ProductIndex.objects.filter(status='verified' ,is_printed=True)
    search_query = request.GET.get('search', '')
    if search_query:
        product_indexes = product_indexes.filter(
    Q(batch_id__icontains=search_query) |
    Q(status__icontains=search_query) |
    Q(received_by__username__icontains=search_query) |
    Q(arrive_date__icontains=search_query)
)
    
    per_page = 10
    paginator = Paginator(product_indexes, per_page)
    page = request.GET.get('page', 1)

    try:
        product_indexes = paginator.page(page)
    except PageNotAnInteger:
        product_indexes = paginator.page(1)
    except EmptyPage:
        product_indexes = paginator.page(paginator.num_pages)

    context = {
        'product_indexes': product_indexes,
        'search_query': search_query,
    }

    return render(request, 'inlet_home.html', context)



@login_required(login_url='managment/login/')
@allowed_users(['admins', 'inlet_user'])
def create_product_index(request):
    if request.method == 'POST':
        try:
            form = ProductIndexForm(request.POST)
            if form.is_valid():
                received_by = request.user
                form.instance.received_by = received_by 
                form.save()
            return redirect('inlet_home')
        except Exception as E:
            print("ERRORRRRRRRRRRRR : ",E)
            pass
        
    else:
        form = ProductIndexForm()

    return render(request, 'create_product_index.html', {'form': form})


@login_required(login_url='managment/login/')
@allowed_users(['admins', 'inlet_user'])
def list_product_index(request):
    product_indexes = ProductIndex.objects.all().order_by('-arrive_date')  # Added ordering
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        product_indexes = product_indexes.filter(
            Q(gate_inward_No__icontains=search_query) |
            Q(party_challan_no__icontains=search_query) |
            Q(part_bill_no__icontains=search_query) |
            Q(batch_id__icontains=search_query) |
            Q(UOM__icontains=search_query) |
            Q(po_no__icontains=search_query) |
            Q(status__icontains=search_query) |
            Q(received_by__username__icontains=search_query) |
            Q(arrive_date__icontains=search_query)
        )
    
    items_per_page = 10 
    paginator = Paginator(product_indexes, items_per_page)
    page = request.GET.get('page', 1)
    
    try:
        product_indexes = paginator.page(page)
    except PageNotAnInteger:
        product_indexes = paginator.page(1)
    except EmptyPage:
        product_indexes = paginator.page(paginator.num_pages)

    return render(request, 'product_index_list.html', {'product_indexes': product_indexes, 'search_query': search_query})


@login_required(login_url='managment/login/')
@allowed_users(['admins', 'inlet_user', 'managment_user'])
def list_products(request):
    products = Product.objects.all()
    per_page = 20
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
    Q(name__icontains=search_query) |
    Q(product_id__icontains=search_query) |
    Q(MaterialCode__icontains=search_query) |
    Q(description__icontains=search_query)
)

    paginator = Paginator(products, per_page)
    page = request.GET.get('page')

    try:
        masters = paginator.page(page)
    except PageNotAnInteger:
        masters = paginator.page(1)
    except EmptyPage:
        masters = paginator.page(paginator.num_pages)

    return render(request, 'list_products.html', {'products': products, 'search_query': search_query})


@login_required(login_url='managment/login/')
@allowed_users(['admins', 'inlet_user', 'managment_user'])
def product_list_masters(request ,MaterialCode):
    product = get_object_or_404(Product, MaterialCode=MaterialCode)
    masters_list = Master.objects.filter(product=product)
    active_count = product.active_count
    inProgressCount = product.in_progress_masters_count
    totalCount = masters_list.count
    break_count = product.break_count
    deactive_count = product.deactive_count
    per_page = 20
    search_query = request.GET.get('search')
    if search_query:
        masters_list = masters_list.filter(
    Q(product__name__icontains=search_query) |
    Q(status__icontains=search_query) |
    Q(uuid__icontains=search_query) |
    Q(batch_id__icontains=search_query)
)

    paginator = Paginator(masters_list, per_page)
    page = request.GET.get('page')

    try:
        masters = paginator.page(page)
    except PageNotAnInteger:
        masters = paginator.page(1)
    except EmptyPage:
        masters = paginator.page(paginator.num_pages)
    return render(request, 'master_list_by_product.html', {'product': product, 'masters': masters, 'active_count': active_count, 'in_progress_count': inProgressCount})



@login_required(login_url='managment/login/')
@allowed_users(['admins', 'inlet_user', 'managment_user'])
def product_specification(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product_indexes = ProductIndex.objects.filter(product=product)
    context = {
        'product': product,
        'product_indexes': product_indexes,
        # Add other specification data to the context as needed
    }
    
    return render(request, 'product_specification.html', context)


@login_required(login_url='managment/login/')
@allowed_users(['admins', 'inlet_user', 'managment_user'])
def product_quantity(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product_indexes = ProductIndex.objects.filter(product=product)
    
    context = {
        'product': product,
        'product_indexes': product_indexes,
    }
    
    return render(request, 'product_quantity.html', context)



@login_required(login_url='managment/login/')
@allowed_users(['admins', 'inlet_user', 'managment_user','activators'])
def product_batch(request, batch_id):
    products = Master.objects.filter(batch_id=batch_id)
    product_index = ProductIndex.objects.filter(batch_id=batch_id).first()
    Received_By = None
    Received_Date = None
    product_counts = 0

    if products.exists(): 
        first_product = products.first() 
        Received_By = first_product.received_by
        Received_Date = first_product.added_date.strftime('%Y-%m-%d %H:%M:%S')
        product_counts = (
        Master.objects
        .filter(batch_id=batch_id)
        .values('status')
        .annotate(count=Count('status'))
    )

    context = {
        'products': products,
        'product_index': product_index,
        'product_counts': product_counts,
        'batch_id_info': batch_id,
        'Received_By': Received_By,
        'Received_Date': Received_Date,
    }
    return render(request, 'product_batch.html', context)



@login_required(login_url='managment/login/')
@allowed_users(['admins', 'inlet_user', 'managment_user','activators'])
def download_ids(request, batch_id):

    products = Master.objects.filter(batch_id=batch_id)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="unique_ids_batch_{batch_id}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Unique ID'])
    for product in products:
        writer.writerow([product.uuid])
    return response

@login_required(login_url='managment/login/')
@allowed_users(['admins', 'inlet_user', 'managment_user','activators'])
def download_id(request, master_id):

    try:
        product = Master.objects.get(uuid=id)
        products = [product]
        response['Content-Disposition'] = f'attachment; filename="unique_id_{id}.csv"'
    except Master.DoesNotExist:
            messages.error(request, 'Invalid ID. Product not found.')
    writer = csv.writer(response)
    writer.writerow(['Unique ID'])
    for product in products:
        writer.writerow([product.uuid])
    return response



def is_printed(request):
    product_indexes = ProductIndex.objects.filter(status='verified' , is_printed=False)
    form = ProductIndexPrintForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        selected_product_indexes = request.POST.getlist('selected_product_indexes')
        received_by = request.user
        try:
            ProductIndex.objects.filter(pk__in=selected_product_indexes).update(is_printed=True , is_printed_by=received_by)    
            messages.success(request, f'marking Successful')
        except Exception as e:
            print(f"ERROR : {e}")
            messages.error(request, f'Error During Marking \nError : {e}')
       

    context = {'product_indexes': product_indexes, 'form': form}
    return render(request, 'printing.html', context)



@login_required(login_url='managment/login/')
@allowed_users(['admins', 'inlet_user' ,'activators'])
def activation(request):
    if request.method == 'POST':
        uuid_to_activate = request.POST.get('uuid_to_activate').replace(" ", "")
        uuid_to_activate = uuid_to_activate.replace(" ", "")
        try:
            master_product = Master.objects.get(uuid=uuid_to_activate)
            if request.user.has_perm('inlet.change_master'):
                try:
                    master_product.status = 'active'
                    activator_name = request.user.username 
                    activation_date = timezone.now()  
                    current_data = master_product.data_json or {}
                    current_data['Activation'] = {
                        'activator_name': activator_name,
                        'activator_email': request.user.email,
                        'activation_date': activation_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'status_changed_to': 'active',
                    }
                    master_product.data_json = current_data
                    master_product.save()
                    return redirect()
                except Exception as e:
                    pass
            else:
                messages.error(request, 'You are not authorized to activate this product.')
        except Master.DoesNotExist:
            messages.error(request, 'Invalid UUID. Product not found.')

    return render(request, 'activation.html')




@login_required(login_url='managment/login/')
@allowed_users(['admins', 'inlet_user', 'managment_user','activators'])
def view_master(request, product_id):
    product = get_object_or_404(Master, uuid=product_id)
    context = {
        'product': product,
    }
    return render(request, 'view_product.html', context)



@login_required(login_url='managment/login/')
@allowed_users(['admins', 'inlet_user', 'managment_user', 'activators'])
def batch_verification(request):
    unverified_product_indexes = ProductIndex.objects.filter(status='unverified').order_by('-grn_date')
    # verified_product_indexes = ProductIndex.objects.filter(status='verified')
    context = {
        'unverified_product_indexes': unverified_product_indexes,
    }
    return render(request, 'batch_verification.html', context)



@login_required(login_url='managment/login/')
@allowed_users(['admins', 'inlet_user', 'managment_user', 'activators'])
def download_qr_code(request, batch_id,grn_no):
    img_data = single_qr_main(batch_id,grn_no)
    response = HttpResponse(img_data, content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="qr_{batch_id}.png"'
    return response


def print_qr_code(request, batch_id, grn_no, size):
    print(f"SIZE : {size}")
    img_data = single_qr_main(batch_id, grn_no=grn_no, size=size)  # Pass size parameter here
    response = HttpResponse(img_data, content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="qr_{batch_id}.png"'
    return response


def batch_verification(request):
    query = request.GET.get('q')
    sort_by = request.GET.get('sort_by', '-arrive_date')
    filter_conditions = Q(status='unverified')

    if query:
        filter_conditions &= (Q(supplier_name__icontains=query) |
                              Q(supplier_gstin__icontains=query) |
                              Q(batch_id__icontains=query) | 
                              Q(party_challan_date__icontains=query) | 
                              Q(party_challan_no__icontains=query) | 
                              Q(grn_no__icontains=query))

    unverified_product_indexes = ProductIndex.objects.filter(filter_conditions).order_by(sort_by)

    paginator = Paginator(unverified_product_indexes, 10)
    page_number = request.GET.get('page')
    try:
        unverified_product_indexes = paginator.page(page_number)
    except PageNotAnInteger:
        unverified_product_indexes = paginator.page(1)
    except EmptyPage:
        unverified_product_indexes = paginator.page(paginator.num_pages)

    context = {
        'unverified_product_indexes': unverified_product_indexes,
        'query': query,
        'sort_by': sort_by,
    }
    return render(request, 'batch_verification.html', context)
    

@login_required(login_url='managment/login/')
@allowed_users(['admins', 'inlet_user', 'managment_user', 'activators'])
def batch_verification_history(request):
    product_indexes = ProductIndex.objects.filter(status='verified')

    # Implement search functionality
    query = request.GET.get('q')
    if query:
        product_indexes = product_indexes.filter(
            Q(batch_id__icontains=query) |
            Q(party_name__icontains=query) |
            Q(party_challan_no__icontains=query) |
            Q(part_bill_no__icontains=query) |
            Q(party_challan_no__icontains=query) |
            Q(arrive_date__icontains=query) |
            Q(status__icontains=query)
        )

    # Implement paging
    per_page = 10  # You can adjust this as needed
    paginator = Paginator(product_indexes, per_page)
    page = request.GET.get('page')

    try:
        product_indexes = paginator.page(page)
    except PageNotAnInteger:
        product_indexes = paginator.page(1)
    except EmptyPage:
        product_indexes = paginator.page(paginator.num_pages)

    context = {
        'product_indexes': product_indexes,
        'search_query': query,  # Pass the search query to pre-fill the search input in the template
    }
    return render(request, 'batch_verification_history.html', context)





# def short_quantity_report(request,product_index):
#     payload = {
#             "CompanyShortName": product_index.supplier_name,
#             "GrnNo": product_index.grn_no,
#             "GrnDate": product_index.grn_date.strftime('%d/%m/%Y'),
#             "PartyName": product_index.party_name,
#             "PartyChallanNo": product_index.party_challan_no,
#             "PartyChallanDate": product_index.party_challan_date,
#             "GateInwardNo": product_index.gate_inward_No,
#             "PoNo": product_index.po_no,
#             "PoDate": product_index.po_date.strftime('%d/%m/%Y'),
#             "SubGlAcNo": product_index.SubGlAcNo,
#             "short_qty": []
#         }
#     for item in product_index.productindexitem_set.all():
#         received_quantity_key = f'received_quantities_{ item.id }'
#         short_quantity = item.quantity_received - int(request.POST.get(received_quantity_key))
#         print(f'SHORT QUNATITY from report: {short_quantity}')
#         short_qty_item = {
#                     "MaterialCode": item.product.MaterialCode,
#                     "MaterialName": item.product.name,
#                     "MaterialUom": item.UOM,
#                     "ShortQty": short_quantity
#                 }
#         payload["short_qty"].append(short_qty_item)
#     try:
#         return(informinforminforminform_short_quantity_api(payload ,request ))
#     except Exception as e:
#         messages.error(request, f'Error Reporting Short Qunatity : {e}')
#         messages.error(request, f'can Not Procceed')
        
    

@login_required(login_url='managment/login/')
@allowed_users(['admins', 'inlet_user', 'managment_user', 'activators'])
def batch_activation(request, batch_id):
    product_index = get_object_or_404(ProductIndex, batch_id=batch_id)

    if request.method == 'POST':
        all_checkboxes_checked = True
        # short_quantity_reported = short_quantity_report(request,product_index)
        # print(short_quantity_reported)
        

        for item in product_index.productindexitem_set.all():
            received_quantity_key = f'received_quantities_{ item.id }'
            value_received_quantity = float(request.POST.get(received_quantity_key))
            print(f"Enetrd Quantity : { value_received_quantity }")
            short_quantity = item.quantity_received - float(request.POST.get(received_quantity_key))
            print(f'SHORT QUNATITY asdasd: {short_quantity}')
            key = f'quantity_per_box_select_{ item.id }'
            quantity_per_box_key = int(request.POST.get(key, '0'))

            print(f"QUANTITY PER BOX : {quantity_per_box_key} \n IS INSERT : {item.product.is_insert}")

            if True:
                try:
                    received_quantity = item.quantity_received
                    print(received_quantity)
                    received_quantity -= short_quantity
                    print(received_quantity)
                    # balancing_report = request.FILES.get(f'balancing_report_{item.id}')
                    # drawing = request.FILES.get(f'drawing_{item.id}')
                    # inspection_report = request.FILES.get(f'inspection_report_{item.id}')
                    # num_boxes = ceil(received_quantity / quantity_per_box_key)
                    
                    if received_quantity < 1:
                        messages.success(request, f'Zero Quantity : No Product Created')
                        item.short_quantity = short_quantity
                        item.save()
                    else:
                        product = item.product
                        product.in_progress_masters_count = F('in_progress_masters_count') + received_quantity
                        product.save()
                        if product.is_insert:
                            remaining_quantity = received_quantity
                            try:
                                received_quantity = ceil(remaining_quantity / quantity_per_box_key)
                            except Exception as e:
                                print(f"Error occurred during division: {e}")
                        received_quantity = int(round(received_quantity))                  
                        for _ in range(received_quantity):
                            if product.is_insert:
                                quantity_in_this_box = min(quantity_per_box_key, remaining_quantity)
                            b_name = f"INLET - {product_index.part_bill_no}"
                            master_data = {
                                'product': item.product,
                                'batch_id': batch_id,
                                'received_by': request.user,
                                'data_json': {
                                    'Inlet': {
                                        b_name: {
                                            'gate_inward_No': product_index.gate_inward_No,
                                            'supplier_name': product_index.supplier_name,
                                            'supplier_gstn': product_index.supplier_gstin,
                                            'product_id': item.product.product_id,
                                            'status': product_index.status,
                                            'batch_id': str(batch_id),
                                            'quantity_requested': item.quantity_requested,
                                            'quantity_received': received_quantity,
                                            'received_by': str(request.user),
                                            'arrive_date': product_index.arrive_date.strftime('%Y-%m-%d %H:%M:%S'),
                                            'party_challan_no': product_index.party_challan_no,
                                            'part_bill_no': product_index.part_bill_no,
                                            # 'part_date': product_index.part_date.strftime('%Y-%m-%d'),

                                            'po_no': product_index.po_no,
                                            'Insert': product.is_insert,
                                            # 'quantity_per_box': quantity_in_this_box ,
                                        }
                                    }
                                }
                            }
                            if product.is_insert:
                                master_data['data_json']['Inlet'][b_name]['quantity_per_box'] = quantity_in_this_box
                                print(f"INSERTS QUANTITY ADDED TO BOX : {quantity_in_this_box}")
                                remaining_quantity -= quantity_in_this_box
                            instance = Master.objects.create(**master_data)
                            if item.product.is_insert:
                                instance.is_insert = product.is_insert
                                instance.quantity_per_box = quantity_in_this_box
                                instance.box_capacity = quantity_per_box_key
                                print(f"INSER QUANTITY ADDED TO BOX : {instance.quantity_per_box}")
                                instance.save()
                        try:
                            if uploaded_file:
                                if balancing_report:
                                    item.balancing_report = balancing_report
                                if drawing:
                                    item.drawing = drawing
                                if inspection_report:
                                    item.inspection_report = inspection_report
                                # item.quantity_received = received_quantity
                                item.short_quantity = short_quantity
                                item.actual_quantity= received_quantity
                                item.unactive_count= received_quantity
                                item.save()
                                
                            else:
                                # item.quantity_received = received_quantity
                                item.short_quantity = short_quantity
                                item.actual_quantity= received_quantity
                                item.unactive_count = received_quantity
                                item.save()
                                
                        except Exception as e :
                            item.short_quantity = short_quantity
                            item.actual_quantity= received_quantity
                            item.unactive_count = received_quantity
                            item.save()
                            print("SAVED")
                            print(e)
                            # messages.error(request, f'File Upload Error \n{e}')
                        
                except Exception as e:
                    messages.error(request, f'Invalid received quantity for {item.product.name}. Please enter a valid number.\n Error : {e}')
                    print(f"batcH VERIFICTION : Please enter a valid number")
                    all_checkboxes_checked = True
        
        if all_checkboxes_checked :
            product_index.status = 'verified'
            product_index.save()
            print(f" VERIFICTION : successfull")
            messages.success(request, 'Batch activated successfully!')
            return redirect('batch_detail', batch_id=batch_id)
        else:
            messages.error(request, 'Please correct above issues and try again.')
    return redirect('batch_detail', batch_id=batch_id)

def generate_restore_id(product_name):
    current_timestamp = str(time.time())
    product_letter = product_name[0]
    data = current_timestamp + product_letter
    hashed_data = hashlib.sha256(data.encode()).hexdigest()
    restore_id = hashed_data[:6]
    return restore_id


# FILE UPLOAD

@login_required(login_url='managment/login/')
@allowed_users(['admins', 'inlet_user', 'managment_user', 'activators'])
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('batch_verification')
    else:
        form = ProductForm()

    return redirect('batch_verification')





def download_file(request, item_id, batch_id):
    item = get_object_or_404(YourModel, id=item_id)
    batch = get_object_or_404(YourBatchModel, id=batch_id)

    # Ensure the user has permission to access the file if needed

    file_path = item.uploaded_file.path
    with open(file_path, 'rb') as file:
        response = HttpResponse(file.read())
        content_type = 'application/octet-stream'
        response['Content-Type'] = content_type
        response['Content-Disposition'] = f'attachment; filename="{item.id}_{batch.id}_{os.path.basename(file_path)}"'
        return response
    
    
    
    
# @login_required(login_url='managment/login/')
# @allowed_users(['admins', 'inlet_user', 'managment_user', 'activators'])
# def batch_activation(request, batch_id):
#     product_index = get_object_or_404(ProductIndex, batch_id=batch_id)

#     if request.method == 'POST':
#         all_checkboxes_checked = True

#         for item in product_index.productindexitem_set.all():
#             received_quantity_key = f'received_quantities_{item.id}'
#             verification_checkbox_key = f'verification_checkboxes_{item.id}'

#             if request.POST.get(verification_checkbox_key):
#                 try:
#                     received_quantity = int(request.POST.get(received_quantity_key))
                    
#                     if received_quantity < 1:
#                         messages.error(request, f'Invalid received quantity for {item.product.name}. Please enter a valid number greater than zero.')
#                         all_checkboxes_checked = False
#                     else:
#                         for _ in range(received_quantity):
#                             b_name = f"INLET - {product_index.part_bill_no}"
#                             short_uuid = item.short_uuid
#                             master_data = {
#                                 'product': item.product,
#                                 'batch_id': batch_id,
#                                 'short_uuid': short_uuid,
#                                 'received_by': request.user,
#                                 'data_json': {
#                                     'Inlet': {
#                                         b_name: {
#                                             'gate_inward_No': product_index.gate_inward_No,
#                                             'product_id': item.product.product_id,
#                                             'status': product_index.status,
#                                             'batch_id': str(batch_id),
#                                             'quantity_requested': item.quantity_requested,
#                                             'quantity_received': received_quantity,
#                                             'received_by': str(request.user),
#                                             'arrive_date': product_index.arrive_date.strftime('%Y-%m-%d %H:%M:%S'),
#                                             'party_challan_no': product_index.party_challan_no,
#                                             'part_bill_no': product_index.part_bill_no,
#                                             'part_date': product_index.part_date.strftime('%Y-%m-%d'),
#                                             'UOM': product_index.UOM,
#                                             'po_no': product_index.po_no,
#                                             'rate': product_index.rate,
#                                             'ammount': product_index.ammount,
#                                         }
#                                     }
#                                 }
#                             }
#                             Master.objects.create(**master_data)

#                         item.quantity_received = received_quantity
#                         item.save()
#                 except ValueError:
#                     messages.error(request, f'Invalid received quantity for {item.product.name}. Please enter a valid number.')
#                     print(f"batcH VERIFICTION : Please enter a valid number")
#                     all_checkboxes_checked = False
#         if all_checkboxes_checked:
#             product_index.status = 'verified'
#             product_index.save()
#             print(f"batcH VERIFICTION : successfully")
#             messages.success(request, 'Batch activated successfully!')
#         else:
#             messages.error(request, 'Some checkboxes were not checked or invalid received quantity. Please correct the issues and try again.')
#             print(f"batcH VERIFICTION :Some checkboxes were not checked ")
#     return render(request, 'batch_detail.html', {'product_index': product_index})




















        # if request.method == 'POST':
        #     batch_ids = request.POST.get('batch_id')
        # print(f'BATCH VERIFICATION : {batch_ids}')
        # for batch_id in batch_ids:
        #     try:
        #         product_index = ProductIndex.objects.get(batch_id=batch_id, status='unverified')
        #         product_index.status = 'in_progress'
        #         with transaction.atomic():
        #             master_instances = []

        #             for item in product_index.productindexitem_set.all():
        #                 received_quantity_key = f'received_quantities_{item.id}'
        #                 checkbox_key = f'verification_checkboxes_{item.id}'
        #                 received_quantity = int(request.POST.get(received_quantity_key, 0))

        #                 if received_quantity > 0 and request.POST.get(checkbox_key):
        #                     # Create Master instances based on received quantity
        #                     for _ in range(received_quantity):
        #                         master_data = {
        #                             'inlet_data': {
        #                                 'gate_inward_No': product_index.gate_inward_No,
        #                                 'product_id': product_index.product.product_id,
        #                                 'status': product_index.status,
        #                                 'batch_id': str(batch_id),
        #                                 'quantity_requested': item.quantity_requested,
        #                                 'quantity_received': received_quantity,
        #                                 'received_by': str(request.user),
        #                                 'arrive_date': product_index.arrive_date.strftime('%Y-%m-%d %H:%M:%S'),
        #                                 'party_challan_no': product_index.party_challan_no,
        #                                 'part_bill_no': product_index.part_bill_no,
        #                                 'part_date': product_index.part_date.strftime('%Y-%m-%d'),
        #                                 'UOM': product_index.UOM,
        #                                 'po_no': product_index.po_no,
        #                                 'rate': product_index.rate,
        #                                 'ammount': product_index.ammount,
        #                             }
        #                         }
        #                         master_instances.append(Master(
        #                             product=item.product,
        #                             received_by=request.user,
        #                             batch_id=batch_id,
        #                             data_json=master_data
        #                         ))

        #             Master.objects.bulk_create(master_instances)

        #         # Update ProductIndex status and save
        #         product_index.quantity_received = sum(item.quantity_received for item in product_index.productindexitem_set.all())
        #         product_index.save()

        #         messages.success(request, f'Batch {batch_id} verified successfully.')
        #     except ProductIndex.DoesNotExist:
        #         messages.error(request, f'Invalid batch ID {batch_id}. Batch not found or already verified.')