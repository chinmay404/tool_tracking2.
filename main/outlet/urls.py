from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from . import views
from . import gen_pdf


urlpatterns = [
    path('',views.outlet_home,name='outlet_home'),
    path('sale-orders/<int:order_no>/', views.sale_order_detail, name='sale_order_detail'),
    path('add_uuid/<int:order_no>/<str:MaterialCode>/', views.add_uuid, name='add_uuid'),
    path('sale-orders/<int:order_no>/product/<str:MaterialCode>/', views.sale_order_product_detail, name='sale_order_product_detail'),
    path('sale-orders/<int:order_no>/product/<str:MaterialCode>/remove-uuid/', views.remove_uuid, name='remove_uuid'),
    path('sale-orders/<int:order_no>/product/<str:MaterialCode>/save-and-return/', views.save_and_return, name='save_and_return'),
    path('download_qrcode_pdf<int:order_no>/', views.download_qrcode_pdf, name='download_qrcode_pdf'),
    path('out_verification', views.out_verification, name='out_verification'),
    path('done_verification/<str:group_id>/', views.done_verification, name='done_verification'),
    path('create_sale_order_group/', views.create_sale_order_group, name='create_sale_order_group'),
    path('sale_order_group_detail/<int:group_id>/', views.sale_order_group_detail, name='sale_order_group_detail'),
    path('delete_sale_order_group/<int:group_id>/', views.delete_sale_order_group, name='delete_sale_order_group'),
    path('generate_pdf/<int:group_id>/', gen_pdf.generate_pdf, name='generate_pdf'),
    path('sale_order_group_history', views.sale_order_group_history, name='sale_order_group_history'),
    path('veichal_allocation', views.veichal_allocation, name='veichal_allocation'),
    path('veichal-allocation-details/<str:tracking_id>', views.veichal_allocation_details, name='veichal_allocation_details'),
    path('create_group_for_selected_orders/', views.create_group_for_selected_orders, name='create_group_for_selected_orders'),
    path('veichal-allocation-history/', views.veichal_allocation_history, name='veichal_allocation_history'), 
    path('add_groups_to_vehicle/<int:vehicle_id>/', views.add_groups_to_vehicle, name='add_groups_to_vehicle'),
    path('claim_empty_box/<path:product_id>/', views.claim_empty_box, name='claim_empty_box'),

]