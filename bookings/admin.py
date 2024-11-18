from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(ModelAdmin):
    list_display = [
        "id",
        "guest_info",
        "room_info",
        "date_info",
        "status",
        "total_price",
        "created_at",
        "view_analytics",  # Add analytics link column
    ]
    list_filter = ["status", "created_at", "check_in", "check_out"]
    search_fields = ["user__email", "user__username", "room__name", "room__room_number"]
    readonly_fields = ["created_at", "updated_at", "total_price"]

    fieldsets = (
        (
            "Booking Information",
            {
                "fields": (
                    "user",
                    "room",
                    "status",
                    "total_price",
                    ("check_in", "check_out"),
                    ("adults", "children"),
                )
            },
        ),
        ("Additional Information", {"fields": ("special_requests",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def guest_info(self, obj) -> str:
        """Format guest information for display."""
        return format_html(
            "<strong>{}</strong><br/><small>{}</small>",
            obj.user.get_full_name() or obj.user.username,
            obj.user.email,
        )

    guest_info.short_description = "Guest"

    def room_info(self, obj):
        """Format room information for display."""
        return format_html(
            "<strong>{}</strong><br/><small>Room {}</small>",
            obj.room.name,
            obj.room.room_number,
        )

    room_info.short_description = "Room"

    def date_info(self, obj):
        """Format booking dates information for display."""
        return format_html(
            "<strong>{}</strong> to <strong>{}</strong><br/><small>{} nights</small>",
            obj.check_in.strftime("%Y-%m-%d"),
            obj.check_out.strftime("%Y-%m-%d"),
            obj.duration,
        )

    date_info.short_description = "Dates"

    def view_analytics(self, obj=None):
        """Add a link to analytics dashboard."""
        url = reverse("admin:analytics_bookingstatistics_changelist")
        return mark_safe(
            f'<a href="{url}" class="button" style="white-space: nowrap;">View Analytics</a>'
        )

    view_analytics.short_description = "Analytics"
    view_analytics.allow_tags = True
