import requests
from django.http import JsonResponse
from django.utils import timezone
import time
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from .models import Vehicle
from django.contrib.auth.decorators import login_required
from .decorators import unauth_user, allowed_users

@login_required(login_url='managment/login/')
@allowed_users(allowed_roles=['admins', 'managment_user',])
def vehicle_detail(request, vehicle_number):
    # Get vehicle object from database
    vehicle = get_object_or_404(Vehicle, vehicle_number=vehicle_number)

    # Send request to API to get live location data
    api_url = f"https://api.fleetx.io/api/v1/analytics/live/byNumber/{vehicle_number}"
    headers = {"Authorization": "Bearer bbb342c4-c2a6-43fa-9475-0f8151eb1e7d"}
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        live_location_data = response.json()

        # Update vehicle model with live location data
        vehicle.latitude = live_location_data.get('latitude')
        vehicle.longitude = live_location_data.get('longitude')
        vehicle.last_updated_at = live_location_data.get('lastUpdatedAt')
        vehicle.last_status_time = live_location_data.get('lastStatusTime')
        vehicle.last_acc_on = live_location_data.get('lastAccOn')
        vehicle.total_odometer = live_location_data.get('totalOdometer')
        vehicle.status = live_location_data.get('status')
        vehicle.address = live_location_data.get('address')
        vehicle.vehicle_make = live_location_data.get('vehicleMake')
        vehicle.vehicle_model = live_location_data.get('vehicleModel')
        vehicle.fuel_type = live_location_data.get('fuelType')
        vehicle.vehicle_year = live_location_data.get('vehicleYear')
        vehicle.current_status = live_location_data.get('currentStatus')
        vehicle.tag_ids = live_location_data.get('tagIds')
        vehicle.vehicle_type_value = live_location_data.get('vehicleTypeValue')

        vehicle.save()

        # Fetch historical records and past carried data as before
        history = None
        past_carried_data = vehicle.past_carried
        print(f"LIVE LOCATION SENT INTIAL : {vehicle.latitude} : {vehicle.longitude}")
        return render(request, 'vehicle_detail.html', {'vehicle': vehicle, 'history': history, 'past_carried_data': past_carried_data})
    else:
        messages.error(request, f'Fletex API Request Failed')
        messages.error(request, f'Error Code : {response.status_code}')
        messages.error(request, f'response : {response}')
        return render(request, 'vehicle_detail.html', {'vehicle': vehicle, 'history': history, 'past_carried_data': past_carried_data})





def live_location(request, vehicle_number):
    # api_url = f"https://api.fleetx.io/api/v1/analytics/live/byNumber/{vehicle_number}"
    # headers = {"Authorization": "Bearer bbb342c4-c2a6-43fa-9475-0f8151eb1e7d"}

    # time.sleep(10000)
    # response = requests.get(api_url, headers=headers)
    # print("VIEW CALLED")
    # if response.status_code == 200:
        # live_location_data = response.json()
        # latitude = live_location_data.get('latitude')
        # longitude = live_location_data.get('longitude')
        time.sleep(10)
        latitude = 16.7706683
        longitude = 74.2735483
        print(f"LIVE LOCATION SENT : {latitude} {longitude}")
        return JsonResponse({'latitude': latitude, 'longitude': longitude})
    # else:
        # return JsonResponse({'error': 'Failed to fetch live location data'}, status=500)
    
    
    
    
    
@login_required(login_url='managment/login/')
@allowed_users(allowed_roles=['admins', 'managment_user',])
def vehicle_list(request):
    api_url = 'https://api.fleetx.io/api/v1/analytics/live'
    headers = {'Authorization': 'Bearer bbb342c4-c2a6-43fa-9475-0f8151eb1e7d'}
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        api_data = response.json()
        vehicles = api_data.get('vehicles', [])
    else:
        error_message = f"Failed to fetch data from Fletex API: {response.status_code}"
        messages.error(request, f'error_message ; {error_message}')
    return render(request, 'vehicle_list.html', {'vehicles': vehicles})
    