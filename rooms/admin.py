
from django.contrib import admin
from .models import Room, RoomImage

class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'room_type', 'price_per_night', 'capacity_adults', 'capacity_children')
    list_filter = ('room_type', 'bed_type', 'floor')
    search_fields = ('number', 'name')
    inlines = [RoomImageInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('number', 'name', 'room_type', 'bed_type', 'floor', 'price_per_night')
        }),
        ('Capacity', {
            'fields': ('capacity_adults', 'capacity_children')
        }),
        ('Amenities', {
            'fields': (
                'has_wifi', 'has_ac', 'has_heating', 'has_tv', 'has_bathroom',
                'has_bathtub', 'has_shower', 'has_minibar', 'has_safe',
                'has_desk', 'has_wardrobe', 'has_coffee_maker', 'has_balcony'
            )
        }),
    )