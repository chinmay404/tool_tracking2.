from django.shortcuts import render, redirect, HttpResponse ,get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomUserAuthenticationForm
from .decorators import unauth_user, allowed_users
from django.contrib.auth.models import Group
from inlet.models import Master,ProductIndex,Product
from django.db.models import Q
from django.db.models import Count, Case, When, IntegerField
from django.contrib.auth.models import User, Group, Permission
from .models import CustomUser, Vehicle
from outlet.models import SaleOrder
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models.functions import TruncMonth
from django.utils import timezone
import json
from django.contrib.sessions.models import Session
from datetime import datetime, timedelta
from AI import ai
from django.contrib import messages
from main.settings import ALLOW_AI

def chat(request):
    response = None
    if request.method == 'POST' and ALLOW_AI:
        user_input = request.POST.get('user_input', '')
        try:
            response = ai.get_response(user_input,request)
        except Exception as e:
            messages.error(request, f'Error :  {e}')
    if ALLOW_AI:
        return render(request, 'chat.html', {'response': response})
    else:
        return render(request, 'unavilable.html')



    

@login_required(login_url='managment/login/')
@allowed_users(allowed_roles=['admins', 'managment_user'])
def home(request):
    all_vehicles = Vehicle.objects.all()
    product_indexes = ProductIndex.objects.filter(status='verified').order_by('-arrive_date')
    activated_product_index = product_indexes.filter(status='verified')
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    # Extract user IDs from active sessions
    active_user_ids = [session.get_decoded().get('_auth_user_id') for session in active_sessions]
    # Get active users
    time_range = request.GET.get('time_range')

    if time_range == 'one_month':
        start_date = datetime.now() - timedelta(days=30)
    elif time_range == 'one_week':
        start_date = datetime.now() - timedelta(days=7)
    else:
        # Default to one month if no time range is selected
        start_date = datetime.now() - timedelta(days=30)
    active_users = CustomUser.objects.filter(id__in=active_user_ids)  # Use your custom user model
    completed_sale_orders_count = SaleOrder.objects.filter(status='complete', order_date__gte=start_date).count()
    total_sale_orders_count = SaleOrder.objects.count()
    total_product_indexes_count = ProductIndex.objects.count()
    completed_product_indexes_count = ProductIndex.objects.filter(status='complete', arrive_date__gte=start_date).count()

    # Implement search functionality
    query = request.GET.get('q')
    if query:
        product_indexes = product_indexes.filter(
            Q(gate_inward_No__icontains=query) |
            Q(party_challan_no__icontains=query) |
            Q(part_bill_no__icontains=query) |
            Q(batch_id__icontains=query) |
            Q(UOM__icontains=query) |
            Q(po_no__icontains=query) |
            Q(status__icontains=query) |
            Q(received_by__username__icontains=query) |
            Q(arrive_date__icontains=query)
        )
        activated_product_index = product_indexes.filter(status='verified')

    # Implement paging
    per_page = 10  # You can adjust this as needed
    paginator = Paginator(product_indexes, per_page)
    page = request.GET.get('page')
    total_count = Master.objects.all().count
    status_counts = Master.objects.values('status').annotate(count=Count('status'))
    status_count_dict = {item['status']: item['count'] for item in status_counts}

    try:
        product_indexes = paginator.page(page)
    except PageNotAnInteger:
        product_indexes = paginator.page(1)
    except EmptyPage:
        product_indexes = paginator.page(paginator.num_pages)
    
    # Retrieve monthly counts
    monthly_counts = ProductIndex.objects.filter(status='verified').annotate(
        month=TruncMonth('arrive_date')).values('month').annotate(count=Count('arrive_date')).order_by('-month')[:12]

    # Extract counts from monthly_counts
    monthly_counts_dict = {entry['month'].strftime('%B %Y'): entry['count'] for entry in monthly_counts}

    # Create chart data
    chart_data = {
        'saleOrdersCount': total_sale_orders_count,
        'completedSaleOrdersCount': completed_sale_orders_count,
        'productIndexesCount': total_product_indexes_count,
        'completedProductIndexesCount': completed_product_indexes_count,
        'monthlyCounts': monthly_counts_dict
    }

    context = {
        'completed_sale_orders_count': completed_sale_orders_count,
        'completed_product_indexes_count': completed_product_indexes_count,
        'status_counts': status_count_dict,
        'product_indexes': product_indexes,
        'total_count': total_count,
        'active_users': active_users,
        'all_vehicles': all_vehicles,
        'activated_product_index': activated_product_index,
        'search_query': query,
        'chart_data': json.dumps(chart_data),
        'total_sale_orders_count': total_sale_orders_count,
        'total_product_indexes_count': total_product_indexes_count
    }

    return render(request, 'managment_home.html', context)


def sale_orders(request):
    sale_orders = SaleOrder.objects.all()

    # Implement search functionality
    query = request.GET.get('q')
    if query:
        sale_orders = sale_orders.filter(
            Q(grn_number__icontains=query) |
            Q(po_number__icontains=query) |
            Q(vehicle_no__icontains=query) |
            Q(driver_name__icontains=query) |
            Q(destination__icontains=query) |
            Q(bill_no__icontains=query)
        )

    page = request.GET.get('page', 1)
    paginator = Paginator(sale_orders, 10)

    try:
        sale_orders = paginator.page(page)
    except PageNotAnInteger:
        sale_orders = paginator.page(1)
    except EmptyPage:
        sale_orders = paginator.page(paginator.num_pages)

    context = {
        'sale_orders': sale_orders,
        'search_query': query,  # Pass the search query to pre-fill the search input in the template
    }

    return render(request, 'sale_orders.html', context)




