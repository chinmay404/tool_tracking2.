from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test

def unauth_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('managment_home')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff, login_url='not_authorised')

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
                print(f"User_GROUP : {group}")
            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return render(request, "not_authorised.html")
        return wrapper_func
    return decorator
