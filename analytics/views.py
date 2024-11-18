from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from .admin import BookingStatisticsAdmin


@staff_member_required
def dashboard_view(request):
    admin_instance = BookingStatisticsAdmin(BookingStatisticsAdmin.model, None)
    context = admin_instance.get_chart_data()
    return render(request, "admin/analytics/dashboard.html", context)
