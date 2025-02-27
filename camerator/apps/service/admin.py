from django.contrib import admin

from apps.service.models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "number_of_photos",
        "created_date",
    )
