from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic import RedirectView
from managment import views as managment_views
from django.contrib import admin
from api.utility_api_calls import tracking_detail

admin.site.site_title = 'Tool Tracking ADMIN'
admin.site.site_header = 'ADMIN Portal'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout/', managment_views.logout_view, name='logout'),
    path('managment/', include('managment.urls')),
    path('inlet/', include('inlet.urls')),
    path('api/', include('api.urls')),
    path('outlet/', include('outlet.urls')),
    path('units/', include('units.urls')),
    path('tracking/<str:tracking_id>/', tracking_detail, name='tracking_detail'),
    path('', RedirectView.as_view(pattern_name='managment_home', permanent=False)),  
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)