
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseForbidden, JsonResponse
from .models import Booking
from .forms import BookingForm
from rooms.models import Room
from decimal import Decimal
from datetime import datetime
from django.contrib import messages
from .forms import BookingCreateForm, BookingUpdateForm

class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingCreateForm
    template_name = 'bookings/booking_create.html'
    success_url = reverse_lazy('bookings:booking_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['room'] = get_object_or_404(Room, pk=self.kwargs['room_pk'])
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.room = get_object_or_404(Room, pk=self.kwargs['room_pk'])
        response = super().form_valid(form)
        messages.success(self.request, 'Booking created successfully!')
        return response

class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'bookings/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 10

    def get_queryset(self):
        queryset = Booking.objects.filter(user=self.request.user)
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset.select_related('room')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Booking.STATUS_CHOICES
        context['current_status'] = self.request.GET.get('status', '')
        return context

class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'bookings/booking_detail.html'
    context_object_name = 'booking'

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

class BookingCancelView(LoginRequiredMixin, UpdateView):
    model = Booking
    fields = []  # No fields to update
    template_name = 'bookings/booking_cancel.html'
    success_url = reverse_lazy('bookings:booking_list')

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user, status__in=['pending', 'confirmed'])

    def form_valid(self, form):
        if self.object.can_be_cancelled:
            self.object.status = 'cancelled'
            messages.success(self.request, 'Booking cancelled successfully.')
            return super().form_valid(form)
        messages.error(self.request, 'This booking cannot be cancelled.')
        return redirect('bookings:booking_detail', pk=self.object.pk)

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