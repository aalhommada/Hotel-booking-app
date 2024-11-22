from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone

from .models import Room, RoomImage


@pytest.fixture
def managers_group():
    group, _ = Group.objects.get_or_create(name="Managers")
    content_type = ContentType.objects.get_for_model(Room)

    permissions = Permission.objects.filter(
        content_type=content_type,
        codename__in=["add_room", "change_room", "delete_room", "view_room"],
    )
    group.permissions.add(*permissions)
    return group


@pytest.fixture
def manager_user(managers_group):
    user = User.objects.create_user(
        username="manager",
        password="manager123",
        email="manager@example.com",
        is_staff=True,
    )
    user.groups.add(managers_group)
    content_type = ContentType.objects.get_for_model(Room)
    permissions = Permission.objects.filter(content_type=content_type)
    user.user_permissions.add(*permissions)

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


# Test T001: Room Search and Filter
@pytest.mark.django_db
class TestRoomSearch:
    def test_room_list_view(self, client, test_room):
        """Test basic room listing"""
        response = client.get(reverse("rooms:room_list"))

        assert response.status_code == 200
        assert test_room in response.context["rooms"]

    def test_room_filter_by_capacity(self, client, test_room):
        """Test filtering rooms by capacity"""
        url = reverse("rooms:room_list")
        response = client.get(f"{url}?adults=2&children=1")

        assert response.status_code == 200
        assert test_room in response.context["rooms"]

        # Test exceeding capacity
        response = client.get(f"{url}?adults=3&children=2")
        assert test_room not in response.context["rooms"]

    def test_room_filter_by_dates(self, client, test_room):
        """Test filtering rooms by dates"""
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=7)

        url = reverse("rooms:room_list")
        response = client.get(f"{url}?check_in={tomorrow}&check_out={next_week}")

        assert response.status_code == 200
        assert test_room in response.context["rooms"]

    def test_room_detail_view(self, client, test_room):
        """Test room detail view"""
        response = client.get(reverse("rooms:room_detail", kwargs={"pk": test_room.pk}))

        assert response.status_code == 200
        assert response.context["room"] == test_room


