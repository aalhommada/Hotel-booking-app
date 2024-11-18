from datetime import timedelta

from django.contrib import admin
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from unfold.admin import ModelAdmin

from bookings.models import Booking
from rooms.models import Room

from .models import BookingStatistics


@admin.register(BookingStatistics)
class BookingStatisticsAdmin(ModelAdmin):
    change_list_template = "admin/analytics/bookingstatistics/change_list.html"
    list_display = [
        "date",
        "total_bookings",
        "confirmed_bookings",
        "total_revenue",
        "rooms_booked",
        "average_price",
    ]
    list_filter = ["date"]
    ordering = ["-date"]

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)

        try:
            # Get last 12 months of data
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=365)

            # Monthly revenue and bookings data
            monthly_stats = (
                Booking.objects.filter(
                    check_in__gte=start_date, status__in=["confirmed", "completed"]
                )
                .annotate(month=TruncMonth("check_in"))
                .values("month")
                .annotate(revenue=Sum("total_price"), bookings=Count("id"))
                .order_by("month")
            )

            # Initialize all months with zero values
            months = []
            current_date = start_date.replace(day=1)
            while current_date <= end_date:
                months.append({"month": current_date, "revenue": 0, "bookings": 0})
                current_date = (current_date + timedelta(days=32)).replace(day=1)

            # Update months with actual data
            stats_dict = {stat["month"]: stat for stat in monthly_stats}

            for month in months:
                if month["month"] in stats_dict:
                    month["revenue"] = float(stats_dict[month["month"]]["revenue"])
                    month["bookings"] = stats_dict[month["month"]]["bookings"]

            # Prepare chart data
            chart_data = {
                "labels": [month["month"].strftime("%B %Y") for month in months],
                "revenue": [month["revenue"] for month in months],
                "bookings": [month["bookings"] for month in months],
            }

            total_rooms = Room.objects.filter(is_active=True).count()
            if total_rooms > 0:
                occupancy_stats = (
                    Booking.objects.filter(
                        check_in__gte=start_date, status__in=["confirmed", "completed"]
                    )
                    .annotate(month=TruncMonth("check_in"))
                    .values("month")
                    .annotate(
                        occupied_rooms=Count("room", distinct=True),
                    )
                    .order_by("month")
                )

                occupancy_data = {"labels": chart_data["labels"], "rates": []}

                stats_dict = {
                    stat["month"]: stat["occupied_rooms"] for stat in occupancy_stats
                }

                for month in months:
                    occupied = stats_dict.get(month["month"], 0)
                    rate = (occupied / total_rooms) * 100
                    occupancy_data["rates"].append(round(rate, 2))

                response.context_data["occupancy_data"] = occupancy_data

            response.context_data["chart_data"] = chart_data

        except (AttributeError, KeyError):
            pass

        return response
