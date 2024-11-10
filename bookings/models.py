# bookings/models.py
from datetime import datetime
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from rooms.models import Room

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    adults = models.PositiveIntegerField()
    children = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    special_requests = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking {self.id} - {self.user.username} - {self.room.name}"

    def clean(self):
        if not hasattr(self, 'room') or not self.room:
            raise ValidationError("Room is required")
            
        if self.check_in and self.check_out:
            if self.check_in >= self.check_out:
                raise ValidationError("Check-out date must be after check-in date")
            
            if isinstance(self.check_in, str):
                self.check_in = datetime.strptime(self.check_in, "%Y-%m-%d").date()

            if self.check_in < timezone.now().date():
                raise ValidationError("Check-in date cannot be in the past")
            
            # Check room capacity
            if hasattr(self, 'adults') and self.adults:
                if int(self.adults) > self.room.capacity_adults:
                    raise ValidationError("Number of adults exceeds room capacity")
            
            if hasattr(self, 'children') and self.children:
                if int(self.children) > self.room.capacity_children:
                    raise ValidationError("Number of children exceeds room capacity")
            
            # Check for overlapping bookings
            overlapping_bookings = Booking.objects.filter(
                room=self.room,
                check_in__lt=self.check_out,
                check_out__gt=self.check_in,
                status__in=['pending', 'confirmed']
            ).exclude(pk=self.pk)
            
            if overlapping_bookings.exists():
                raise ValidationError("Room is not available for selected dates")

    def calculate_total_price(self):
        """Calculate total price based on room price and duration"""
        if hasattr(self, 'room') and self.check_in and self.check_out:
            days = (self.check_out - self.check_in).days
            return self.room.price_per_night * Decimal(days)
        return Decimal('0')

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)

    @property
    def duration(self):
        """Calculate booking duration in days"""
        return (self.check_out - self.check_in).days

    @property
    def is_past(self):
        """Check if booking is in the past"""
        return self.check_out < timezone.now().date()

    @property
    def can_be_cancelled(self):
        """Check if booking can be cancelled"""
        return (
            self.status in ['pending', 'confirmed'] and 
            not self.is_past and 
            self.check_in > timezone.now().date()
        )