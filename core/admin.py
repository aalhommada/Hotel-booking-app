from django.contrib import admin
from .models import Contact, Notification, SiteSetting

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['subject', 'name', 'email', 'created_at', 'resolved']
    list_filter = ['resolved', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'type', 'read', 'created_at']
    list_filter = ['type', 'read', 'created_at']
    search_fields = ['title', 'message', 'user__username', 'user__email']
    readonly_fields = ['created_at']

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'updated_at']
    search_fields = ['key', 'value', 'description']
    readonly_fields = ['updated_at']