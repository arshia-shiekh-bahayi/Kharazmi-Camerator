from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from jalali_date import datetime2jalali


class AuthorableModelAdminMixin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super().save_model(request, obj, form, change)


class TimestampableAdminMixin:
    @admin.display(description=_("Created at"))
    def formatted_created_at(self, obj):
        return datetime2jalali(obj.created_at).strftime("%H:%M:%S _ %Y/%m/%d")

    @admin.display(description=_("Updated at"))
    def formatted_updated_at(self, obj):
        return datetime2jalali(obj.updated_at).strftime("%H:%M:%S _ %Y/%m/%d")
