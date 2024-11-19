from django.urls import path

from . import views

app_name = "analytics"

urlpatterns = [
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("year-data/<int:year>/", views.get_year_data, name="year_data"),
]
