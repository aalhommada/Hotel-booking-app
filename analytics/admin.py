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
        extra_context = extra_context or {}

        try:
            # Get selected year from request, defaulting to current year
            selected_year = request.GET.get("selected_year")
            selected_year = (
                int(selected_year)
                if selected_year and selected_year.isdigit()
                else timezone.now().year
            )

            # Get available years from actual bookings
            available_years = list(
                Booking.objects.dates("check_in", "year")
                .values_list("check_in__year", flat=True)
                .distinct()
            )

            # Ensure current year is always available
            current_year = timezone.now().year
            if current_year not in available_years:
                available_years.append(current_year)

            # Sort years in descending order
            available_years.sort(reverse=True)

            # Set date range for selected year
            start_date = timezone.datetime(selected_year, 1, 1).date()
            end_date = timezone.datetime(selected_year, 12, 31).date()

            # Get monthly stats
            monthly_stats = (
                Booking.objects.filter(
                    check_in__gte=start_date,
                    check_in__lte=end_date,
                    status__in=["confirmed", "completed"],
                )
                .annotate(month=TruncMonth("check_in"))
                .values("month")
                .annotate(revenue=Sum("total_price", default=0), bookings=Count("id"))
                .order_by("month")
            )

            # Initialize all months
            months = [
                {
                    "month": timezone.datetime(selected_year, month, 1).date(),
                    "revenue": 0,
                    "bookings": 0,
                }
                for month in range(1, 13)
            ]

            # Update with actual data
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

            # Calculate occupancy if rooms exist
            total_rooms = Room.objects.filter(is_active=True).count()
            if total_rooms > 0:
                occupancy_stats = (
                    Booking.objects.filter(
                        check_in__gte=start_date,
                        check_in__lte=end_date,
                        status__in=["confirmed", "completed"],
                    )
                    .annotate(month=TruncMonth("check_in"))
                    .values("month")
                    .annotate(occupied_rooms=Count("room", distinct=True))
                    .order_by("month")
                )

                occupancy_data = {"labels": chart_data["labels"], "rates": []}

                # Create occupancy stats dictionary
                occupancy_dict = {
                    stat["month"]: stat["occupied_rooms"] for stat in occupancy_stats
                }

                # Calculate rates for all months
                for month in months:
                    occupied = occupancy_dict.get(month["month"], 0)
                    rate = (occupied / total_rooms) * 100
                    occupancy_data["rates"].append(round(rate, 2))

                extra_context["occupancy_data"] = occupancy_data

            # Update context
            extra_context.update(
                {
                    "chart_data": chart_data,
                    "available_years": available_years,
                    "selected_year": selected_year,
                }
            )

        except Exception as e:
            print(f"Error in changelist_view: {e}")
            # Provide default empty data
            extra_context.update(
                {
                    "chart_data": {"labels": [], "revenue": [], "bookings": []},
                    "available_years": [timezone.now().year],
                    "selected_year": timezone.now().year,
                    "occupancy_data": {"labels": [], "rates": []},
                }
            )

        return super().changelist_view(request, extra_context=extra_context)

    def get_chart_data(self):
        try:
            # Default to current year
            selected_year = timezone.now().year

            # Set date range for selected year
            start_date = timezone.datetime(selected_year, 1, 1).date()
            end_date = timezone.datetime(selected_year, 12, 31).date()

            # Get monthly stats
            monthly_stats = (
                Booking.objects.filter(
                    check_in__gte=start_date,
                    check_in__lte=end_date,
                    status__in=["confirmed", "completed"],
                )
                .annotate(month=TruncMonth("check_in"))
                .values("month")
                .annotate(revenue=Sum("total_price", default=0), bookings=Count("id"))
                .order_by("month")
            )

            # Initialize all months
            months = [
                {
                    "month": timezone.datetime(selected_year, month, 1).date(),
                    "revenue": 0,
                    "bookings": 0,
                }
                for month in range(1, 13)
            ]

            # Update with actual data
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

            # Calculate occupancy
            total_rooms = Room.objects.filter(is_active=True).count()
            if total_rooms > 0:
                occupancy_stats = (
                    Booking.objects.filter(
                        check_in__gte=start_date,
                        check_in__lte=end_date,
                        status__in=["confirmed", "completed"],
                    )
                    .annotate(month=TruncMonth("check_in"))
                    .values("month")
                    .annotate(occupied_rooms=Count("room", distinct=True))
                    .order_by("month")
                )

                occupancy_data = {"labels": chart_data["labels"], "rates": []}

                # Create occupancy stats dictionary
                occupancy_dict = {
                    stat["month"]: stat["occupied_rooms"] for stat in occupancy_stats
                }

                # Calculate rates for all months
                for month in months:
                    occupied = occupancy_dict.get(month["month"], 0)
                    rate = (occupied / total_rooms) * 100
                    occupancy_data["rates"].append(round(rate, 2))

                chart_data["occupancy_data"] = occupancy_data

            return {"chart_data": chart_data}

        except Exception as e:
            print(f"Error in get_chart_data: {e}")
            return {
                "chart_data": {
                    "labels": [],
                    "revenue": [],
                    "bookings": [],
                    "occupancy_data": {"labels": [], "rates": []},
                }
            }
