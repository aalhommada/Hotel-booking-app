# core/tests.py
from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from bookings.models import Booking
from rooms.models import Room

from .models import Contact, Notification


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        username="admin", password="admin123", email="admin@example.com"
    )


@pytest.fixture
def manager_user():
    user = User.objects.create_user(
        username="manager",
        password="manager123",
        email="manager@example.com",
        is_staff=True,
    )
    from django.contrib.auth.models import Group

    managers_group, _ = Group.objects.get_or_create(name="Managers")
    user.groups.add(managers_group)

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
def test_booking(admin_user, test_room):
    return Booking.objects.create(
        user=admin_user,
        room=test_room,
        check_in=timezone.now().date(),
        check_out=timezone.now().date() + timedelta(days=2),
        adults=2,
        children=0,
        status="confirmed",
        total_price=Decimal("200.00"),
    )


@pytest.mark.django_db
class TestDashboard:
    def test_admin_dashboard_access(self, client, admin_user):
        """Test dashboard access for admin"""
        client.login(username="admin", password="admin123")
        response = client.get(reverse("core:dashboard"))

        assert response.status_code == 200
        assert "total_rooms" in response.context
        assert "available_rooms" in response.context

    def test_manager_dashboard_access(self, client, manager_user):
        """Test dashboard access for manager"""
        client.login(username="manager", password="manager123")
        response = client.get(reverse("core:dashboard"))

        assert response.status_code == 200

    def test_unauthorized_dashboard_access(self, client):
        """Test dashboard access restriction"""
        response = client.get(reverse("core:dashboard"))
        assert response.status_code == 302  # Redirect to login

    def test_dashboard_statistics(self, client, admin_user, test_room, test_booking):
        """Test dashboard statistics calculation"""
        client.login(username="admin", password="admin123")
        response = client.get(reverse("core:dashboard"))

        assert response.context["total_rooms"] == 1
        assert response.context["available_rooms"] == 1
        assert response.context["bookings_today"] >= 0
        assert "month_revenue" in response.context
        assert "occupancy_rate" in response.context


@pytest.mark.django_db
class TestContact:
    def test_contact_form_submission(self, client):
        """Test contact form submission"""
        contact_data = {
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Test Subject",
            "message": "Test Message",
        }

        response = client.post(reverse("core:contact"), contact_data)

        assert response.status_code == 302  # Redirect after successful submission
        assert Contact.objects.count() == 1
        contact = Contact.objects.first()
        assert contact.name == "Test User"
        assert contact.email == "test@example.com"

    def test_invalid_contact_form(self, client):
        """Test contact form with invalid data"""
        invalid_data = {
            "name": "Test User",
            "email": "invalid-email",  # Invalid email
            "subject": "",  # Required field
            "message": "Test Message",
        }

        response = client.post(reverse("core:contact"), invalid_data)

        assert response.status_code == 200  # Form redisplay
        assert Contact.objects.count() == 0


@pytest.mark.django_db
class TestNotifications:
    def test_notification_list_view(self, client, admin_user):
        """Test notifications list view"""
        # Create test notification
        notification = Notification.objects.create(
            user=admin_user,
            type="system",
            title="Test Notification",
            message="Test Message",
        )

        client.login(username="admin", password="admin123")
        response = client.get(reverse("core:notifications"))

        assert response.status_code == 200
        assert notification in response.context["notifications"]

    def test_notification_mark_as_read(self, client, admin_user):
        """Test notifications being marked as read"""
        # Create unread notification
        Notification.objects.create(
            user=admin_user,
            type="system",
            title="Test Notification",
            message="Test Message",
            read=False,
        )

        client.login(username="admin", password="admin123")
        response = client.get(reverse("core:notifications"))

        # Check if notification was marked as read
        notification = Notification.objects.first()
        assert notification.read == True


@pytest.mark.django_db
class TestHome:
    def test_home_page_view(self, client, test_room):
        """Test home page view"""
        response = client.get(reverse("core:home"))

        assert response.status_code == 200
        assert "featured_rooms" in response.context
        assert test_room in response.context["featured_rooms"]

    def test_featured_rooms_limit(self, client):
        """Test featured rooms limit"""
        # Create 6 rooms
        for i in range(6):
            Room.objects.create(
                name=f"Room {i}",
                room_number=str(i),
                floor=1,
                room_type="double",
                bed_type="queen",
                price_per_night=Decimal("100.00"),
                capacity_adults=2,
                capacity_children=1,
                is_active=True,
            )

        response = client.get(reverse("core:home"))
        assert (
            len(response.context["featured_rooms"]) == 4
        )  # Only 4 rooms should be shown


@pytest.mark.django_db
class TestModels:
    def test_contact_model(self):
        """Test Contact model"""
        contact = Contact.objects.create(
            name="Test User",
            email="test@example.com",
            subject="Test Subject",
            message="Test Message",
        )
        assert str(contact) == "Test Subject - Test User"
        assert contact.resolved == False

    def test_notification_model(self, admin_user):
        """Test Notification model"""
        notification = Notification.objects.create(
            user=admin_user,
            type="system",
            title="Test Notification",
            message="Test Message",
        )
        assert str(notification) == f"Test Notification - {admin_user.username}"
        assert notification.read == False