@login_required(login_url='managment/login/')
@allowed_users(allowed_roles=['admins', 'managment_user'])
def vehicle_detail(request, vehicle_number):
    vehicle = get_object_or_404(Vehicle, vehicle_number=vehicle_number)
    past_carried_data = vehicle.past_carried
    history = vehicle.history.all()
    current_carrying_sale_order = {}
    print("CURRENT CARRYING TRACK")
    print(vehicle.current_carrying)
    if vehicle.current_carrying:
        for group_id in vehicle.current_carrying:
            sale_orders = SaleOrder.objects.filter(group_id=group_id)
            print(sale_orders)
            current_carrying_sale_order[group_id] = sale_orders
    primary_key(current_carrying_sale_order)
    context = {
        'vehicle': vehicle,
        'history': history,
        'past_carried_data': past_carried_data,
        'current_carrying_sale_order': current_carrying_sale_order,
    }

    return render(request, 'vehicle_detail.html', context)


@login_required(login_url='managment/login/')
@allowed_users(allowed_roles=['admins', 'managment_user',])
def inventory_detail(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    masters = Master.objects.filter(product=product)
    masters_count = masters.count()

    active_masters_count = masters.filter(status='active').count()
    in_progress_masters_count = masters.filter(status='in_progress').count()

    context = {
        'masters': masters,
        'masters_count': masters_count,
        'product': product,
        'active_masters_count': active_masters_count,
        'in_progress_masters_count': in_progress_masters_count,
    }
    return render(request, 'inventory_detail.html', context)


@login_required
def profile_view(request):
    user = request.user
    historical_records = user.history
    context = {
        'user': user,
    }
    return render(request, 'profile.html', context)


@unauth_user
def login_view(request):
    form = CustomUserAuthenticationForm(request, data=request.POST)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            print('User:', user)

            login(request, user)
            messages.success(request, f'Welcome { user.username }')
            
            if user.groups.exists():
                group_names = [group.name for group in user.groups.all()]
                # print('User Groups: ', group_names)

                if 'admins' in group_names or 'managment_user' in group_names or user.username == 'admin':
                    return redirect('managment_home')
                elif 'inlet_user' in group_names:
                    return redirect('inlet_home')
                elif 'store_user' in group_names:
                    return redirect('api_home')
                elif 'inspection' in group_names:
                    return redirect('batch_verification')
                
                elif 'activators' in group_names:
                    return redirect('list_batch')
                elif 'outlet_user' in group_names:
                    return redirect('outlet_home')
                elif 'gate_user' in group_names:
                    return redirect('batch_verification')
                elif any('Units' in group_name for group_name in group_names):
                    return redirect('units_home')  # Redirect to units_home for users in any group containing "Units"
                elif 'wait_list' in group_names:
                    return redirect('wating_feild')
        else:
            print('Form errors:', form.errors)
            messages.error(request, f'Invalid username or password')
        form = CustomUserAuthenticationForm()

    context = {
        'form': form,
    }
    return render(request, 'login.html', context)



@unauth_user
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            group = Group.objects.get(name='wait_list')
            user.groups.add(group)
            login(request, user)
            return redirect('wating_feild')
    else:
        form = CustomUserCreationForm()

    context = {
        'form': form,
    }
    return render(request, 'register.html', context)


@login_required(login_url='managment/login/')
def logout_view(request):
    logout(request)
    return redirect('login')


@allowed_users(allowed_roles=['admins'])
def admin_only(request):
    return redirect('admin:index')





@login_required(login_url='managment/login/')
def wating_feild(request):
    return render(request,'wating_feild.html')


@login_required(login_url='managment/login/')
@allowed_users(allowed_roles=['admins', 'managment_user'])
def inquiry(request):
    search_results = None

    if request.method == 'POST':
        query = request.POST.get('query')
        if query:
            fields_to_search = ['uuid', 'batch_id', 'product__name', 'status', 'added_date', 'received_by__username','status']
            queries = [Q(**{f'{field}__icontains': query}) for field in fields_to_search]
            search_query = Q()
            for query in queries:
                search_query |= query

            search_results = Master.objects.filter(search_query)

    return render(request, 'inquiry.html', {'search_results': search_results})






                    # ************  USER MANAGEMNT ***********#

@login_required(login_url='login')  # Ensure the user is logged in
def manage_users(request):
    if request.user.is_admin():
        users = CustomUser.objects.all()
    else:
        users = CustomUser.objects.filter(unit=request.user.unit)
        

    context = {
        'users': users,
    }

    return render(request, 'manage_users.html', context)

def manage_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user_groups = user.groups.all()
    user_permissions = user.user_permissions.all()

    groups = Group.objects.all()
    permissions = Permission.objects.all()

    sorted_permissions = get_sorted_permissions()

    context = {
        'user': user,
        'user_groups': user_groups,
        'user_permissions': user_permissions,
        'groups': groups,
        'permissions': permissions,
        'sorted_permissions': sorted_permissions,
    }

    return render(request, 'manage_user.html', context)



@login_required(login_url='managment/login/')
def get_sorted_permissions():
    permissions = Permission.objects.all()

    sorted_permissions = {}

    for permission in permissions:
        # Extract category from permission name
        category = permission.name.split()[2].lower()
        if category not in sorted_permissions:
            sorted_permissions[category] = []
        sorted_permissions[category].append(permission)

    return sorted_permissions

@login_required(login_url='managment/login/')
def manage_users_unit(request):
    unit_users = CustomUser.objects.filter(unit=request.user.unit)
    context = {'users': unit_users}
    return render(request, 'manage_users.html', context)