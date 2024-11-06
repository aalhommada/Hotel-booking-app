from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

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

class RoomImage(models.Model):
    room = models.ForeignKey(Room, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='room_images/')
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    # Automatically generate thumbnails
    thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(300, 200)],
        format='JPEG',
        options={'quality': 60}
    )
    
    class Meta:
        ordering = ['order']

