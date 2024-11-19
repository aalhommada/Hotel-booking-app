from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from bookings.models import Booking
from rooms.models import Room

from .admin import BookingStatisticsAdmin
from .models import BookingStatistics


@staff_member_required
def dashboard_view(request):
    admin_instance = BookingStatisticsAdmin(BookingStatistics, None)
    context = admin_instance.get_chart_data()
    return render(request, "admin/analytics/dashboard.html", context)


@staff_member_required
def get_year_data(request, year):
    try:
        start_date = timezone.datetime(year, 1, 1).date()
        end_date = timezone.datetime(year, 12, 31).date()

        monthly_stats = (
            Booking.objects.filter(
                check_in__gte=start_date,
                check_in__lte=end_date,
                status__in=["confirmed", "completed"],
            )
            .annotate(month=TruncMonth("check_in"))
            .values("month")
            .annotate(revenue=Sum("total_price"), bookings=Count("id"))
            .order_by("month")
        )

        months = []
        for month in range(1, 13):
            months.append(
                {
                    "month": timezone.datetime(year, month, 1).date().strftime("%B %Y"),
                    "revenue": 0,
                    "bookings": 0,
                }
            )

        for stat in monthly_stats:
            month_index = stat["month"].month - 1
            months[month_index]["revenue"] = float(stat["revenue"] or 0)
            months[month_index]["bookings"] = stat["bookings"]

        total_rooms = Room.objects.filter(is_active=True).count()
        occupancy_data = None

        if total_rooms > 0:
            occupancy_stats = (
                Booking.objects.filter(
                    check_in__gte=start_date,
                    check_in__lte=end_date,
                    status__in=["confirmed", "completed"],
                )
                .annotate(month=TruncMonth("check_in"))
                .values("month")
                .annotate(
                    occupied_rooms=Count("room", distinct=True),
                )
                .order_by("month")
            )

            occupancy_rates = [0] * 12
            for stat in occupancy_stats:
                month_index = stat["month"].month - 1
                rate = (stat["occupied_rooms"] / total_rooms) * 100
                occupancy_rates[month_index] = round(rate, 2)

            occupancy_data = {
                "labels": [m["month"] for m in months],
                "rates": occupancy_rates,
            }

        return JsonResponse(
            {
                "chart_data": {
                    "labels": [m["month"] for m in months],
                    "revenue": [m["revenue"] for m in months],
                    "bookings": [m["bookings"] for m in months],
                },
                "occupancy_data": occupancy_data,
            }
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
