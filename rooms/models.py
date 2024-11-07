from django.db import models
from django.utils import timezone
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit

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
    
    number = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    bed_type = models.CharField(max_length=20, choices=BED_TYPES)
    floor = models.IntegerField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    capacity_adults = models.IntegerField()
    capacity_children = models.IntegerField()
    
    # Amenities
    has_wifi = models.BooleanField(default=True)
    has_ac = models.BooleanField(default=True)
    has_heating = models.BooleanField(default=True)
    has_tv = models.BooleanField(default=True)
    has_bathroom = models.BooleanField(default=True)
    has_bathtub = models.BooleanField(default=False)
    has_shower = models.BooleanField(default=True)
    has_minibar = models.BooleanField(default=False)
    has_safe = models.BooleanField(default=False)
    has_desk = models.BooleanField(default=True)
    has_wardrobe = models.BooleanField(default=True)
    has_coffee_maker = models.BooleanField(default=False)
    has_balcony = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - Room {self.number}"
    

    def get_amenities(self):
        """Returns a list of active amenities"""
        amenities = []
        if self.has_wifi: amenities.append('WiFi')
        if self.has_ac: amenities.append('Air Conditioning')
        if self.has_heating: amenities.append('Heating')
        if self.has_tv: amenities.append('TV')
        if self.has_bathroom: amenities.append('Private Bathroom')
        if self.has_balcony: amenities.append('Balcony')
        if self.has_minibar: amenities.append('Minibar')
        if self.has_desk: amenities.append('Work Desk')
        if self.has_closet: amenities.append('Closet')
        if self.has_safe: amenities.append('Safe')
        return amenities

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

