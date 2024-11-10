# bookings/forms.py
from django import forms
from .models import Booking
from django.core.exceptions import ValidationError
from datetime import datetime

class BookingCreateForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['check_in', 'check_out', 'adults', 'children', 'special_requests']
        widgets = {
            'room': forms.HiddenInput(),
            'check_in': forms.DateInput(attrs={
                'type': 'date',
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }),
            'check_out': forms.DateInput(attrs={
                'type': 'date',
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }),
            'adults': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }),
            'children': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }),
            'special_requests': forms.Textarea(attrs={
                'rows': 3,
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            })
        }

    def __init__(self, *args, **kwargs):
        self.room = kwargs.pop('room', None)
        super().__init__(*args, **kwargs)
        if self.room:
            self.fields['adults'].widget.attrs.update({
                'min': '1',
                'max': str(self.room.capacity_adults)
            })
            self.fields['children'].widget.attrs.update({
                'min': '0',
                'max': str(self.room.capacity_children)
            })

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        adults = cleaned_data.get('adults')
        children = cleaned_data.get('children', 0)

        if check_in and check_out:
            if check_in >= check_out:
                raise ValidationError("Check-out must be after check-in date")

            if check_in < datetime.now().date():
                raise ValidationError("Check-in cannot be in the past")

            if self.room:
                # Check room capacity
                if adults > self.room.capacity_adults:
                    raise ValidationError("Number of adults exceeds room capacity")
                if children > self.room.capacity_children:
                    raise ValidationError("Number of children exceeds room capacity")

                # Check availability
                overlapping_bookings = Booking.objects.filter(
                    room=self.room,
                    check_in__lt=check_out,
                    check_out__gt=check_in,
                    status__in=['pending', 'confirmed']
                ).exclude(pk=self.instance.pk if self.instance else None)

                if overlapping_bookings.exists():
                    raise ValidationError("Room is not available for selected dates")

                # Calculate total price
                days = (check_out - check_in).days
                self.instance.total_price = self.room.price_per_night * days

        return cleaned_data

class BookingUpdateForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['special_requests']
        widgets = {
            'special_requests': forms.Textarea(
                attrs={
                    'rows': 3,
                    'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
                }
            )
        }