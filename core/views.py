from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg, Count, Sum
from django.utils import timezone
from django.views.generic import CreateView, ListView, TemplateView

from bookings.models import Booking
from rooms.models import Room

from .forms import ContactForm
from .models import Contact, Notification


class DashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "core/dashboard.html"

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return (
            self.request.user.is_staff
            and self.request.user.groups.filter(name="Managers").exists()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)

        # Room statistics
        context["total_rooms"] = Room.objects.count()
        context["available_rooms"] = Room.objects.filter(is_active=True).count()

        # Booking statistics
        context["bookings_today"] = Booking.objects.filter(check_in=today).count()

        context["bookings_month"] = Booking.objects.filter(
            created_at__date__gte=thirty_days_ago
        ).count()

        # Revenue statistics
        month_revenue = (
            Booking.objects.filter(
                created_at__date__gte=thirty_days_ago, status="confirmed"
            ).aggregate(total=Sum("total_price"))["total"]
            or 0
        )

        context["month_revenue"] = month_revenue

        # Occupancy rate
        total_room_days = context["total_rooms"] * 30
        booked_room_days = Booking.objects.filter(
            check_in__gte=thirty_days_ago, status="confirmed"
        ).count()

        context["occupancy_rate"] = (
            (booked_room_days / total_room_days * 100) if total_room_days > 0 else 0
        )

        # Recent bookings
        context["recent_bookings"] = Booking.objects.select_related(
            "user", "room"
        ).order_by("-created_at")[:5]

        return context


class ContactView(CreateView):
    model = Contact
    form_class = ContactForm
    template_name = "core/contact.html"
    success_url = "/"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, "Your message has been sent. We will contact you soon."
        )
        return response


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "core/notifications.html"
    context_object_name = "notifications"
    paginate_by = 10

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        # Mark all as read
        Notification.objects.filter(user=request.user, read=False).update(read=True)
        return super().get(request, *args, **kwargs)


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_rooms"] = (
            Room.objects.filter(is_active=True)
            .select_related()
            .prefetch_related("images")[:4]
        )
        return context
