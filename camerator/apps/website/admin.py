from django.contrib import admin
from .models import Newsletter, Contact


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ("email",)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "subject",
        "created_date",
    )
