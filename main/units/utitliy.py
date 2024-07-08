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


def reached_at_destination(request,veichal_no):
    try:
        vehicle = Vehicle.objects.get(vehicle_number=veichal_no)
        vehicle.status = 'reached_at_destination'
        ongoing_status_data = vehicle.ongoing_status or {}
        ongoing_status_data['reached_at_destination'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        vehicle.ongoing_status = ongoing_status_data
        vehicle.last_location = request.user.unit.name
        vehicle.save()
        # messages.success(request, f'Veichal ')
    except Exception as e:
        messages.error(request, f'Veichal Return Marking Error: {e}')
    
    


def chnage_all_master():
    pass
    