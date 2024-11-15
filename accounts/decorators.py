# accounts/decorators.py
from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def group_required(*group_names):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "Please login to access this page.")
                return redirect("accounts:login")

            if (
                not request.user.groups.filter(name__in=group_names).exists()
                and not request.user.is_superuser
            ):
                messages.error(
                    request, "You do not have permission to access this page."
                )
                return redirect("rooms:room_list")

            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator
