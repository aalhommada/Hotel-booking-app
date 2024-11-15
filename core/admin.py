from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Contact, Notification


@admin.register(Contact)
class ContactAdmin(ModelAdmin):
    list_display = ["subject", "name", "email", "created_at", "resolved"]
    list_filter = ["resolved", "created_at"]
    search_fields = ["name", "email", "subject", "message"]
    readonly_fields = ["created_at"]


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ["title", "user", "type", "read", "created_at"]
    list_filter = ["type", "read", "created_at"]
    search_fields = ["title", "message", "user__username", "user__email"]
    readonly_fields = ["created_at"]
