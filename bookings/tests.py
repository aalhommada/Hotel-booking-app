from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone

from rooms.models import Room

from .models import Booking


@pytest.fixture
def test_user():
    return User.objects.create_user(
        username="testuser", password="testpass123", email="test@example.com"
    )


@pytest.fixture
def test_room():
    return Room.objects.create(
        name="Test Room",
        room_number="101",
        floor=1,
        room_type="double",
        bed_type="queen",
        price_per_night=Decimal("100.00"),
        capacity_adults=2,
        capacity_children=1,
        is_active=True,
    )


@pytest.fixture
def valid_booking_data():
    tomorrow = timezone.now().date() + timedelta(days=1)
    return {
        "check_in": tomorrow.strftime("%Y-%m-%d"),
        "check_out": (tomorrow + timedelta(days=2)).strftime("%Y-%m-%d"),
        "adults": 2,
        "children": 1,
        "special_requests": "Test request",
    }


# Test T003: Booking Process
@pytest.mark.django_db
class TestBookingProcess:
    def test_create_booking(self, client, test_user, test_room, valid_booking_data):
        """Test complete booking creation process"""
        client.login(username="testuser", password="testpass123")

        # Add room to the booking data
        data = valid_booking_data.copy()
        data["room"] = test_room.pk

        print("\nTest Data:")
        print(f"Room: {test_room.pk} - {test_room.name}")
        print(f"User: {test_user.username}")
        print(f"Booking Data: {data}")

        url = reverse("bookings:booking_create", kwargs={"room_pk": test_room.pk})

        # Make the request
        response = client.post(url, data, follow=True)

        print(f"\nResponse Status: {response.status_code}")
        if response.context and "form" in response.context:
            form = response.context["form"]
            print(f"Form Errors: {form.errors}")
            print(f"Form Data: {form.data}")
            print(f"Form Room: {form.room}")
            print(f"Form Instance Room: {getattr(form.instance, 'room', None)}")

        booking = Booking.objects.filter(
            user=test_user,
            room=test_room,
            check_in=data["check_in"],
            check_out=data["check_out"],
        ).first()

        assert booking is not None
        assert booking.user == test_user
        assert booking.room == test_room
        assert booking.status == "pending"
        assert booking.total_price == test_room.price_per_night * 2

    def test_booking_with_invalid_dates(self, client, test_user, test_room):
        """Test booking with invalid dates"""
        client.login(username="testuser", password="testpass123")

        yesterday = timezone.now().date() - timedelta(days=1)
        invalid_data = {
            "check_in": yesterday.strftime("%Y-%m-%d"),
            "check_out": timezone.now().date().strftime("%Y-%m-%d"),
            "adults": 2,
            "children": 1,
        }

        response = client.post(
            reverse("bookings:booking_create", kwargs={"room_pk": test_room.pk}),
            invalid_data,
        )

        assert response.status_code == 200  # Form redisplay
        assert Booking.objects.count() == 0

    def test_booking_with_overlapping_dates(
        self, client, test_user, test_room, valid_booking_data
    ):
        """Test booking with overlapping dates"""
        # Convert string dates back to date objects for creating initial booking
        check_in = timezone.datetime.strptime(
            valid_booking_data["check_in"], "%Y-%m-%d"
        ).date()
        check_out = timezone.datetime.strptime(
            valid_booking_data["check_out"], "%Y-%m-%d"
        ).date()

        # Create initial booking
        Booking.objects.create(
            user=test_user,
            room=test_room,
            check_in=check_in,
            check_out=check_out,
            adults=valid_booking_data["adults"],
            children=valid_booking_data["children"],
            status="confirmed",
            total_price=test_room.price_per_night * 2,
        )

        client.login(username="testuser", password="testpass123")

        response = client.post(
            reverse("bookings:booking_create", kwargs={"room_pk": test_room.pk}),
            valid_booking_data,
        )

        assert response.status_code == 200  # Form redisplay
        assert Booking.objects.count() == 1  # No new booking created

    def test_booking_view_availability(self, client, test_room):
        """Test room availability check"""
        tomorrow = timezone.now().date() + timedelta(days=1)
        next_week = tomorrow + timedelta(days=7)

        response = client.get(
            reverse("bookings:check_availability", kwargs={"room_pk": test_room.pk}),
            {
                "check_in": tomorrow.strftime("%Y-%m-%d"),
                "check_out": next_week.strftime("%Y-%m-%d"),
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["available"] is True

    def test_invalid_capacity(self, client, test_user, test_room, valid_booking_data):
        """Test booking with invalid capacity"""
        client.login(username="testuser", password="testpass123")

        data = valid_booking_data.copy()
        data["adults"] = test_room.capacity_adults + 1

        response = client.post(
            reverse("bookings:booking_create", kwargs={"room_pk": test_room.pk}), data
        )

        assert response.status_code == 200
        assert Booking.objects.count() == 0


@pytest.mark.django_db
class TestBookingManagement:
    def test_booking_list_view(self, client, test_user):
        """Test booking list view"""
        client.login(username="testuser", password="testpass123")
        response = client.get(reverse("bookings:booking_list"))

        assert response.status_code == 200
        assert "bookings" in response.context

    def test_booking_detail_view(
        self, client, test_user, test_room, valid_booking_data
    ):
        """Test booking detail view"""
        check_in = timezone.datetime.strptime(
            valid_booking_data["check_in"], "%Y-%m-%d"
        ).date()
        check_out = timezone.datetime.strptime(
            valid_booking_data["check_out"], "%Y-%m-%d"
        ).date()

        booking = Booking.objects.create(
            user=test_user,
            room=test_room,
            check_in=check_in,
            check_out=check_out,
            adults=valid_booking_data["adults"],
            children=valid_booking_data["children"],
            status="confirmed",
            total_price=test_room.price_per_night * 2,
        )

        client.login(username="testuser", password="testpass123")
        response = client.get(
            reverse("bookings:booking_detail", kwargs={"pk": booking.pk})
        )

        assert response.status_code == 200
        assert response.context["booking"] == booking

    def test_booking_cancellation(
        self, client, test_user, test_room, valid_booking_data
    ):
        """Test booking cancellation"""
        check_in = timezone.datetime.strptime(
            valid_booking_data["check_in"], "%Y-%m-%d"
        ).date()
        check_out = timezone.datetime.strptime(
            valid_booking_data["check_out"], "%Y-%m-%d"
        ).date()

        booking = Booking.objects.create(
            user=test_user,
            room=test_room,
            check_in=check_in,
            check_out=check_out,
            adults=valid_booking_data["adults"],
            children=valid_booking_data["children"],
            status="confirmed",
            total_price=test_room.price_per_night * 2,
        )

        client.login(username="testuser", password="testpass123")
        response = client.post(
            reverse("bookings:booking_cancel", kwargs={"pk": booking.pk})
        )

        booking.refresh_from_db()
        assert response.status_code == 302
        assert booking.status == "cancelled"


@pytest.mark.django_db
class TestBookingModel:
    def test_booking_clean_method(self, test_user, test_room, valid_booking_data):
        """Test booking model validation"""
        check_in = timezone.datetime.strptime(
            valid_booking_data["check_in"], "%Y-%m-%d"
        ).date()
        check_out = timezone.datetime.strptime(
            valid_booking_data["check_out"], "%Y-%m-%d"
        ).date()

        booking = Booking(
            user=test_user,
            room=test_room,
            check_in=check_in,
            check_out=check_out,
            adults=valid_booking_data["adults"],
            children=valid_booking_data["children"],
            total_price=test_room.price_per_night * 2,
        )

        booking.clean()  # Should not raise ValidationError

        # Test invalid dates
        booking.check_in = timezone.now().date() - timedelta(days=1)
        with pytest.raises(ValidationError):
            booking.clean()

    def test_booking_price_calculation(self, test_user, test_room, valid_booking_data):
        """Test total price calculation"""
        check_in = timezone.datetime.strptime(
            valid_booking_data["check_in"], "%Y-%m-%d"
        ).date()
        check_out = timezone.datetime.strptime(
            valid_booking_data["check_out"], "%Y-%m-%d"
        ).date()

        booking = Booking.objects.create(
            user=test_user,
            room=test_room,
            check_in=check_in,
            check_out=check_out,
            adults=valid_booking_data["adults"],
            children=valid_booking_data["children"],
            status="confirmed",
            total_price=0,  # Will be calculated on save
        )

        expected_price = test_room.price_per_night * 2  # 2 nights
        assert booking.total_price == expected_price
