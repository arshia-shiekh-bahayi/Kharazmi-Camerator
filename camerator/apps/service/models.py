from django.db import models
from django.utils.translation import gettext_lazy as _


class Service(models.Model):
    class ProcessingType(models.TextChoices):
        RETOUCH = "retouch", _("Retouch")
        FINISHED = "finished", _("Finished")

    class CameraType(models.TextChoices):
        PROFESSIONAL = "professional", _("Professional")
        SEMIPROFESSIONAL = "semi professional", _("Semi-Professional")
        NEWBIE = "newbie", _("Newbie")

    class ResolutionType(models.TextChoices):
        MP12 = "12MP", _("12MP")
        MP108 = "108MP", _("108MP")
        MP256 = "256MP", _("256MP")

    class ServiceChoices(models.TextChoices):
        PUBLISHED = "published", _("Published")
        DRAFT = "draft", _("Draft")

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, allow_unicode=True, blank=True)
    description = models.TextField()
    number_of_photos = models.IntegerField(default=10)
    thumbnail = models.ImageField(upload_to="services/images/", blank=False, null=False)
    processing = models.CharField(
        choices=ProcessingType.choices,
        default=ProcessingType.RETOUCH,
        verbose_name=_("Processing type"),
    )
    camera = models.CharField(
        choices=CameraType.choices,
        default=CameraType.SEMIPROFESSIONAL,
        verbose_name=_("Camera type"),
    )
    resolution = models.CharField(
        choices=ResolutionType.choices,
        default=ResolutionType.MP12,
        verbose_name=_("Resolution"),
    )
    term = models.IntegerField(default=7)
    price = models.IntegerField(default=10)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    status = models.CharField(
        choices=ServiceChoices.choices,
        default=ServiceChoices.PUBLISHED,
        verbose_name=_("Status"),
    )
