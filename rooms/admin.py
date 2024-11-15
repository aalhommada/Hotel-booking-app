# rooms/admin.py
from typing import Any

from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from .constants import AMENITY_FIELDS
from .models import Room, RoomImage


class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1
    fields = ("image", "format", "is_primary", "caption", "order")


@admin.register(Room)
class RoomAdmin(ModelAdmin):
    list_display = [
        "room_number",
        "name",
        "room_type",
        "price_per_night",
        "is_active",
        "image_preview",
    ]
    list_filter = ["room_type", "is_active", "bed_type", "floor"]
    search_fields = ["name", "room_number", "description"]
    inlines = [RoomImageInline]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "room_number",
                    "name",
                    "room_type",
                    "bed_type",
                    "floor",
                    "price_per_night",
                )
            },
        ),
        ("Capacity", {"fields": ("capacity_adults", "capacity_children")}),
        (
            "Amenities",
            {"fields": AMENITY_FIELDS},
        ),
        ("Additional Info", {"fields": ("description", "is_active")}),
    )

    def image_preview(self, obj: Any) -> str:
        primary_image = obj.get_primary_image()
        if primary_image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 100px;"/>',
                primary_image.image.url,
            )
        return "No image"

    image_preview.short_description = "Preview"  # type: ignore

    class Media:
        css = {"all": ("admin/css/custom_admin.css",)}
