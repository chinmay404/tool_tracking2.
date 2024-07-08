from django.urls import path
from .views import *
from .export_data import export_data
from .utility_api_calls import master_detail ,group_details , tracking_detail ,update_invoice_numbers

urlpatterns = [
    path('get/product/<str:uuid>/', master_detail, name='get_product'),
    path('get/packing_slip/<str:group_id>/', group_details, name='group_details_API'),
    path('', api_home, name='api_home'),
    path('batch_detail/<str:batch_id>/', batch_detail, name='batch_detail'),
    path('activate_via_batch/<str:batch_id>/', activate_via_batch, name='activate_via_batch'),
    path('activate_via_btach_single_product/<str:batch_id>/<str:MaterialCode>/', activate_via_btach_single_product, name='activate_via_btach_single_product'),
    path('activate_master/<str:MaterialCode>/', activate_master, name='activate_master'),
    path('activate_via_product', activate_via_product, name='activate_via_product'),
    path('activate_multiple_masters/<str:product_id>/', activate_multiple_masters, name='activate_multiple_masters'),
    # path('create_product_index/', CreateProductIndexView.as_view({'post': 'create'}), name='create_product_index'),
    # path('sale_order/', SaleOrderViewSet.as_view({'post': 'create'}), name='creat_sale_order'),
    path('upload-reports/', upload_reports, name='upload_reports'),
    path('export-data/<str:table_name>/<str:app>/', export_data, name='export_data'),
    path('get/get_product_details/<str:uuid>/', get_product_details , name='get_product_details_master'),
    path('tracking/<str:tracking_id>/', tracking_detail, name='tracking_detail'),
    path('update-invoice/', update_invoice_numbers, name='update_invoice_numbers'),
]
