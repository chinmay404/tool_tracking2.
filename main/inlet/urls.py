from django.urls import path,include
from . import views
from django.views.generic import RedirectView


urlpatterns = [
    path('', RedirectView.as_view(pattern_name='inlet_home', permanent=False)),
    path('home/', views.home, name='inlet_home'),
    path('create_product_index/',views.create_product_index,name='create_product_index'),
    path('list_product_index/', views.list_product_index,name='list_product_index'),
    path('list_products/', views.list_products, name='list_products'),
    path('product_list_masters/<str:MaterialCode>', views.product_list_masters, name='product_list_masters'),
    path('product_specification/<int:product_id>/', views.product_specification, name='product_specification'),
    path('product_batch/<uuid:batch_id>/', views.product_batch, name='product_batch'),
    path('product_quantity/<int:product_id>/', views.product_quantity, name='product_quantity'),
    # path('download_ids/<uuid:batch_id>/', views.download_ids, name='download_ids'),
    # path('download_id/<uuid:master_id>/', views.download_id, name='download_id'),
    path('api/', include('api.urls')),
    path('download-qr/<str:batch_id>/<str:grn_no>', views.download_qr_code, name='download_qr'),
    path('print-qr/<str:batch_id>/<str:grn_no>/<str:size>', views.print_qr_code, name='print_qr'),
    path('printing/', views.is_printed, name='printing'),
    path('view_product/<str:product_id>/', views.view_master, name='view_product'),
    path('batch_verification/', views.batch_verification, name='batch_verification'),
    path('batch_verification_history/', views.batch_verification_history, name='batch_verification_history'),
    path('batch_activation/<str:batch_id>', views.batch_activation, name='batch_activation'),
    path('create_product/', views.create_product, name='create_product'),
    path('download/<int:item_id>/<int:batch_id>/', views.download_file, name='download_file'),
    path('generate-qr/', views.generate_qr_page, name='generate_qr_page'),

]
