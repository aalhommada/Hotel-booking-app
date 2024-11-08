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

        check_in = self.request.GET.get('check_in')
        check_out = self.request.GET.get('check_out')
        adults = self.request.GET.get('adults')
        children = self.request.GET.get('children')
        room_type = self.request.GET.get('room_type')


        search_query = self.request.GET.get('search', '')
 
        # Filter by room type if provided
        if room_type:
            queryset = queryset.filter(room_type=room_type)

        # Filter by capacity if provided
        if adults:
            try:
                adults = int(adults)
                queryset = queryset.filter(capacity_adults__gte=adults)
            except ValueError:
                pass

        if children:
            try:
                children = int(children)
                queryset = queryset.filter(capacity_children__gte=children)
            except ValueError:
                pass

        # Filter by availability if both dates are provided
        if check_in and check_out:
            try:
                from django.db.models import Q
                overlapping_bookings = Q(
                    booking__check_in__lt=check_out,
                    booking__check_out__gt=check_in,
                    booking__status__in=['pending', 'confirmed']
                )
                queryset = queryset.exclude(overlapping_bookings)
            except ValueError:
                pass

        return queryset.prefetch_related('images').distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'room_types': Room.ROOM_TYPES,
            'selected_type': self.request.GET.get('room_type', ''),
            'check_in': self.request.GET.get('check_in', ''),
            'check_out': self.request.GET.get('check_out', ''),
            'adults': self.request.GET.get('adults', ''),
            'children': self.request.GET.get('children', ''),
        })
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