from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import CustomUser,Vehicle
from simple_history.admin import SimpleHistoryAdmin

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'date_joined', 'last_login', 'is_active', 'is_staff', 'unit']
    list_display_links = ['username']
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('unit',)}),
        ('Permissions', {'fields': ('groups', 'user_permissions')}),

    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_active', 'is_staff', 'user_permissions', 'unit'),
        }),
    )
    search_fields = ['username', 'email', 'unit']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "user_permissions":
            unit_name = request.user.unit if request.user.is_authenticated else None
            kwargs["queryset"] = db_field.related_model.objects.filter(content_type__app_label='your_app_name', content_type__model='customuser', group__name__contains=unit_name)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.is_staff and obj.unit:
            group_name = f'{obj.unit} - Admins'
            admin_group, created = Group.objects.get_or_create(name=group_name)
            admin_group.user_set.add(obj)



class VehicleAdmin(SimpleHistoryAdmin):  # Using SimpleHistoryAdmin instead of admin.ModelAdmin
    list_display = ['vehicle_number', 'driver_name', 'driver_phone_number']
    search_fields = ['vehicle_number', 'driver_name', 'driver_phone_number']
    
    
    
    
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Vehicle, VehicleAdmin)