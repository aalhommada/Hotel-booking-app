# accounts/tests.py
import pytest
from django.contrib.auth.models import Group, Permission, User
from django.test import Client
from django.urls import reverse


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def test_user():
    user = User.objects.create_user(
        username="testuser", password="testpass123", email="test@example.com"
    )
    return user


@pytest.fixture
def test_admin():
    admin = User.objects.create_superuser(
        username="admin", password="admin123", email="admin@example.com"
    )
    return admin


# Test T002: Account Registration
@pytest.mark.django_db
class TestUserRegistration:
    def test_user_registration_successful(self, client):
        """Test successful user registration and redirect to login"""
        registration_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "securepass123",
            "password2": "securepass123",
            "first_name": "New",
            "last_name": "User",
        }

        response = client.post(reverse("accounts:register"), registration_data)

        assert response.status_code == 302  # Redirect status
        assert response.url == reverse("accounts:login")  # Redirects to login
        assert User.objects.filter(username="newuser").exists()

    def test_user_registration_invalid_data(self, client):
        """Test registration with invalid data"""
        invalid_data = {
            "username": "newuser",
            "email": "invalid-email",
            "password1": "pass123",
            "password2": "different123",
        }

        response = client.post(reverse("accounts:register"), invalid_data)

        assert response.status_code == 200  # Form redisplay
        assert not User.objects.filter(username="newuser").exists()


# Test T007: Admin Group Management
@pytest.mark.django_db
class TestAdminGroupManagement:
    def test_create_group_and_assign_user(self, client, test_admin):
        """Test creating a group and assigning a user to it"""
        client.login(username="admin", password="admin123")

        # Create a new group
        group_name = "Test Group"
        response = client.post(
            "/admin/auth/group/add/", {"name": group_name, "permissions": []}
        )

        assert Group.objects.filter(name=group_name).exists()

        # Create a new user and assign to group
        user = User.objects.create_user("groupuser", "group@test.com", "pass123")
        group = Group.objects.get(name=group_name)
        user.groups.add(group)

        assert group in user.groups.all()

    def test_assign_permissions_to_group(self, client, test_admin):
        """Test assigning permissions to a group"""
        client.login(username="admin", password="admin123")

        # Create group
        group = Group.objects.create(name="Staff Group")

        # Get some permissions
        permissions = Permission.objects.filter(content_type__app_label="auth")[:2]
        group.permissions.set(permissions)

        assert group.permissions.count() == 2


@pytest.mark.django_db
class TestUserProfile:
    def test_profile_view_authenticated(self, client, test_user):
        """Test accessing profile when authenticated"""
        client.login(username="testuser", password="testpass123")
        response = client.get(reverse("accounts:profile"))

        assert response.status_code == 200
        assert "profile" in response.context
        assert response.context["profile"] == test_user

    def test_profile_view_unauthenticated(self, client):
        """Test accessing profile when not authenticated"""
        response = client.get(reverse("accounts:profile"))

        assert response.status_code == 302  # Redirect to login
        assert "login" in response.url

    def test_profile_edit(self, client, test_user):
        """Test editing user profile"""
        client.login(username="testuser", password="testpass123")

        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "email": "updated@example.com",
            "profile-phone": "1234567890",
            "profile-address": "Test Address",
        }

        response = client.post(reverse("accounts:profile_edit"), update_data)

        assert response.status_code == 302  # Redirect after successful update
        updated_user = User.objects.get(id=test_user.id)
        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == "Name"
