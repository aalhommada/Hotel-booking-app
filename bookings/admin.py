
from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'room', 'check_in', 'check_out', 'status', 'total_price')
    list_filter = ('status', 'check_in', 'check_out')
    search_fields = ('user__username', 'room__name', 'room__number')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('user', 'room', 'check_in', 'check_out', 'status')
        }),
        ('Guest Information', {
            'fields': ('adults', 'children', 'special_requests')
        }),
        ('Financial', {
            'fields': ('total_price',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        # Make certain fields readonly after creation
        if obj:  # editing an existing object
            return self.readonly_fields + ('user', 'room', 'total_price')
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new booking
            # Calculate the total price based on the room price and duration
            days = (obj.check_out - obj.check_in).days
            obj.total_price = obj.room.price_per_night * days
        super().save_model(request, obj, form, change)

    class Media:
        css = {
            'all': ('css/admin-custom.css',)
        }
        js = ('js/admin-booking.js',)