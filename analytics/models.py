from django.db import models

from bookings.models import Booking


class BookingStatistics(models.Model):
    date = models.DateField(unique=True)
    total_bookings = models.IntegerField(default=0)
    confirmed_bookings = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rooms_booked = models.IntegerField(default=0)
    average_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Booking Statistics"

    def __str__(self):
        return f"Stats for {self.date}"

    @classmethod
    def update_or_create_stats(cls, date):
        """Update or create statistics for a given date"""
        bookings = Booking.objects.filter(
            check_in__lte=date,
            check_out__gt=date,
            status__in=["confirmed", "completed"],
        )

        stats, _ = cls.objects.update_or_create(
            date=date,
            defaults={
                "total_bookings": bookings.count(),
                "confirmed_bookings": bookings.filter(status="confirmed").count(),
                "total_revenue": sum(b.total_price for b in bookings),
                "rooms_booked": bookings.values("room").distinct().count(),
                "average_price": (
                    sum(b.total_price for b in bookings) / bookings.count()
                    if bookings.exists()
                    else 0
                ),
            },
        )
        return stats