# Test T005: Room CRUD Operations
@pytest.mark.django_db
class TestRoomManagement:
    def test_create_room(self, client, manager_user):
        """Test room creation by manager"""
        client.login(username="manager", password="manager123")
        client.force_login(manager_user)

        response = client.get(reverse("rooms:room_create"))
        csrf_token = response.cookies["csrftoken"].value

        room_data = {
            "name": "New Room",
            "room_number": "102",
            "floor": 1,
            "room_type": "double",
            "bed_type": "queen",
            "price_per_night": "120.00",
            "capacity_adults": 2,
            "capacity_children": 2,
            "description": "A new test room",
            "is_active": True,
            "has_wifi": True,
            "has_tv": True,
            "has_ac": True,
            "has_heating": True,
            "has_bathroom": True,
            "has_balcony": False,
            "has_minibar": False,
            "has_desk": True,
            "has_closet": True,
            "has_safe": False,
            "images-TOTAL_FORMS": "0",
            "images-INITIAL_FORMS": "0",
            "images-MIN_NUM_FORMS": "0",
            "images-MAX_NUM_FORMS": "10",
            "csrfmiddlewaretoken": csrf_token,
        }

        response = client.post(
            reverse("rooms:room_create"), data=room_data, follow=True
        )

        if response.status_code != 302:
            print(f"Response status: {response.status_code}")
            print(f"User authenticated: {response.wsgi_request.user.is_authenticated}")
            print(
                f"User groups: {[g.name for g in response.wsgi_request.user.groups.all()]}"
            )
            if hasattr(response, "context") and "form" in response.context:
                print(f"Form errors: {response.context['form'].errors}")

        assert Room.objects.filter(room_number="102").exists()

    def test_update_room(self, client, manager_user, test_room):
        """Test room update"""
        client.login(username="manager", password="manager123")
        client.force_login(manager_user)

        response = client.get(reverse("rooms:room_edit", kwargs={"pk": test_room.pk}))
        csrf_token = response.cookies["csrftoken"].value

        updated_data = {
            "name": "Updated Room",
            "room_number": test_room.room_number,
            "floor": test_room.floor,
            "room_type": test_room.room_type,
            "bed_type": test_room.bed_type,
            "price_per_night": "150.00",
            "capacity_adults": test_room.capacity_adults,
            "capacity_children": test_room.capacity_children,
            "description": "Updated description",
            "is_active": True,
            "has_wifi": True,
            "has_tv": True,
            "has_ac": True,
            "has_heating": True,
            "has_bathroom": True,
            "has_balcony": False,
            "has_minibar": False,
            "has_desk": True,
            "has_closet": True,
            "has_safe": False,
            "images-TOTAL_FORMS": "0",
            "images-INITIAL_FORMS": "0",
            "images-MIN_NUM_FORMS": "0",
            "images-MAX_NUM_FORMS": "10",
            "csrfmiddlewaretoken": csrf_token,
        }

        response = client.post(
            reverse("rooms:room_edit", kwargs={"pk": test_room.pk}),
            data=updated_data,
            follow=True,
        )

        if response.status_code != 302:
            print(f"Response status: {response.status_code}")
            print(f"User authenticated: {response.wsgi_request.user.is_authenticated}")
            print(
                f"User groups: {[g.name for g in response.wsgi_request.user.groups.all()]}"
            )
            if hasattr(response, "context") and "form" in response.context:
                print(f"Form errors: {response.context['form'].errors}")

        test_room.refresh_from_db()
        assert test_room.name == "Updated Room"
        assert test_room.price_per_night == Decimal("150.00")

    def test_delete_room(self, client, manager_user, test_room):
        """Test room deletion"""
        client.login(username="manager", password="manager123")
        client.force_login(manager_user)

        response = client.post(
            reverse("rooms:room_delete", kwargs={"pk": test_room.pk})
        )

        assert response.status_code == 302
        assert not Room.objects.filter(pk=test_room.pk).exists()

    def test_room_image_management(self, client, manager_user, test_room):
        """Test adding images to room"""
        client.login(username="manager", password="manager123")

        response = client.get(reverse("rooms:room_edit", kwargs={"pk": test_room.pk}))
        csrf_token = response.cookies["csrftoken"].value

        image_content = b"GIF89a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
        image_data = SimpleUploadedFile(
            "test_image.gif", image_content, content_type="image/gif"
        )

        data = {
            "name": test_room.name,
            "room_number": test_room.room_number,
            "floor": test_room.floor,
            "room_type": test_room.room_type,
            "bed_type": test_room.bed_type,
            "price_per_night": test_room.price_per_night,
            "capacity_adults": test_room.capacity_adults,
            "capacity_children": test_room.capacity_children,
            "description": "Test description",
            "is_active": True,
            "has_wifi": True,
            "has_tv": True,
            "has_ac": True,
            "has_heating": True,
            "has_bathroom": True,
            "has_balcony": False,
            "has_minibar": False,
            "has_desk": True,
            "has_closet": True,
            "has_safe": False,
            # Image formset data
            "images-TOTAL_FORMS": "1",
            "images-INITIAL_FORMS": "0",
            "images-MIN_NUM_FORMS": "0",
            "images-MAX_NUM_FORMS": "10",
            "images-0-id": "",
            "images-0-room": test_room.pk,
            "images-0-image": image_data,
            "images-0-is_primary": "on",
            "images-0-caption": "Test Image",
            "images-0-order": "0",
            "csrfmiddlewaretoken": csrf_token,
        }

        response = client.post(
            reverse("rooms:room_edit", kwargs={"pk": test_room.pk}),
            data=data,
            format="multipart",
            follow=True,
        )

        if response.status_code != 302:
            print(f"Response status: {response.status_code}")
            print(f"User authenticated: {response.wsgi_request.user.is_authenticated}")
            print(
                f"User groups: {[g.name for g in response.wsgi_request.user.groups.all()]}"
            )
            if hasattr(response, "context"):
                if "form" in response.context:
                    print(f"Form errors: {response.context['form'].errors}")
                if "image_formset" in response.context:
                    print(
                        f"Image formset errors: {response.context['image_formset'].errors}"
                    )
                    for form in response.context["image_formset"].forms:
                        print(f"Image form errors: {form.errors}")

        test_room.refresh_from_db()
        assert test_room.images.count() == 1

        # Additional assertions
        room_image = test_room.images.first()
        assert room_image is not None
        assert room_image.is_primary == True
        assert room_image.caption == "Test Image"


@pytest.mark.django_db
class TestRoomAvailability:
    def test_check_room_availability(self, client, test_room):
        """Test room availability checking"""
        tomorrow = timezone.now().date() + timedelta(days=1)
        next_week = tomorrow + timedelta(days=7)

        response = client.get(
            reverse("rooms:check_availability", kwargs={"pk": test_room.pk}),
            {
                "check_in": tomorrow.strftime("%Y-%m-%d"),
                "check_out": next_week.strftime("%Y-%m-%d"),
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["available"] is True

    def test_invalid_date_format(self, client, test_room):
        """Test handling of invalid date format"""
        response = client.get(
            reverse("rooms:check_availability", kwargs={"pk": test_room.pk}),
            {"check_in": "invalid", "check_out": "invalid"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["available"] is False
        assert "Invalid date format" in data["message"]
