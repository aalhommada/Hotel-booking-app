# rooms/models.py
from datetime import datetime

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit


class Room(models.Model):
    ROOM_TYPES = (
        ("single", "Single"),
        ("double", "Double"),
        ("suite", "Suite"),
        ("family", "Family"),
    )

    BED_TYPES = (
        ("single", "Single"),
        ("double", "Double"),
        ("queen", "Queen"),
        ("king", "King"),
    )

    name = models.CharField(max_length=100)
    room_number = models.CharField(max_length=10, unique=True)
    floor = models.IntegerField()
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    bed_type = models.CharField(max_length=20, choices=BED_TYPES)
    price_per_night = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    capacity_adults = models.IntegerField(validators=[MinValueValidator(1)])
    capacity_children = models.IntegerField(validators=[MinValueValidator(0)])
    description = models.TextField(blank=True)

    # Amenities
    has_wifi = models.BooleanField(default=True)
    has_ac = models.BooleanField(default=True)
    has_heating = models.BooleanField(default=True)
    has_tv = models.BooleanField(default=True)
    has_bathroom = models.BooleanField(default=True)
    has_balcony = models.BooleanField(default=False)
    has_minibar = models.BooleanField(default=False)
    has_desk = models.BooleanField(default=True)
    has_closet = models.BooleanField(default=True)
    has_safe = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - Room {self.room_number}"

    class Meta:
        ordering = ["room_number"]

    def check_availability(self, check_in_str, check_out_str):
        """Check if the room is available for the given dates"""
        try:
            check_in = datetime.strptime(check_in_str, "%Y-%m-%d").date()
            check_out = datetime.strptime(check_out_str, "%Y-%m-%d").date()

            if check_in >= check_out:
                raise ValueError("Check-out must be after check-in")

            if check_in < timezone.now().date():
                raise ValueError("Check-in cannot be in the past")

            # Check for overlapping bookings
            overlapping_bookings = self.booking_set.filter(
                check_in__lt=check_out,
                check_out__gt=check_in,
                status__in=["pending", "confirmed"],
            )

            return not overlapping_bookings.exists()

        except ValueError as e:
            raise ValueError(str(e))

    def get_primary_image(self):
        """Get the primary image or first image or None"""
        return self.images.filter(is_primary=True).first() or self.images.first()

    def get_gallery_images(self):
        """Get all images except primary for gallery"""
        primary_image = self.get_primary_image()
        if primary_image:
            return self.images.exclude(id=primary_image.id)
        return self.images.all()

    def get_amenities_list(self):
        """Get list of available amenities"""
        amenities = []
        if self.has_wifi:
            amenities.append(("WiFi", "wifi"))
        if self.has_ac:
            amenities.append(("Air Conditioning", "ac"))
        if self.has_heating:
            amenities.append(("Heating", "heat"))
        if self.has_tv:
            amenities.append(("TV", "tv"))
        if self.has_bathroom:
            amenities.append(("Private Bathroom", "bath"))
        if self.has_balcony:
            amenities.append(("Balcony", "balcony"))
        if self.has_minibar:
            amenities.append(("Minibar", "drink"))
        if self.has_desk:
            amenities.append(("Work Desk", "desk"))
        if self.has_closet:
            amenities.append(("Closet", "closet"))
        if self.has_safe:
            amenities.append(("Safe", "lock"))
        return amenities


class RoomImage(models.Model):
    IMAGE_FORMATS = (
        ("JPEG", "JPEG"),
        ("PNG", "PNG"),
        ("WEBP", "WebP"),
    )

    room = models.ForeignKey(Room, related_name="images", on_delete=models.CASCADE)
    image = ProcessedImageField(
        upload_to="room_images",
        processors=[ResizeToFit(1920, 1080)],
        format="JPEG",
        options={"quality": 85},
    )
    format = models.CharField(
        max_length=10,
        choices=IMAGE_FORMATS,
        default="JPEG",
        help_text="Select the output format for this image",
    )
    is_primary = models.BooleanField(default=False)
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "uploaded_at"]

    def __str__(self):
        return f"Image for {self.room.name} ({self.order})"

    def save(self, *args, **kwargs):
        # Set the image format based on the format field
        self.image.format = self.format

        if self.is_primary:
            # Ensure only one primary image per room
            RoomImage.objects.filter(room=self.room).exclude(pk=self.pk).update(
                is_primary=False
            )

        super().save(*args, **kwargs)
