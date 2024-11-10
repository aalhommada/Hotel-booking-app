from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    path('', views.RoomListView.as_view(), name='room_list'),
    path('<int:pk>/', views.RoomDetailView.as_view(), name='room_detail'),
    path('create/', views.RoomCreateView.as_view(), name='room_create'),
    path('<int:pk>/edit/', views.RoomUpdateView.as_view(), name='room_edit'),
    path('<int:pk>/delete/', views.RoomDeleteView.as_view(), name='room_delete'),
    path('<int:pk>/book/', views.book_room, name='book_room'),
    path('manage/', views.RoomManagementView.as_view(), name='room_manage'),
     path('<int:pk>/check-availability/', views.check_room_availability, name='check_availability'),    
]