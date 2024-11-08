from django.db import models
from django.utils import timezone
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
from django.core.validators import MinValueValidator


class Room(models.Model):
    ROOM_TYPES = (
        ('single', 'Single'),
        ('double', 'Double'),
        ('suite', 'Suite'),
        ('family', 'Family'),
    )
    
    BED_TYPES = (
        ('single', 'Single'),
        ('double', 'Double'),
        ('queen', 'Queen'),
        ('king', 'King'),
    )

    name = models.CharField(max_length=100)
    room_number = models.CharField(max_length=10, unique=True)  # Added this field
    floor = models.IntegerField()
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    bed_type = models.CharField(max_length=20, choices=BED_TYPES)
    price_per_night = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    capacity_adults = models.IntegerField(validators=[MinValueValidator(1)])
    capacity_children = models.IntegerField(validators=[MinValueValidator(0)])
    description = models.TextField(blank=True)  # Added this field
    
    # Amenities
    has_wifi = models.BooleanField(default=True)
    has_ac = models.BooleanField(default=True)
    has_heating = models.BooleanField(default=True)
    has_tv = models.BooleanField(default=True)
    has_bathroom = models.BooleanField(default=True)
    has_balcony = models.BooleanField(default=False)
    has_minibar = models.BooleanField(default=False)
    has_desk = models.BooleanField(default=True)
    has_closet = models.BooleanField(default=True)  # Added this field
    has_safe = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)  # Added this field
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - Room {self.room_number}"

    class Meta:
        ordering = ['room_number']
class RoomImage(models.Model):
    IMAGE_FORMATS = (
        ('JPEG', 'JPEG'),
        ('PNG', 'PNG'),
        ('WebP', 'WebP'),
        ('GIF', 'GIF'),
    )

    room = models.ForeignKey(Room, related_name='images', on_delete=models.CASCADE)
    image = ProcessedImageField(
        upload_to='room_images',
        processors=[ResizeToFit(1920, 1080)],
        format=models.CharField(
            max_length=10, 
            choices=IMAGE_FORMATS, 
            default='JPEG'
        ),
        options={'quality': 85}
    )
    image_format = models.CharField(
        max_length=10, 
        choices=IMAGE_FORMATS, 
        default='JPEG'
    )
    is_primary = models.BooleanField(default=False)
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['order', 'uploaded_at']

    def save(self, *args, **kwargs):
        if self.is_primary:
            # Ensure only one primary image per room
            RoomImage.objects.filter(room=self.room).exclude(pk=self.pk).update(is_primary=False)
        # Set the image format based on the selection
        self.image.format = self.image_format
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.room.name} ({self.order})"

