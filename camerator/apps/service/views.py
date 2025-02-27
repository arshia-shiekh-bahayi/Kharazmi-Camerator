from django.views.generic import ListView

from apps.service.models import Service


class ServiceListView(ListView):
    model = Service
    template_name = "service/service-list.html"
    context_object_name = "services"
