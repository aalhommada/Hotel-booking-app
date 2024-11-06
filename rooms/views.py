from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Room
from django.shortcuts import render
from django.http import HttpResponse

class RoomListView(ListView):
    model = Room
    template_name = 'rooms/room_list.html'
    context_object_name = 'rooms'
    
    def get_queryset(self):
        queryset = Room.objects.all()
        
        # Filter by room type
        room_type = self.request.GET.get('room_type')
        if room_type:
            queryset = queryset.filter(room_type=room_type)
            
        # Filter by capacity
        adults = self.request.GET.get('adults')
        if adults:
            queryset = queryset.filter(capacity_adults__gte=adults)
            
        children = self.request.GET.get('children')
        if children:
            queryset = queryset.filter(capacity_children__gte=children)
            
        return queryset
    
    def get_template_names(self):
        if self.request.htmx:
            return ['rooms/partials/room_list_partial.html']
        return [self.template_name]

class RoomDetailView(DetailView):
    model = Room
    template_name = 'rooms/room_detail.html'
    context_object_name = 'room'