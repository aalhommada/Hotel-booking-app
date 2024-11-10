# accounts/middleware.py
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class RoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Define protected paths
            admin_paths = ['/admin/', '/manager/']
            team_paths = ['/bookings/manage/']
            
            path = request.path_info
            
            # Allow superusers everywhere
            if request.user.is_superuser:
                return self.get_response(request)

            # Check admin area access
            if any(path.startswith(p) for p in admin_paths):
                # Allow staff users with permissions
                if request.user.is_staff and request.user.groups.filter(permissions__isnull=False).exists():
                    return self.get_response(request)
                messages.error(request, 'Access denied. Insufficient permissions.')
                return redirect('rooms:room_list')

            # Check team area access
            if any(path.startswith(p) for p in team_paths):
                if request.user.groups.filter(permissions__isnull=False).exists():
                    return self.get_response(request)
                messages.error(request, 'Access denied. Insufficient permissions.')
                return redirect('rooms:room_list')

        response = self.get_response(request)
        return response