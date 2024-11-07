from django import forms
from .models import Room, RoomImage

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = [
            'name', 'room_number', 'floor', 'room_type', 'bed_type',
            'price_per_night', 'capacity_adults', 'capacity_children',
            'description', 'has_wifi', 'has_ac', 'has_heating', 'has_tv',
            'has_bathroom', 'has_balcony', 'has_minibar', 'has_desk',
            'has_closet', 'has_safe', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price_per_night': forms.NumberInput(attrs={'min': 0, 'step': 0.01}),
            'capacity_adults': forms.NumberInput(attrs={'min': 1}),
            'capacity_children': forms.NumberInput(attrs={'min': 0}),
        }

class RoomImageForm(forms.ModelForm):
    class Meta:
        model = RoomImage
        fields = ['image', 'is_primary', 'caption', 'order']
        widgets = {
            'order': forms.NumberInput(attrs={'min': 0}),
        }

RoomImageFormSet = forms.inlineformset_factory(
    Room,
    RoomImage,
    form=RoomImageForm,
    extra=1,
    can_delete=True
)