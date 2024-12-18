# core/context_processors.py
from datetime import date

from .models import Notification


def notifications_processor(request):
    unread_count = 0
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            user=request.user, read=False
        ).count()
    return {"unread_notifications_count": unread_count}


def date_processor(request):
    return {
        "today": date.today(),
    }
