from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden

def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please login to access this page.')
                return redirect('accounts:login')
                
            if request.user.role not in roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('rooms:room_list')
                
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator