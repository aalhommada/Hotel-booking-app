# bookings/urls.py
from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.BookingListView.as_view(), name='booking_list'),
    path('<int:pk>/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('create/<int:room_pk>/', views.BookingCreateView.as_view(), name='booking_create'),
    path('<int:pk>/cancel/', views.BookingCancelView.as_view(), name='booking_cancel'),
]