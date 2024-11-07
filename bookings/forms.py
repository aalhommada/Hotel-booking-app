
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