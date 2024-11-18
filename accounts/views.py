# accounts/views.py
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView

from .forms import CustomUserChangeForm, CustomUserCreationForm, LoginForm
from .models import UserProfile


class LoginView(BaseLoginView):
    template_name = "accounts/login.html"
    form_class = LoginForm
    success_url = reverse_lazy("rooms:room_list")
    redirect_authenticated_user = True

    def form_valid(self, form):
        remember_me = form.cleaned_data.get("remember_me")
        if not remember_me:
            # Session expires when browser closes
            self.request.session.set_expiry(0)
        return super().form_valid(form)

    def get_success_url(self):
        next_url = self.request.GET.get("next")
        if next_url:
            return next_url
        return reverse_lazy("core:home")

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password")
        return super().form_invalid(form)


class LogoutView(BaseLogoutView):
    next_page = reverse_lazy("rooms:room_list")
    http_method_names = ["get", "post"]


class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Registration successful. Please log in.")
        return response


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "accounts/profile.html"
    context_object_name = "profile"

    def get_object(self):
        # Ensure profile exists
        UserProfile.objects.get_or_create(user=self.request.user)
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_profile"] = self.request.user.profile  # Add profile to context
        # Add recent bookings if you have them
        context["recent_bookings"] = self.request.user.booking_set.order_by(
            "-created_at"
        )[:5]
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = "accounts/profile_edit.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self):
        UserProfile.objects.get_or_create(user=self.request.user)
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Profile updated successfully.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)
