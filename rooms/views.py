# rooms/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import JsonResponse
from .models import Room, RoomImage
from .forms import RoomForm, RoomImageFormSet
from accounts.decorators import role_required
from django.utils.decorators import method_decorator

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

    def get_queryset(self):
        return super().get_queryset().prefetch_related('images')

@method_decorator(role_required('admin', 'manager'), name='dispatch')
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

@method_decorator(role_required('admin', 'manager'), name='dispatch')
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

@method_decorator(role_required('admin', 'manager'), name='dispatch')
class RoomDeleteView(LoginRequiredMixin, DeleteView):
    model = Room
    template_name = 'rooms/room_confirm_delete.html'
    success_url = reverse_lazy('rooms:room_manage')

@method_decorator(role_required('admin', 'manager'), name='dispatch')
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

def check_room_availability(request):
    """HTMX endpoint to check room availability"""
    room_id = request.GET.get('room_id')
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    
    if not all([room_id, check_in, check_out]):
        return JsonResponse({
            'available': False,
            'message': 'Missing required parameters'
        })
    
    try:
        room = Room.objects.get(id=room_id)
        # Add your availability checking logic here
        available = True  # Replace with actual availability check
        return JsonResponse({
            'available': available,
            'message': 'Room is available' if available else 'Room is not available'
        })
    except Room.DoesNotExist:
        return JsonResponse({
            'available': False,
            'message': 'Room not found'
        })