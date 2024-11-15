# bookings/admin.py
from typing import Any

from django.contrib import admin
from django.utils.html import format_html
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

    def guest_info(self, obj: Any) -> str:
        return format_html(
            "<strong>{}</strong><br/><small>{}</small>",
            obj.user.get_full_name() or obj.user.username,
            obj.user.email,
        )

    guest_info.short_description = "Guest"  # type: ignore

    def room_info(self, obj):
        return format_html(
            "<strong>{}</strong><br/><small>Room {}</small>",
            obj.room.name,
            obj.room.room_number,
        )

    room_info.short_description = "Room"  # type: ignore

    def date_info(self, obj):
        return format_html(
            "<strong>{}</strong> to <strong>{}</strong><br/><small>{} nights</small>",
            obj.check_in.strftime("%Y-%m-%d"),
            obj.check_out.strftime("%Y-%m-%d"),
            obj.duration,
        )

    date_info.short_description = "Dates"  # type: ignore
