# analytics/tests.py
from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from bookings.models import Booking
from rooms.models import Room

from .models import BookingStatistics


@pytest.fixture
def staff_user():
    user = User.objects.create_superuser(
        username="staff", password="staff123", email="staff@example.com", is_staff=True
    )
    return user


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
def sample_bookings(test_room, staff_user):
    # Create bookings across different months
    bookings = []
    start_date = date(2024, 1, 1)

    for month in range(3):  # Create bookings for first 3 months
        booking = Booking.objects.create(
            user=staff_user,
            room=test_room,
            check_in=start_date + timedelta(days=30 * month),
            check_out=start_date + timedelta(days=(30 * month) + 2),
            adults=2,
            children=0,
            status="confirmed",
            total_price=Decimal("200.00"),
        )
        bookings.append(booking)

    return bookings


# Test T006: Manager Analytics
@pytest.mark.django_db
class TestAnalyticsDashboard:
    def test_dashboard_access(self, client, staff_user):
        """Test dashboard access for staff users"""
        client.login(username="staff", password="staff123")

        response = client.get(reverse("analytics:dashboard"))

        response = client.get(
            reverse("analytics:dashboard"),
        )

        assert response.status_code == 200

        assert response.status_code == 200
        assert "chart_data" in response.context

    def test_dashboard_unauthorized_access(self, client):
        """Test dashboard access restriction"""
        response = client.get(reverse("analytics:dashboard"))
        assert response.status_code == 302  # Redirect to login

    def test_yearly_revenue_data(self, client, staff_user, sample_bookings):
        """Test yearly revenue data calculation"""
        client.login(username="staff", password="staff123")

        response = client.get(reverse("analytics:year_data", kwargs={"year": 2024}))

        assert response.status_code == 200
        data = response.json()
        assert "chart_data" in data
        assert "revenue" in data["chart_data"]
        assert len(data["chart_data"]["revenue"]) == 12  # All months included

    def test_occupancy_calculation(self, client, staff_user, sample_bookings):
        """Test room occupancy rate calculation"""
        client.login(username="staff", password="staff123")

        response = client.get(reverse("analytics:year_data", kwargs={"year": 2024}))

        data = response.json()
        assert "occupancy_data" in data
        assert "rates" in data["occupancy_data"]

        # Test January occupancy (should be 100% as we have 1 room and 1 booking)
        january_rate = data["occupancy_data"]["rates"][0]
        assert january_rate == 100.0


@pytest.mark.django_db
class TestBookingStatistics:
    def test_statistics_creation(self, sample_bookings):
        """Test booking statistics creation"""
        date_to_test = date(2024, 1, 1)
        stats = BookingStatistics.update_or_create_stats(date_to_test)

        assert stats.total_bookings == 1
        assert stats.confirmed_bookings == 1
        assert stats.total_revenue == Decimal("200.00")
        assert stats.rooms_booked == 1

    def test_statistics_calculation(self, client, staff_user, sample_bookings):
        """Test statistics calculation in admin view"""
        client.login(username="staff", password="staff123")

        BookingStatistics.update_or_create_stats(date(2024, 1, 1))

        response = client.get(reverse("admin:analytics_bookingstatistics_changelist"))
        assert response.status_code == 200

        assert "available_years" in response.context
        assert 2024 in response.context["available_years"]

    def test_empty_data_handling(self, client, staff_user):
        """Test handling of periods with no bookings"""
        client.login(username="staff", password="staff123")

        response = client.get(reverse("analytics:year_data", kwargs={"year": 2023}))

        data = response.json()
        assert all(revenue == 0 for revenue in data["chart_data"]["revenue"])
        assert all(bookings == 0 for bookings in data["chart_data"]["bookings"])


@pytest.mark.django_db
class TestAnalyticsPerformance:
    def test_large_dataset_handling(self, client, staff_user, test_room):
        """Test handling of large number of bookings"""
        # Create 100 bookings
        start_date = date(2024, 1, 1)
        for i in range(100):
            Booking.objects.create(
                user=staff_user,
                room=test_room,
                check_in=start_date + timedelta(days=i),
                check_out=start_date + timedelta(days=i + 1),
                adults=2,
                status="confirmed",
                total_price=Decimal("100.00"),
            )

        client.login(username="staff", password="staff123")
        response = client.get(reverse("analytics:year_data", kwargs={"year": 2024}))

        assert response.status_code == 200
        data = response.json()
        assert "chart_data" in data
