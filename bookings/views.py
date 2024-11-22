import json
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from rooms.models import Room

from .forms import BookingCreateForm
from .models import Booking


class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingCreateForm
    template_name = "bookings/booking_create.html"
    success_url = reverse_lazy("bookings:booking_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        room = get_object_or_404(Room, pk=self.kwargs["room_pk"])
        kwargs["room"] = room

        if kwargs.get("data"):
            data = kwargs["data"].copy()
            data["room"] = room.pk
            kwargs["data"] = data

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room = get_object_or_404(Room, pk=self.kwargs["room_pk"])
        context["room"] = room
        context["today"] = datetime.now().date().strftime("%Y-%m-%d")

        # Get booked dates for this room
        booked_dates = []
        bookings = room.booking_set.filter(
            status__in=["pending", "confirmed"], check_out__gte=datetime.now().date()
        )
        for booking in bookings:
            current = booking.check_in
            while current <= booking.check_out:
                booked_dates.append(current.strftime("%Y-%m-%d"))
                current += timedelta(days=1)
        context["booked_dates"] = json.dumps(booked_dates)
        return context

    def form_valid(self, form):
        print("\nForm validation succeeded:")
        print(f"Form cleaned data: {form.cleaned_data}")
        form.instance.user = self.request.user
        form.instance.status = "pending"
        response = super().form_valid(form)
        messages.success(
            self.request,
            "Your booking has been created successfully! We will confirm it shortly.",
        )
        return response

    def form_invalid(self, form):
        print("\nForm validation failed:")
        print(f"Form errors: {form.errors}")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("bookings:booking_detail", kwargs={"pk": self.object.pk})


class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "bookings/booking_list.html"
    context_object_name = "bookings"
    paginate_by = 10

    def get_queryset(self):
        queryset = Booking.objects.filter(user=self.request.user)
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)
        return queryset.select_related("room")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = Booking.STATUS_CHOICES
        context["current_status"] = self.request.GET.get("status", "")
        return context


class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = "bookings/booking_detail.html"
    context_object_name = "booking"

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)


class BookingCancelView(LoginRequiredMixin, UpdateView):
    model = Booking
    fields: list = []  # No fields to update
    template_name = "bookings/booking_cancel.html"
    success_url = reverse_lazy("bookings:booking_list")

    def get_queryset(self):
        return Booking.objects.filter(
            user=self.request.user, status__in=["pending", "confirmed"]
        )

    def form_valid(self, form):
        if self.object.can_be_cancelled:
            self.object.status = "cancelled"
            messages.success(self.request, "Booking cancelled successfully.")
            return super().form_valid(form)
        messages.error(self.request, "This booking cannot be cancelled.")
        return redirect("bookings:booking_detail", pk=self.object.pk)


def check_availability(request, room_pk):
    """HTMX endpoint to check room availability"""
    check_in = request.GET.get("check_in")
    check_out = request.GET.get("check_out")

    if not all([check_in, check_out]):
        return JsonResponse({"available": False, "message": "Please select dates"})

    try:
        check_in = datetime.strptime(check_in, "%Y-%m-%d").date()
        check_out = datetime.strptime(check_out, "%Y-%m-%d").date()

        if check_in >= check_out:
            return JsonResponse(
                {"available": False, "message": "Check-out must be after check-in date"}
            )

        if check_in < datetime.now().date():
            return JsonResponse(
                {"available": False, "message": "Check-in cannot be in the past"}
            )

    except ValueError:
        return JsonResponse({"available": False, "message": "Invalid dates"})

    overlapping_bookings = Booking.objects.filter(
        room_id=room_pk,
        status__in=[
            "pending",
            "confirmed",
        ],  # Only check pending and confirmed bookings
        check_in__lt=check_out,
        check_out__gt=check_in,
    ).exists()

    return JsonResponse(
        {
            "available": not overlapping_bookings,
            "message": (
                "Room is available for selected dates"
                if not overlapping_bookings
                else "Room is not available for selected dates"
            ),
        }
    )
