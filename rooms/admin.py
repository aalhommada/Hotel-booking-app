# rooms/admin.py
from django.contrib import admin
from .models import Room, RoomImage

class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'name', 'room_type', 'price_per_night', 'is_active']  
    list_filter = ['room_type', 'is_active']
    search_fields = ['name', 'room_number']
    inlines = [RoomImageInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('room_number', 'name', 'room_type', 'bed_type', 'floor', 'price_per_night')
        }),
        ('Capacity', {
            'fields': ('capacity_adults', 'capacity_children')
        }),
        ('Amenities', {
            'fields': (
                'has_wifi', 'has_ac', 'has_heating', 'has_tv', 'has_bathroom',
                'has_minibar', 'has_safe', 'has_desk', 'has_closet', 
                'has_balcony'
            )
        }),
        ('Additional Info', {
            'fields': ('description', 'is_active')
        }),
    )