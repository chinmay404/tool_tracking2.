from django.urls import path,include
from . import views
from django.views.generic import RedirectView


urlpatterns = [
    path('', RedirectView.as_view(pattern_name='units_home', permanent=False)),
    path('home/', views.home, name='units_home'),
    path('requisitions_history/', views.requisitions_history, name='requisitions_history'),
    path('requisitions_history/', views.requisitions_history, name='requisitions_history'),
    path('units_inlet/', views.units_inlet_input, name='units_inlet_input'),
    path('units_inlet_group/<str:group_id>', views.units_inlet, name='units_inlet_group'),
    path('units_inspection', views.units_inspection, name='units_inspection'),
    path('units_inventory/', views.units_inventory, name='units_inventory'),
    path('units_product/<str:product_name>/', views.units_product, name='units_product'),
    path('done_verification/<str:group_id>/', views.units_done_verification, name='units_done_verification'),
    path('unit_machines/', views.unit_machines, name='unit_machines'),
    path('machine_details/<str:name>/', views.machine_details, name='machine_details'),
    path('master_allocation/<int:requisition_id>/', views.master_allocation, name='master_allocation'),
    path('process_master_allocation/<int:requisition_id>/', views.process_master_allocation, name='process_master_allocation'),
    path('mark_sale_order_checked/', views.mark_sale_order_checked, name='mark_sale_order_checked'),
    path('accept_all/<str:uuid>/', views.accept_or_reject_all, {'action': 'accept'}, name='accept_all'),
    path('reject_all/<str:uuid>/', views.accept_or_reject_all, {'action': 'reject'}, name='reject_all'),
    path('indivisual_inspection/<str:uuid>/', views.indivisual_inspection, name='indivisual_inspection'),
    path('units_inspection_saleorder_list/', views.units_inspection_saleorder_list, name='units_inspection_saleorder_list'),
    path('master_allocation/<int:requisition_id>/product_detail/<str:product_id>/', views.requisition_product_detail, name='product_detail'),
    path('process_master_allocation/<int:requisition_id>/product_detail/<str:product_id>/', views.process_master_allocation, name='process_master_allocation'),
    # path('home/', views.home, name='units_home'),
]