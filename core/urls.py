# core/urls.py
from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("notifications/", views.NotificationListView.as_view(), name="notifications"),
]
