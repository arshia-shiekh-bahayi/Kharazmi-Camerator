from __future__ import annotations

from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from services.sms_service import SMSService, SMSServiceResult
from utils.mixins.models import Timestampable, UUIDPrimaryKeyMixin
from utils.validators import MobileValidator


def two_min_from_now():
    return timezone.now() + timedelta(minutes=5)


class UserManager(models.Manager["User"]):
    pass


class User(AbstractUser, UUIDPrimaryKeyMixin):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _("Phone Number"),
        max_length=150,
        unique=True,
        validators=[username_validator, MobileValidator()],
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    national_code = models.CharField(
        max_length=10, null=True, blank=True, verbose_name=_("National Code")
    )

    image = models.ImageField(
        upload_to="users/images/",
        blank=False,
        null=False,
        default="users/images/default.png",
    )
    description = models.TextField(blank=True, null=True)
    REQUIRED_FIELDS = []

    def __str__(self) -> str:
        return f"{self.username} ({self.first_name} {self.last_name})"


class AuthRequest(UUIDPrimaryKeyMixin, Timestampable, models.Model):
    """Data history of each authentication request."""

    class Meta:
        verbose_name = _("Auth Request")
        verbose_name_plural = _("Auth Requests")

    class RequestStatuses(models.TextChoices):
        PENDING = "pending", _("Pending")
        COMPLETED = "completed", _("Completed")

    mobile = models.CharField(max_length=11, validators=[MobileValidator()])
    otp_code = models.CharField(max_length=6, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    national_code = models.CharField(
        max_length=10, null=True, blank=True, verbose_name=_("National Code")
    )
    expire_datetime = models.DateTimeField(default=two_min_from_now)
    user_is_registered = models.BooleanField(
        default=False, verbose_name=_("User is registered?")
    )
    request_status = models.CharField(
        max_length=10, choices=RequestStatuses.choices, default=RequestStatuses.PENDING
    )

    def __str__(self) -> str:
        return self.mobile + " - " + str(self.created_at)

    def is_expired(self) -> bool:
        return timezone.now() > self.expire_datetime

    def is_closed(self) -> bool:
        return self.request_status == self.RequestStatuses.COMPLETED

    def close_request(self) -> None:
        self.request_status = self.RequestStatuses.COMPLETED
        self.save()

    def send_otp_code(self) -> None:
        result: SMSServiceResult = SMSService.send_otp_code(self.mobile)
        self.otp_code = result.kwargs["otp_code"]
        self.save()

    def resend_otp_code(self) -> None:
        result: SMSServiceResult = SMSService.send_otp_code(self.mobile)
        self.otp_code = result.kwargs["otp_code"]
        self.expire_datetime = two_min_from_now()
        self.save()

    def get_user_or_none(self) -> User | None:
        user: User | None = User.objects.filter(username=self.mobile).last()
        return user

    def create_new_user(self) -> User:
        user: User = User.objects.create(
            username=self.mobile,
            first_name=self.first_name,
            last_name=self.last_name,
            national_code=self.national_code,
        )
        return user

    def disable_previous_codes(self) -> None:
        AuthRequest.objects.filter(mobile=self.mobile).update(
            request_status=AuthRequest.RequestStatuses.COMPLETED
        )
