
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse
from .models import Booking
from .forms import BookingForm
from rooms.models import Room
from decimal import Decimal
from datetime import datetime

class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'bookings/booking_create.html'
    success_url = reverse_lazy('bookings:booking_list')

    def get_initial(self):
        initial = super().get_initial()
        initial['check_in'] = self.request.GET.get('check_in')
        initial['check_out'] = self.request.GET.get('check_out')
        initial['adults'] = self.request.GET.get('adults', 1)
        initial['children'] = self.request.GET.get('children', 0)
        return initial

    def form_valid(self, form):
        room = get_object_or_404(Room, pk=self.kwargs['room_pk'])
        form.instance.room = room
        form.instance.user = self.request.user
        
        # Calculate total price
        check_in = form.cleaned_data['check_in']
        check_out = form.cleaned_data['check_out']
        days = (check_out - check_in).days
        form.instance.total_price = room.price_per_night * Decimal(days)
        
        return super().form_valid(form)

class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'bookings/booking_list.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'manager']:
            return Booking.objects.all().order_by('-created_at')
        elif user.role == 'team':
            return Booking.objects.filter(
                check_in__date=datetime.today().date()
            ).order_by('check_in')
        else:
            return Booking.objects.filter(user=user).order_by('-created_at')

class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'bookings/booking_detail.html'
    context_object_name = 'booking'

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'manager', 'team']:
            return Booking.objects.all()
        return Booking.objects.filter(user=user)

def check_availability(request, room_pk):
    """HTMX endpoint to check room availability"""
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    
    if not all([check_in, check_out]):
        return JsonResponse({'available': False, 'message': 'Please select dates'})
        
    try:
        check_in = datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'available': False, 'message': 'Invalid dates'})

    overlapping_bookings = Booking.objects.filter(
        room_id=room_pk,
        check_in__lte=check_out,
        check_out__gte=check_in
    ).exists()

    return JsonResponse({
        'available': not overlapping_bookings,
        'message': 'Available' if not overlapping_bookings else 'Not available for selected dates'
    })