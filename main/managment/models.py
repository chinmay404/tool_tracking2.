from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models import JSONField  # Import JSONField
from simple_history.models import HistoricalRecords







class CustomUserManagers(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not username:
            raise ValueError('The Username field must be set')  # Require a username
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password):
        user = self.create_user(username, email, password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True  
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    unit = models.CharField(max_length=50)
    objects = CustomUserManagers()
    history = HistoricalRecords()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']  


    def assign_role(self, role_name):
        if self.is_admin():
            unit_group, created = Group.objects.get_or_create(name=self.unit)
            role_group, created = Group.objects.get_or_create(name=f"{self.unit} - {role_name}")
            role_group.user_set.add(self)

            return f"Role '{role_name}' assigned to user {self.username} in unit {self.unit}"

        return "Permission denied. Only admins can assign roles."

    def revoke_role(self, role_name):
        if self.is_admin():
            try:
                role_group = Group.objects.get(name=f"{self.unit} - {role_name}")
                role_group.user_set.remove(self)

                return f"Role '{role_name}' revoked from user {self.username} in unit {self.unit}"
            except Group.DoesNotExist:
                return f"Role '{role_name}' does not exist in unit {self.unit}"

        return "Permission denied. Only admins can revoke roles."

    def is_admin(self):
        return self.is_staff and self.unit

    def __str__(self):
        return f"{self.username}"
    





class Vehicle(models.Model):
    vehicle_number = models.CharField(max_length=20, unique=True)
    on_path = models.BooleanField(default=False, null=True)
    driver_name = models.CharField(max_length=100, null=True)
    ongoing_status = JSONField(default=dict, null=True)  # Setting default to an empty dictionary
    current_carrying = JSONField(null=True)
    past_carried = JSONField(null=True)
    status = models.CharField(null=True, blank=True)
    driver_phone_number = models.CharField(max_length=15, null=True)
    current_destination = models.CharField(max_length=150, null=True)
    last_location = models.CharField(max_length=150, null=True)
    data_json = JSONField(null=True)
    history = HistoricalRecords()

    # Extra fields from API response
    vehicle_make = models.CharField(max_length=100, null=True)
    vehicle_model = models.CharField(max_length=100, null=True)
    fuel_type = models.CharField(max_length=50, null=True)
    vehicle_year = models.IntegerField(null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    last_updated_at = models.DateTimeField(null=True)
    last_status_time = models.DateTimeField(null=True)
    last_acc_on = models.DateTimeField(null=True)
    total_odometer = models.FloatField(null=True)
    current_status = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=255, null=True)
    tag_ids = models.JSONField(null=True)
    vehicle_type_value = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.vehicle_number
    
    def default_ongoing_status(self):
        return {
            "Allocated": {},
            "Dispatched": {},
            "Reached":{},
            "Returned":{},
            "Total_time":{},
        }
    
    
    
    

