from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _

from apps.user.forms import UserAdminChangeForm, UserAdminCreationForm
from apps.user.models import AuthRequest, User
from utils.mixins.admin import TimestampableAdminMixin


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "national_code",
                    "image",
                    "description",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = [
        "username",
        "first_name",
        "last_name",
        "national_code",
        "is_superuser",
    ]
    search_fields = (
        "username",
        "first_name",
        "last_name",
        "national_code",
    )


@admin.register(AuthRequest)
class AuthRequestAdmin(TimestampableAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "mobile",
        "otp_code",
        "user_is_registered",
        "formatted_created_at",
        "formatted_updated_at",
    )
    search_fields = ("mobile",)
    list_filter = ("mobile",)
    ordering = ("-created_at",)
