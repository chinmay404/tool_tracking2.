import re
import logging
from django.urls import reverse, resolve
from django.shortcuts import redirect
from managment.views import logout_view

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)

    def __call__(self, request):
        excluded_paths = [
            reverse('login'), 
            reverse('register'), 
            '/tracking/',
            '/api/get/product/',
            '/api/get/packing_slip/',
            '/api/sale_order/',
            '/api/update-invoice/',
            '/media/',
        ]

        if any(request.path_info == path or request.path_info.startswith(path) for path in excluded_paths):
            return self.get_response(request)
        matched_view = resolve(request.path_info).url_name
        if matched_view in ['login', 'register']:
            return self.get_response(request)

        api_pattern = re.compile(r'^/api/get/\w{8}-\w{4}-\w{4}-\w{4}-\w{12}/$')
        if api_pattern.match(request.path_info):
            return self.get_response(request)

        if not request.user.is_authenticated:
            self.logger.info(f'User not authenticated. Redirecting to login. Path: {request.path_info}')
            return redirect('login')


        return self.get_response(request)
