# rooms/views.py
from decimal import Decimal
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

from bookings.models import Booking
from .models import Room, RoomImage
from .forms import RoomForm, RoomImageFormSet
from accounts.decorators import group_required  # Updated this line
from django.utils.decorators import method_decorator
from datetime import datetime, timedelta
import json

class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    fields = ['check_in', 'check_out', 'adults', 'children']
    template_name = 'bookings/booking_create.html'
    success_url = reverse_lazy('bookings:booking_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room_pk = self.kwargs.get('room_pk')
        context['room'] = get_object_or_404(Room, pk=room_pk)
        return context

    def form_valid(self, form):
        # Get the room
        room_pk = self.kwargs.get('room_pk')
        room = get_object_or_404(Room, pk=room_pk)
        
        # Set the user and room
        form.instance.user = self.request.user
        form.instance.room = room
        
        # Calculate total price
        check_in = form.cleaned_data['check_in']
        check_out = form.cleaned_data['check_out']
        days = (check_out - check_in).days
        form.instance.total_price = room.price_per_night * Decimal(days)
        
        # Set initial status
        form.instance.status = 'pending'
        
        # Validate capacity
        if (form.cleaned_data['adults'] > room.capacity_adults or 
            form.cleaned_data['children'] > room.capacity_children):
            messages.error(self.request, 'Number of guests exceeds room capacity.')
            return self.form_invalid(form)
        
        # Check availability again
        overlapping_bookings = Booking.objects.filter(
            room=room,
            status__in=['pending', 'confirmed'],
            check_in__lt=check_out,
            check_out__gt=check_in
        ).exists()
        
        if overlapping_bookings:
            messages.error(self.request, 'Room is no longer available for these dates.')
            return self.form_invalid(form)
        
        response = super().form_valid(form)
        messages.success(self.request, 'Booking created successfully!')
        return response

    def get_success_url(self):
        return reverse_lazy('bookings:booking_detail', kwargs={'pk': self.object.pk})

class RoomListView(ListView):
    model = Room
    template_name = 'rooms/room_list.html'
    context_object_name = 'rooms'
    paginate_by = 12

    def get_queryset(self):
        queryset = Room.objects.filter(is_active=True)
        search_query = self.request.GET.get('search', '')
        room_type = self.request.GET.get('room_type', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
            
        if room_type:
            queryset = queryset.filter(room_type=room_type)
            
        return queryset.select_related().prefetch_related('images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['room_types'] = Room.ROOM_TYPES
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_type'] = self.request.GET.get('room_type', '')
        return context

class RoomDetailView(DetailView):
    model = Room
    template_name = 'rooms/room_detail.html'
    context_object_name = 'room'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get booked dates
        booked_dates = []
        bookings = self.object.booking_set.filter(
            status__in=['pending', 'confirmed'],
            check_out__gte=datetime.now().date()
        )
        
        for booking in bookings:
            current = booking.check_in
            while current <= booking.check_out:
                booked_dates.append(current.strftime('%Y-%m-%d'))
                current += timedelta(days=1)
        
        context['booked_dates'] = json.dumps(booked_dates)
        context['today'] = datetime.now().date().strftime('%Y-%m-%d')
        return context

@method_decorator(group_required('Managers'), name='dispatch')  # Updated decorator
class RoomCreateView(LoginRequiredMixin, CreateView):
    model = Room
    form_class = RoomForm
    template_name = 'rooms/room_form.html'
    success_url = reverse_lazy('rooms:room_manage')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = RoomImageFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object
            )
        else:
            context['image_formset'] = RoomImageFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        
        if image_formset.is_valid():
            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()
            return super().form_valid(form)
            
        return self.render_to_response(self.get_context_data(form=form))

@method_decorator(group_required('Managers'), name='dispatch')  # Updated decorator
class RoomUpdateView(LoginRequiredMixin, UpdateView):
    model = Room
    form_class = RoomForm
    template_name = 'rooms/room_form.html'
    success_url = reverse_lazy('rooms:room_manage')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = RoomImageFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object
            )
        else:
            context['image_formset'] = RoomImageFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        
        if image_formset.is_valid():
            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()
            return super().form_valid(form)
            
        return self.render_to_response(self.get_context_data(form=form))

@method_decorator(group_required('Managers'), name='dispatch')  # Updated decorator
class RoomDeleteView(LoginRequiredMixin, DeleteView):
    model = Room
    template_name = 'rooms/room_confirm_delete.html'
    success_url = reverse_lazy('rooms:room_manage')

@method_decorator(group_required('Managers'), name='dispatch')  # Updated decorator
class RoomManagementView(LoginRequiredMixin, ListView):
    model = Room
    template_name = 'rooms/room_manage.html'
    context_object_name = 'rooms'
    paginate_by = 20

    def get_queryset(self):
        return Room.objects.all().prefetch_related('images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_rooms'] = Room.objects.filter(is_active=True).count()
        context['inactive_rooms'] = Room.objects.filter(is_active=False).count()
        return context

def check_room_availability(request, pk):
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    
    try:
        room = Room.objects.get(pk=pk)
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
        
        # Check if dates are valid
        if check_in_date >= check_out_date:
            return JsonResponse({
                'available': False,
                'message': 'Check-out date must be after check-in date'
            })
            
        # Check for overlapping bookings
        is_available = not room.booking_set.filter(
            status__in=['pending', 'confirmed'],
            check_in__lt=check_out_date,
            check_out__gt=check_in_date
        ).exists()
        
        return JsonResponse({
            'available': is_available,
            'message': 'Room is available' if is_available else 'Room is not available for selected dates'
        })
        
    except (Room.DoesNotExist, ValueError):
        return JsonResponse({
            'available': False,
            'message': 'Invalid request'
        })
    

@login_required
def book_room(request, pk):
    if request.method == 'POST':
        room = get_object_or_404(Room, pk=pk)
        
        try:
            # Create booking
            booking = Booking(
                user=request.user,
                room=room,
                check_in=request.POST['check_in'],
                check_out=request.POST['check_out'],
                adults=request.POST['adults'],
                children=request.POST.get('children', 0),
                special_requests=request.POST.get('special_requests', ''),
                status='pending'
            )
            
            # Clean and validate
            booking.clean()
            
            if isinstance(booking.check_in, str):
                booking.check_in = datetime.strptime(booking.check_in, "%Y-%m-%d").date()
            if isinstance(booking.check_out, str):
                booking.check_out = datetime.strptime(booking.check_out, "%Y-%m-%d").date()

            # Calculate the number of days
            days = (booking.check_out - booking.check_in).days
            booking.total_price = room.price_per_night * Decimal(days)
            
            # Save booking
            booking.save()
            
            messages.success(request, 'Your booking has been created successfully! We will confirm it shortly.')
            return redirect('bookings:booking_detail', pk=booking.pk)
            
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('rooms:room_detail', pk=pk)
            
    return redirect('rooms:room_detail', pk=pk)