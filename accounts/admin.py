from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from unfold.admin import ModelAdmin

from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"


class CustomUserAdmin(UserAdmin, ModelAdmin):
    inlines = (UserProfileInline,)
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "get_groups",
    )

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])

    get_groups.short_description = "Groups"  # type: ignore

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "email",
                    "first_name",
                    "last_name",
                    "is_staff",
                    "is_active",
                    "groups",
                ),
            },
        ),
    )

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new user
            # If user is assigned to any group with permissions
            if form.cleaned_data.get("groups") and any(
                group.permissions.exists() for group in form.cleaned_data["groups"]
            ):
                obj.is_staff = True
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # After saving related objects (like groups), update is_staff based on group permissions
        obj = form.instance
        if obj.groups.filter(permissions__isnull=False).exists():
            obj.is_staff = True
            obj.save()
        else:
            # If user has no groups with permissions, remove staff status
            # unless they're a superuser
            if not obj.is_superuser:
                obj.is_staff = False
                obj.save()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Users can only see users in their groups or with lower permissions
        if request.user.groups.exists():
            user_groups = request.user.groups.all()
            return qs.filter(groups__in=user_groups)
        return qs.none()

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets

        # Customize fieldsets based on user permissions
        if request.user.is_superuser:
            return super().get_fieldsets(request, obj)

        # Limited fields for non-superusers
        return (
            (None, {"fields": ("username", "password")}),
            ("Personal info", {"fields": ("first_name", "last_name", "email")}),
            ("Permissions", {"fields": ("is_active", "groups")}),
        )


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
