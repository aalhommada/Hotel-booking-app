
from django import forms
from .models import Booking
from django.core.exceptions import ValidationError
from datetime import date

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['check_in', 'check_out', 'adults', 'children', 'special_requests']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date', 'min': date.today().isoformat()}),
            'check_out': forms.DateInput(attrs={'type': 'date', 'min': date.today().isoformat()}),
            'special_requests': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        room = self.instance.room if self.instance else None

        if check_in and check_out:
            if check_in >= check_out:
                raise ValidationError("Check-out date must be after check-in date")

            if check_in < date.today():
                raise ValidationError("Check-in date cannot be in the past")

            # Check if room is available for these dates
            if room:
                overlapping_bookings = Booking.objects.filter(
                    room=room,
                    check_in__lte=check_out,
                    check_out__gte=check_in
                ).exclude(pk=self.instance.pk if self.instance else None)

                if overlapping_bookings.exists():
                    raise ValidationError("Room is not available for selected dates")

        return cleaned_data
    
from django import forms
from .models import Booking
from django.utils import timezone

class BookingCreateForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['check_in', 'check_out', 'adults', 'children', 'special_requests']
        widgets = {
            'check_in': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                    'min': timezone.now().date().isoformat()
                }
            ),
            'check_out': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                    'min': timezone.now().date().isoformat()
                }
            ),
            'special_requests': forms.Textarea(
                attrs={
                    'rows': 3,
                    'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                    'placeholder': 'Any special requests?'
                }
            )
        }

    def __init__(self, room=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if room:
            self.room = room
            self.fields['adults'].widget.attrs.update({
                'max': room.capacity_adults,
                'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            })
            self.fields['children'].widget.attrs.update({
                'max': room.capacity_children,
                'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            })

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        adults = cleaned_data.get('adults')
        children = cleaned_data.get('children')

        if all([check_in, check_out, adults]):
            if check_in >= check_out:
                raise forms.ValidationError("Check-out date must be after check-in date")

            if check_in < timezone.now().date():
                raise forms.ValidationError("Check-in date cannot be in the past")

            if hasattr(self, 'room'):
                if adults > self.room.capacity_adults:
                    raise forms.ValidationError("Number of adults exceeds room capacity")
                
                if children and children > self.room.capacity_children:
                    raise forms.ValidationError("Number of children exceeds room capacity")

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