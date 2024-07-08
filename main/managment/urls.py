
from django.urls import path,include
from . import views
from . import veichal_update
from AI import ai




urlpatterns = [
    path('', views.home, name='managment_home_black'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('register/', views.register_view, name='register'),
    path('home/', views.home, name='managment_home'),
    path('logout/', views.logout_view, name='logout'),
    path('admin_only/', views.admin_only, name='admin_only'),
    path('wating_feild/', views.wating_feild, name='wating_feild'),
    path('inquiry/', views.inquiry, name='inquiry'),
    path('inventory_detail/<str:product_id>/', views.inventory_detail, name='inventory_detail'),
    path('manage_users/', views.manage_users, name='manage_users'),
    path('manage_users_unit/', views.manage_users_unit, name='manage_users_unit'),
    path('manage_user/<int:user_id>/', views.manage_user, name='manage_user'),
    path('sale_orders/', views.sale_orders, name='sale_orders'),
    path('vehicle_list/', veichal_update.vehicle_list, name='vehicle_list'),
    path('chat/', views.chat, name='chat'),
    path('vehicles/<str:vehicle_number>/', veichal_update.vehicle_detail, name='vehicle_detail'),
    path('live_location/<str:vehicle_number>/', veichal_update.live_location, name='live_location'),
    
]
